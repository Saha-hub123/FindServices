<?php

namespace App\Http\Controllers;

use App\Models\Report;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use Intervention\Image\Laravel\Facades\Image; // Pastikan package terinstall
// Import di bagian atas
use App\Models\User; 
use Illuminate\Support\Facades\Notification;
use App\Notifications\NewReportNotification;
use App\Notifications\ReportActionNotification;

class UserReportController extends Controller
{
    public function index()
    {
        $reports = Report::where('user_id', Auth::id())
            ->latest()
            ->paginate(10);

        return Inertia::render('Reports/Index', [
            'reports' => $reports
        ]);
    }

    public function store(Request $request)
    {
        $request->validate([
            'subject' => 'required|string|max:100',
            'description' => 'required|string|max:1000',
            'proof_images.*' => 'nullable|image|max:5120', // Max 5MB per file
        ]);

        $imagePaths = [];

        if ($request->hasFile('proof_images')) {
            foreach ($request->file('proof_images') as $file) {
                // 1. Generate Nama Unik
                $filename = 'reports/' . Str::random(40) . '.webp';

                // 2. Kompresi (Resize lebar 1000px, quality 80%)
                $image = Image::read($file)
                    ->scaleDown(width: 1000)
                    ->toWebp(quality: 80);

                // 3. Simpan ke Storage Public
                Storage::disk('public')->put($filename, (string) $image);
                
                $imagePaths[] = $filename;
            }
        }

        // Simpan ke database
        $report = Report::create([
            'user_id' => Auth::id(),
            'subject' => $request->subject,
            'description' => $request->description,
            'proof_images' => $imagePaths,
            'status' => 'pending'
        ]);

        // --- LOGIC NOTIFIKASI BARU ---
        // 1. Ambil semua user yang role-nya admin
        $admins = User::where('role', 'admin')->get();

        // 2. Kirim notifikasi ke mereka
        if ($admins->count() > 0) {
            Notification::send($admins, new NewReportNotification($report));
        }

        return back()->with('message', 'Laporan berhasil dikirim.');
    }

    public function update(Request $request, Report $report)
    {
        // Security: Pastikan punya sendiri & status pending
        if ($report->user_id !== Auth::id() || $report->status !== 'pending') {
            return back()->with('error', 'Laporan ini tidak bisa diedit lagi.');
        }

        $request->validate([
            'subject' => 'required|string|max:100',
            'description' => 'required|string|max:1000',
            'proof_images.*' => 'nullable|image|max:5120',
        ]);

        $data = [
            'subject' => $request->subject,
            'description' => $request->description,
        ];

        // Jika user upload gambar baru, gambar lama ditimpa (atau bisa dilogika append)
        // Di sini kita pakai logika REPLACE agar simpel
        if ($request->hasFile('proof_images')) {
            // Hapus gambar lama dulu (opsional, untuk hemat storage)
            if ($report->proof_images) {
                foreach($report->proof_images as $oldImg) {
                    Storage::disk('public')->delete($oldImg);
                }
            }

            $imagePaths = [];
            foreach ($request->file('proof_images') as $file) {
                $filename = 'reports/' . Str::random(40) . '.webp';
                $image = Image::read($file)->scaleDown(width: 1000)->toWebp(quality: 80);
                Storage::disk('public')->put($filename, (string) $image);
                $imagePaths[] = $filename;
            }
            $data['proof_images'] = $imagePaths;
        }

        $report->update($data);

        // NOTIFIKASI KE SEMUA ADMIN (Bahwa ada revisi)
        $admins = User::where('role', 'admin')->get();
        Notification::send($admins, new ReportActionNotification($report, 'updated'));

        return back()->with('message', 'Laporan berhasil diperbarui.');
    }

    public function destroy(Report $report)
    {
        if ($report->user_id !== Auth::id()) abort(403);
        
        // Hanya boleh hapus jika status pending
        if ($report->status !== 'pending') {
            return back()->with('error', 'Laporan yang sudah diproses tidak dapat dihapus.');
        }

        $report->delete(); // Soft Delete

        // Simpan data dulu sebelum dihapus untuk pesan notifikasi
        // Clone object agar data subject tidak hilang
        $tempReport = clone $report; 

        $report->delete();

        // NOTIFIKASI KE SEMUA ADMIN (Bahwa laporan dihapus)
        $admins = User::where('role', 'admin')->get();
        Notification::send($admins, new ReportActionNotification($tempReport, 'deleted'));

        return back()->with('message', 'Laporan berhasil dihapus.');
    }
}