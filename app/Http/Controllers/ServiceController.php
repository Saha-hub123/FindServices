<?php

namespace App\Http\Controllers;

use App\Models\Service;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB; 
use Illuminate\Support\Facades\Storage;

class ServiceController extends Controller
{
    public function show(Service $service)
    {
        // Load relasi:
        // 1. user: Pemilik jasa (untuk profil provider & tombol chat)
        // 2. category: Untuk badge kategori
        // 3. galleries: Untuk slider gambar
        // 4. reviews.user: Untuk list review beserta nama pengulasnya
        // 5. bookings: Kita hitung jumlahnya (completed only agar valid)
        
        $service->load([
            'user', 
            'category', 
            'galleries', 
            'reviews.user'
        ]);

        // Hitung statistik tambahan
        $service->bookings_count = $service->bookings()->where('status', 'completed')->count();

        return Inertia::render('Service/Show', [
            'service' => $service,
            'auth_user_id' => Auth::id() // Untuk menyembunyikan tombol chat jika lihat jasa sendiri
        ]);
    }

    
    public function create()
    {
        // Kita butuh kategori untuk dropdown
        $categories = \App\Models\Category::all();
        return Inertia::render('Service/Create', [
            'categories' => $categories
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'title' => 'required|string|max:255',
            'category_id' => 'required|exists:categories,id',
            'description' => 'required|string',
            'price_min' => 'required|numeric|min:0',
            'price_max' => 'required|numeric|gte:price_min', // Max tidak boleh lebih kecil dari Min
            'location' => 'required|string', // Alamat teks
            'latitude' => 'required|numeric',
            'longitude' => 'required|numeric',
            'images' => 'required|array|min:1', // Wajib minimal 1 foto
            'images.*' => 'image|mimes:jpeg,png,jpg|max:2048'
        ]);

        DB::transaction(function () use ($request, $validated) {
            // 1. Simpan Data Service
            $service = Auth::user()->services()->create([
                'title' => $validated['title'],
                'category_id' => $validated['category_id'],
                'description' => $validated['description'],
                'price_min' => $validated['price_min'],
                'price_max' => $validated['price_max'],
                'location' => $validated['location'],
                'latitude' => $validated['latitude'],
                'longitude' => $validated['longitude'],
                'status' => 'active', // Langsung aktif atau pending terserah Anda
            ]);

            // 2. Simpan Gambar ke Storage & Database
            if ($request->hasFile('images')) {
                foreach ($request->file('images') as $image) {
                    $path = $image->store('services', 'public');
                    $service->galleries()->create(['image' => $path]);
                }
            }
        });

        return redirect()->route('dashboard')->with('message', 'Jasa berhasil diterbitkan!');
    }

    public function edit(Service $service)
    {
        // Pastikan yang edit adalah pemiliknya
        if ($service->user_id !== Auth::id()) {
            abort(403);
        }

        // Load relasi galeri agar bisa ditampilkan/dihapus
        $service->load('galleries');
        
        $categories = \App\Models\Category::all();

        return Inertia::render('Service/Edit', [
            'service' => $service,
            'categories' => $categories
        ]);
    }

    // Method Update Data
    public function update(Request $request, Service $service)
    {
        if ($service->user_id !== Auth::id()) abort(403);

        $validated = $request->validate([
            'title' => 'required|string|max:255',
            'category_id' => 'required|exists:categories,id',
            'description' => 'required|string',
            'price_min' => 'required|numeric|min:0',
            'price_max' => 'required|numeric|gte:price_min',
            'location' => 'required|string',
            'latitude' => 'required|numeric',
            'longitude' => 'required|numeric',
            // Gambar baru opsional saat edit
            'new_images.*' => 'nullable|image|mimes:jpeg,png,jpg|max:2048',
            // Array ID gambar lama yang ingin dihapus
            'deleted_gallery_ids' => 'nullable|array' 
        ]);

        DB::transaction(function () use ($request, $service, $validated) {
            // 1. Update Data Text
            $service->update([
                'title' => $validated['title'],
                'category_id' => $validated['category_id'],
                'description' => $validated['description'],
                'price_min' => $validated['price_min'],
                'price_max' => $validated['price_max'],
                'location' => $validated['location'],
                'latitude' => $validated['latitude'],
                'longitude' => $validated['longitude'],
            ]);

            // 2. Hapus Gambar Lama yang dipilih user
            if ($request->filled('deleted_gallery_ids')) {
                $galleriesToDelete = \App\Models\Gallery::whereIn('id', $request->deleted_gallery_ids)
                                        ->where('service_id', $service->id)
                                        ->get();
                
                foreach ($galleriesToDelete as $gallery) {
                    // Hapus file fisik (Opsional, kalau mau hemat storage)
                    Storage::disk('public')->delete($gallery->image);
                    // Hapus record DB
                    $gallery->delete();
                }
            }

            // 3. Tambah Gambar Baru (Jika ada)
            if ($request->hasFile('new_images')) {
                foreach ($request->file('new_images') as $image) {
                    $path = $image->store('services', 'public');
                    $service->galleries()->create(['image' => $path]);
                }
            }
        });

        return redirect()->route('dashboard')->with('message', 'Jasa berhasil diperbarui!');
    }

    // Method Delete (Soft Delete)
    public function destroy(Service $service)
    {
        if ($service->user_id !== Auth::id()) abort(403);

        $service->delete(); // Ini otomatis Soft Delete karena trait tadi

        return redirect()->route('profile.index')->with('message', 'Jasa berhasil dihapus.');
    }

    // Menampilkan daftar jasa yang sudah dihapus
    public function trash()
    {
        $trashedServices = \App\Models\Service::onlyTrashed()
            ->where('user_id', Auth::id())
            ->get();

        return Inertia::render('Service/Trash', [
            'services' => $trashedServices
        ]);
    }

    // Mengembalikan jasa (Restore)
    public function restore($id)
    {
        // Kita harus pakai withTrashed() agar bisa menemukan ID yang sudah 'hilang'
        $service = \App\Models\Service::withTrashed()->findOrFail($id);

        // Keamanan: Pastikan milik user sendiri
        if ($service->user_id !== Auth::id()) {
            abort(403);
        }

        $service->restore();

        return redirect()->route('profile.index')->with('message', 'Jasa berhasil dikembalikan!');
    }

    // Hapus Permanen (Opsional)
    public function forceDelete($id)
    {
        $service = \App\Models\Service::withTrashed()->findOrFail($id);
        
        if ($service->user_id !== Auth::id()) abort(403);

        // Hapus gambar fisiknya dulu (cleanup storage)
        foreach ($service->galleries as $gallery) {
            Storage::disk('public')->delete($gallery->image);
        }
        
        $service->forceDelete(); // HILANG SELAMANYA

        return redirect()->back()->with('message', 'Jasa dihapus permanen.');
    }
}