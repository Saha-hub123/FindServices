<?php

namespace App\Http\Controllers;

use App\Models\Service;
use App\Models\Category;
use App\Models\User;
use Illuminate\Http\Request;
use Inertia\Inertia;

class DashboardController extends Controller
{
    public function index(Request $request)
    {
        // 1. FILTER LOGIC
        $filter = $request->input('filter', 'latest'); // Default 'latest'

        $servicesQuery = Service::with(['user', 'category', 'galleries'])
            ->withCount('reviews') // Hitung jumlah ulasan
            ->where('status', 'active');

        switch ($filter) {
            case 'popular':
                // Urutkan berdasarkan jumlah booking terbanyak (Asumsi relasi bookings ada)
                // Jika belum ada data booking, fallback ke rating review terbanyak
                $servicesQuery->withCount('bookings')->orderByDesc('bookings_count');
                break;
            case 'rating':
                // Urutkan berdasarkan rating tertinggi (kolom rating_avg di tabel services)
                $servicesQuery->orderByDesc('rating_avg');
                break;
            case 'latest':
            default:
                $servicesQuery->latest();
                break;
        }

        $services = $servicesQuery->paginate(10)->withQueryString(); // withQueryString agar pagination tidak mereset filter

        // 2. DATA PENDUKUNG
        $categories = Category::all();
        $trendingCategories = $categories->take(5); // Bisa diubah logicnya nanti
        
        // Jasa Populer (Sidebar Kanan)
        $popularServices = Service::with('galleries')
            ->where('status', 'active')
            ->orderByDesc('rating_avg') // Contoh: Jasa rating tinggi
            ->take(4)
            ->get();

        // 3. TOP PROVIDERS (Sidebar Kanan)
        // Ambil 3 User Random yang punya Jasa Aktif
        $topProviders = User::whereHas('services', function($q) {
                $q->where('status', 'active');
            })
            ->inRandomOrder()
            ->take(3)
            ->get();

        return Inertia::render('Dashboard', [
            'services' => $services,
            'categories' => $categories,
            'trendingCategories' => $trendingCategories,
            'popularServices' => $popularServices,
            'topProviders' => $topProviders,
            'filters' => $request->only(['filter']), // Kirim status filter ke frontend
            'is_guest' => !auth()->check()
        ]);
    }

    public function show($event)
    {
        return Inertia::render('Event/Show', [
            'event' => $event->only(
                'id',
                'title',
                'start_date',
                'description',
            ),
        ]);
    }
}