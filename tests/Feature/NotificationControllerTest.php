<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Notification;
use App\Notifications\NewReportNotification; // Contoh notifikasi
use Tests\TestCase;

class NotificationControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_halaman_notifikasi_bisa_diakses()
    {
        $user = User::factory()->create();
        $response = $this->actingAs($user)->get(route('notifications.index'));
        $response->assertStatus(200);
    }

    public function test_tandai_satu_notifikasi_sudah_dibaca()
    {
        $user = User::factory()->create();
        
        // Buat notifikasi dummy secara manual di database
        // Cara termudah: Kirim notifikasi beneran ke user
        // Tapi kita perlu kelas Notifikasi yang nyata. 
        // Kita pakai DatabaseNotification factory manual saja biar cepat.
        
        $notification = $user->notifications()->create([
            'id' => \Illuminate\Support\Str::uuid()->toString(),
            'type' => 'App\Notifications\DummyNotification',
            'data' => ['message' => 'Halo'],
            'read_at' => null
        ]);

        $response = $this->actingAs($user)
            ->post(route('notifications.read', $notification->id));

        $response->assertRedirect(); // Back

        // Cek DB: read_at harus terisi
        $this->assertNotNull($notification->fresh()->read_at);
    }

    public function test_tandai_semua_sudah_dibaca()
    {
        $user = User::factory()->create();
        
        // Buat 2 notifikasi
        $user->notifications()->create([
            'id' => \Illuminate\Support\Str::uuid()->toString(),
            'type' => 'App\Notifications\Dummy1', 'data' => [], 'read_at' => null
        ]);
        $user->notifications()->create([
            'id' => \Illuminate\Support\Str::uuid()->toString(),
            'type' => 'App\Notifications\Dummy2', 'data' => [], 'read_at' => null
        ]);

        $response = $this->actingAs($user)->post(route('notifications.readAll'));

        $response->assertRedirect();
        
        // Semua harus sudah dibaca (tidak ada yang unread)
        $this->assertEquals(0, $user->unreadNotifications()->count());
    }

    public function test_hapus_notifikasi()
    {
        $user = User::factory()->create();
        $notification = $user->notifications()->create([
            'id' => \Illuminate\Support\Str::uuid()->toString(),
            'type' => 'App\Notifications\Dummy', 'data' => [], 'read_at' => null
        ]);

        $response = $this->actingAs($user)->delete(route('notifications.destroy', $notification->id));

        $response->assertRedirect();

        // Data harus hilang dari tabel notifications
        $this->assertDatabaseMissing('notifications', [
            'id' => $notification->id
        ]);
    }
}