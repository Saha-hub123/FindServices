<?php

namespace Tests\Feature;

use App\Models\User;
use App\Models\Report;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Notification;
use Illuminate\Http\UploadedFile;
use Tests\TestCase;

class UserReportControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_halaman_laporan_bisa_diakses()
    {
        $user = User::factory()->create();
        $response = $this->actingAs($user)->get(route('user.reports.index'));
        $response->assertStatus(200);
    }

    public function test_user_bisa_buat_laporan_baru()
    {
        Storage::fake('public'); // Mock Storage
        Notification::fake();    // Mock Notification

        $user = User::factory()->create();
        // Buat admin untuk menerima notifikasi
        $admin = User::factory()->create(['role' => 'admin']);

        $response = $this->actingAs($user)->post(route('user.reports.store'), [
            'subject' => 'Laporan Penipuan',
            'description' => 'User X melakukan penipuan.',
            'proof_images' => [
                UploadedFile::fake()->image('bukti1.jpg')
            ]
        ]);

        $response->assertRedirect();

        $this->assertDatabaseHas('reports', [
            'user_id' => $user->id,
            'subject' => 'Laporan Penipuan',
            'status' => 'pending'
        ]);

        // Pastikan Admin menerima notifikasi
        Notification::assertSentTo($admin, \App\Notifications\NewReportNotification::class);
    }

    public function test_user_bisa_update_laporan_pending_termasuk_foto()
    {
        Storage::fake('public'); // Mock Storage
        Notification::fake();    // Mock Notification

        $user = User::factory()->create();
        $admin = User::factory()->create(['role' => 'admin']);

        // 1. Persiapan Data Awal: Laporan dengan gambar lama
        $oldImageName = 'reports/old_evidence.jpg';
        
        // Simpan file fisik pura-pura di storage
        Storage::disk('public')->put($oldImageName, 'konten lama');

        $report = Report::factory()->create([
            'user_id' => $user->id,
            'status' => 'pending', 
            'subject' => 'Judul Lama',
            'proof_images' => [$oldImageName] // Simpan path di DB (asumsi casting array/json di Model Report)
        ]);

        // 2. Persiapan Gambar Baru
        $newFile = UploadedFile::fake()->image('bukti_baru.jpg');

        // 3. Action: Update laporan dengan gambar baru
        // Gunakan POST (method spoofing Laravel otomatis handle jika form inertia, tapi disini kita POST langsung ke route)
        $response = $this->actingAs($user)->post(route('user.reports.update', $report->id), [
            'subject' => 'Judul Baru Revisi',
            'description' => 'Deskripsi baru lengkap dengan bukti baru.',
            'proof_images' => [$newFile] // Kirim array file baru
        ]);

        $response->assertRedirect();

        // 4. Assertions (Pengecekan)

        // A. Cek Data Text di DB Berubah
        $this->assertDatabaseHas('reports', [
            'id' => $report->id,
            'subject' => 'Judul Baru Revisi',
            'description' => 'Deskripsi baru lengkap dengan bukti baru.'
        ]);

        // B. Cek Logika Storage (PENTING)
        
        // Gambar LAMA harus hilang dari disk
        Storage::disk('public')->assertMissing($oldImageName);

        // Ambil data terbaru dari DB untuk tahu nama file baru (karena random string)
        $updatedReport = $report->fresh();
        $newImages = $updatedReport->proof_images;

        // Pastikan array gambar tidak kosong dan berbeda dari yang lama
        $this->assertIsArray($newImages);
        $this->assertCount(1, $newImages);
        $this->assertNotEquals($oldImageName, $newImages[0]);

        // Gambar BARU harus ada di disk
        Storage::disk('public')->assertExists($newImages[0]);

        // C. Cek Notifikasi ke Admin (Bahwa ada update)
        Notification::assertSentTo($admin, \App\Notifications\ReportActionNotification::class);
    }

    public function test_user_bisa_hapus_laporan_pending()
    {
        Notification::fake();
        $user = User::factory()->create();
        $report = Report::factory()->create([
            'user_id' => $user->id,
            'status' => 'pending'
        ]);

        $response = $this->actingAs($user)->delete(route('user.reports.destroy', $report->id));

        $response->assertRedirect();

        $this->assertSoftDeleted('reports', ['id' => $report->id]);
    }

    public function test_user_tidak_bisa_edit_laporan_yang_sudah_diproses()
    {
        $user = User::factory()->create();
        $report = Report::factory()->create([
            'user_id' => $user->id,
            'status' => 'resolved' // Status sudah selesai
        ]);

        $response = $this->actingAs($user)->post(route('user.reports.update', $report->id), [
            'subject' => 'Coba Edit'
        ]);

        // Harus gagal (Redirect back with error)
        // Data di DB tidak boleh berubah
        $this->assertDatabaseHas('reports', [
            'id' => $report->id,
            'status' => 'resolved'
        ]);
    }
}