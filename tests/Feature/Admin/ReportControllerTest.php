<?php

namespace Tests\Feature\Admin;

use App\Models\User;
use App\Models\Report;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Notification;
use App\Notifications\ReportStatusUpdated;
use Tests\TestCase;

class ReportControllerTest extends TestCase
{
    use RefreshDatabase;

    private function createAdmin()
    {
        return User::factory()->create(['role' => 'admin']);
    }

    public function test_admin_bisa_lihat_daftar_laporan()
    {
        $admin = $this->createAdmin();
        Report::factory()->count(3)->create();

        $response = $this->actingAs($admin)->get(route('admin.reports.index'));

        $response->assertStatus(200)
                 ->assertInertia(fn ($page) => $page
                    ->component('Admin/Reports/Index')
                    ->has('reports.data', 3)
                 );
    }

    public function test_admin_filter_laporan_sampah()
    {
        $admin = $this->createAdmin();
        
        // 1 Laporan Aktif, 1 Laporan Terhapus
        Report::factory()->create(); 
        Report::factory()->create(['deleted_at' => now()]);

        // Filter status=trash
        $response = $this->actingAs($admin)->get(route('admin.reports.index', ['status' => 'trash']));

        $response->assertInertia(fn ($page) => $page
            ->has('reports.data', 1) // Harusnya cuma muncul 1 yang trash
        );
    }

    public function test_admin_bisa_update_status_laporan_dan_kirim_notif()
    {
        Notification::fake(); // Mock Notification

        $admin = $this->createAdmin();
        $userPelapor = User::factory()->create();
        $report = Report::factory()->create([
            'user_id' => $userPelapor->id,
            'status' => 'pending'
        ]);

        // Update jadi resolved
        // Gunakan PATCH sesuai route resource atau manual Anda (di web.php Anda pakai patch)
        $response = $this->actingAs($admin)
                         ->patch(route('admin.reports.update', $report->id), [
                             'status' => 'resolved'
                         ]);

        $response->assertRedirect();

        // Cek DB berubah
        $this->assertDatabaseHas('reports', [
            'id' => $report->id,
            'status' => 'resolved'
        ]);

        // Cek Notifikasi terkirim ke User Pelapor
        Notification::assertSentTo($userPelapor, ReportStatusUpdated::class);
    }

    public function test_admin_bisa_restore_laporan()
    {
        $admin = $this->createAdmin();
        $report = Report::factory()->create(['deleted_at' => now()]);

        $response = $this->actingAs($admin)->post(route('admin.reports.restore', $report->id));

        $response->assertRedirect();
        $this->assertNotSoftDeleted('reports', ['id' => $report->id]);
    }
}