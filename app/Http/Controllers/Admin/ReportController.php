<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Report;
use Illuminate\Http\Request;
use Inertia\Inertia;
// Import di atas
use App\Notifications\ReportStatusUpdated;

class ReportController extends Controller
{
    public function index(Request $request)
    {
        $query = Report::with('user'); // Load data pelapor

        // Filter Logic
        if ($request->status === 'trash') {
            // HANYA ambil yang sudah dihapus
            $query->onlyTrashed();
        } elseif ($request->status && $request->status !== 'all') {
            // Ambil status biasa (Pending/Resolved/Rejected)
            // Laravel otomatis mengecualikan yang deleted (tanpa withTrashed)
            $query->where('status', $request->status);
        }
        // Jika 'all', biarkan default (hanya yang aktif)

        $reports = $query->latest()->paginate(10)->withQueryString();

        return Inertia::render('Admin/Reports/Index', [
            'reports' => $reports,
            'filters' => $request->only(['status'])
        ]);
    }

    public function updateStatus(Request $request, Report $report)
    {
        $request->validate([
            'status' => 'required|in:pending,resolved,rejected'
        ]);

        $report->update(['status' => $request->status]);

        // KIRIM NOTIFIKASI KE USER (PELAPOR)
        // Pastikan user-nya masih ada (belum dihapus akunnya)
        if ($report->user) {
            $report->user->notify(new ReportStatusUpdated($report));
        }

        return back()->with('message', 'Status laporan diperbarui.');
    }

    // Fungsi Mengembalikan Data
    public function restore($id)
    {
        // Cari data di tong sampah
        $report = Report::onlyTrashed()->findOrFail($id);
        
        // Kembalikan
        $report->restore();

        return back()->with('message', 'Laporan berhasil dipulihkan.');
    }
}