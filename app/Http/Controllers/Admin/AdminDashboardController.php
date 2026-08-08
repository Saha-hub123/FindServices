<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Models\User;
use App\Models\Booking; // Pastikan model Booking ada
use App\Models\Report;
use App\Models\Category;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class AdminDashboardController extends Controller
{
    public function index()
    {
        // 1. STATISTIK KARTU (Total Counter)
        $totalUsers = User::count();
        $totalBookings = Booking::count(); 
        $activeServices = \App\Models\Service::where('status', 'active')->count();
        $pendingReports = Report::where('status', 'pending')->count();

        // 2. CHART DATA: TREN PESANAN (6 Bulan Terakhir)
        // Mengelompokkan booking berdasarkan bulan
        $bookingsData = Booking::select(
            DB::raw('COUNT(id) as count'), 
            DB::raw('MONTHNAME(created_at) as month_name'),
            DB::raw('MONTH(created_at) as month_num')
        )
        ->where('created_at', '>=', Carbon::now()->subMonths(6))
        ->groupBy('month_name', 'month_num')
        ->orderBy('month_num')
        ->get();

        // Format untuk Chart.js (Array Label & Array Data)
        $chartBookingLabels = $bookingsData->pluck('month_name');
        $chartBookingValues = $bookingsData->pluck('count');

        // 3. CHART DATA: DISTRIBUSI KATEGORI (Top 5 Kategori dengan jasa terbanyak)
        $categoriesData = Category::withCount('services')
            ->orderByDesc('services_count')
            ->take(5)
            ->get();
        
        $chartCategoryLabels = $categoriesData->pluck('name');
        $chartCategoryValues = $categoriesData->pluck('services_count');

        // 4. CHART DATA: STATUS LAPORAN
        $reportStats = Report::select('status', DB::raw('count(*) as total'))
            ->groupBy('status')
            ->pluck('total', 'status')->all();
        
        // Pastikan urutan array tetap (Pending, Resolved, Rejected)
        $chartReportValues = [
            $reportStats['pending'] ?? 0,
            $reportStats['resolved'] ?? 0,
            $reportStats['rejected'] ?? 0,
        ];

        return Inertia::render('Admin/Dashboard', [
            'stats' => [
                'users' => $totalUsers,
                'bookings' => $totalBookings,
                'services' => $activeServices,
                'reports' => $pendingReports
            ],
            'charts' => [
                'bookings' => [
                    'labels' => $chartBookingLabels,
                    'data' => $chartBookingValues,
                ],
                'categories' => [
                    'labels' => $chartCategoryLabels,
                    'data' => $chartCategoryValues,
                ],
                'reports' => [
                    'data' => $chartReportValues
                ]
            ]
        ]);
    }
}