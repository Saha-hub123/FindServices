<?php

namespace Tests\Feature\Admin;

use App\Models\User;
use App\Models\Booking;
use App\Models\Service;
use App\Models\Report;
use App\Models\Category;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;
use Carbon\Carbon;

class AdminDashboardControllerTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Setup khusus untuk mengajarkan SQLite fungsi MySQL
     */
    protected function setUp(): void
    {
        parent::setUp();

        // Cek apakah driver yang dipakai adalah SQLite
        if (DB::connection()->getDriverName() === 'sqlite') {
            $pdo = DB::connection()->getPdo();

            // 1. Daftarkan fungsi MONTH()
            // MySQL: Mengembalikan angka bulan (1-12)
            // PHP: date('n', ...)
            $pdo->sqliteCreateFunction('MONTH', function ($date) {
                if (!$date) return null;
                return (int) date('n', strtotime($date));
            }, 1);

            // 2. Daftarkan fungsi MONTHNAME()
            // MySQL: Mengembalikan nama bulan (January, February)
            // PHP: date('F', ...)
            $pdo->sqliteCreateFunction('MONTHNAME', function ($date) {
                if (!$date) return null;
                return date('F', strtotime($date));
            }, 1);
        }
    }

    public function test_dashboard_admin_statistik_dan_chart_berhasil_dimuat()
    {
        // 1. Siapkan User Admin
        $admin = User::factory()->create(['role' => 'admin']);

        // 2. Siapkan Data Dummy (Biarkan factory bekerja natural)
        // Kita tidak perlu User::factory()->count(4) lagi karena factory di bawah
        // otomatis akan membuat user-user baru sebagai relasi.
        
        // Buat Kategori
        $cat1 = Category::factory()->create(['name' => 'Tech']);
        $cat2 = Category::factory()->create(['name' => 'Art']);

        // Buat Service (1 Active, 1 Inactive)
        // Ini otomatis membuat User pemilik jasa juga
        $serviceActive = Service::factory()->create(['status' => 'active', 'category_id' => $cat1->id]);
        Service::factory()->create(['status' => 'inactive', 'category_id' => $cat2->id]);

        // Buat Report (1 Pending, 1 Resolved)
        // Ini otomatis membuat User pelapor juga
        Report::factory()->create(['status' => 'pending']);
        Report::factory()->create(['status' => 'resolved']);

        // 3. Siapkan Data Dummy untuk Booking
        // Ini otomatis membuat User Customer & Provider juga
        Booking::factory()->create(['created_at' => Carbon::now()]);
        Booking::factory()->create(['created_at' => Carbon::now()]);
        Booking::factory()->create(['created_at' => Carbon::now()->subMonth()]);

        // --- HITUNG DATA REAL SEKARANG ---
        // Alih-alih menebak angka 5, kita tanya database berapa totalnya sekarang
        $expectedTotalUsers = User::count(); 
        $expectedTotalBookings = Booking::count();
        $expectedActiveServices = Service::where('status', 'active')->count();
        $expectedPendingReports = Report::where('status', 'pending')->count();

        // 4. Akses Dashboard
        $response = $this->actingAs($admin)->get(route('admin.dashboard'));

        // 5. Assertions (Pengecekan)
        $response->assertStatus(200);

        $response->assertInertia(fn ($page) => $page
            ->component('Admin/Dashboard')
            
            // A. Cek Statistik Kartu (Gunakan variabel dinamis)
            ->where('stats.users', $expectedTotalUsers)          
            ->where('stats.bookings', $expectedTotalBookings)       
            ->where('stats.services', $expectedActiveServices)       
            ->where('stats.reports', $expectedPendingReports)        
            
            // B. Cek Kelengkapan Chart
            ->has('charts.bookings.labels')
            ->has('charts.bookings.data')
            ->has('charts.categories.labels')
            ->has('charts.categories.data')
            ->has('charts.reports.data')
        );
    }
}