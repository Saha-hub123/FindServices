<?php

namespace App\Http\Controllers;

use App\Models\Service;
use App\Models\Category;
use Illuminate\Http\Request;
use Inertia\Inertia;
// Pastikan import ini ada di atas
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Support\Facades\DB; // Perlu untuk selectRaw

class MarketplaceController extends Controller
{
    public function index(Request $request)
    {
        // 1. Inisialisasi Query
        $query = Service::query()
            ->with(['user', 'category', 'galleries'])
            ->withAvg('reviews', 'rating');

        // A. Filter Pencarian
        if ($request->search) {
            $query->where(function($q) use ($request) {
                $q->where('title', 'like', '%' . $request->search . '%')
                ->orWhere('description', 'like', '%' . $request->search . '%');
            });
        }

        // B. Filter Kategori
        if ($request->category) {
            $query->whereHas('category', function($q) use ($request) {
                $q->where('slug', $request->category);
            });
        }

        // C. Filter Harga & Rating
        if ($request->price_min) {
            $query->where('price_min', '>=', $request->price_min);
        }
        if ($request->price_max) {
            $query->where('price_min', '<=', $request->price_max);
        }
        // [FIX] Filter Rating (Gunakan WhereRaw agar aman saat Pagination + Radius)
        if ($request->rating_avg) {
            // Kita gunakan subquery langsung di WHERE, bukan HAVING
            // Asumsi nama tabel review adalah 'reviews' dan foreign key 'service_id'
            $query->whereRaw('(SELECT AVG(rating) FROM reviews WHERE reviews.service_id = services.id) >= ?', [$request->rating_avg]);
        }

        // D. Filter Lokasi (Radius) & Sorting
        if ($request->latitude && $request->longitude) {
            $latitude = $request->latitude;
            $longitude = $request->longitude;
            $radius = $request->radius ?? 10;

            // Rumus Haversine
            $query->select('*')
                ->selectRaw(
                    "(6371 * acos(cos(radians(?)) * cos(radians(latitude)) * cos(radians(longitude) - radians(?)) + sin(radians(?)) * sin(radians(latitude)))) AS distance", 
                    [$latitude, $longitude, $latitude]
                )
                ->having('distance', '<=', $radius)
                ->orderBy('distance', 'asc'); // Urutkan dari yang Terdekat
        } else {
            // Jika tidak cari lokasi, urutkan dari yang Terbaru
            $query->latest(); 
        }

        // Eksekusi Query
        $services = $query->where('status', 'active') // Pastikan status active
                        ->withCount('reviews')
                        ->paginate(12)
                        ->withQueryString();

        // [TAMBAHAN BARU]
        // Jika request dari Axios (Load More), kirim JSON raw datanya
        if ($request->wantsJson()) {
            return response()->json($services);
        }
        // ----------------

        $categories = Category::all();

        return Inertia::render('Marketplace/Index', [
            'services' => $services,
            'categories' => $categories,
            
            // PENTING: Tambahkan variabel lokasi ke sini agar input frontend tidak reset
            'filters' => $request->only([
                'search', 
                'category', 
                'price_min', 
                'price_max', 
                'rating_avg',
                'latitude',      // <--- Tambahan
                'longitude',     // <--- Tambahan
                'radius',        // <--- Tambahan
                'location_name'  // <--- Tambahan (agar teks input tidak hilang)
            ])
        ]);
    }
}