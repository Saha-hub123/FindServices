<?php

namespace Tests\Feature;

use App\Models\User;
use App\Models\Chat;
use App\Models\Service;
use App\Models\Booking;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Event;
use Vinkla\Hashids\Facades\Hashids;
use Tests\TestCase;

class ChatControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_halaman_index_chat_bisa_diakses()
    {
        $user = User::factory()->create();
        $response = $this->actingAs($user)->get(route('chats.index'));
        $response->assertStatus(200);
    }

    public function test_halaman_index_chat_dengan_target_user()
    {
        $me = User::factory()->create();
        $partner = User::factory()->create();

        // ChatController butuh 'user_id' yang di-HASH
        $hashId = Hashids::encode($partner->id);

        $response = $this->actingAs($me)->get(route('chats.index', ['user_id' => $hashId]));

        $response->assertStatus(200);
        
        // Pastikan activeChat dikirim ke frontend
        $response->assertInertia(fn ($page) => $page
            ->component('Chats/Index')
            ->where('activeChat.id', $partner->id)
        );
    }

    public function test_user_bisa_kirim_pesan()
    {
        Event::fake(); // Matikan event broadcasting

        $sender = User::factory()->create();
        $receiver = User::factory()->create();
        
        // Controller store() menerima 'receiver_id' dalam bentuk HASH
        $receiverHash = Hashids::encode($receiver->id);

        $response = $this->actingAs($sender)->post(route('chats.store'), [
            'receiver_id' => $receiverHash,
            'message' => 'Halo, apa kabar?',
        ]);

        $response->assertRedirect(); // Redirect back

        $this->assertDatabaseHas('chats', [
            'sender_id' => $sender->id,
            'receiver_id' => $receiver->id, // Database simpan ID asli (integer)
            'message' => 'Halo, apa kabar?'
        ]);
    }

    public function test_tandai_pesan_sudah_dibaca()
    {
        Event::fake();

        $me = User::factory()->create();
        $sender = User::factory()->create();

        // Buat pesan yang belum dibaca dari sender ke me
        Chat::factory()->create([
            'sender_id' => $sender->id,
            'receiver_id' => $me->id,
            'is_read' => false
        ]);

        $response = $this->actingAs($me)->post(route('chats.markAsRead'), [
            'sender_id' => $sender->id
        ]);

        $response->assertStatus(200);

        $this->assertDatabaseHas('chats', [
            'sender_id' => $sender->id,
            'receiver_id' => $me->id,
            'is_read' => true // Harus berubah jadi true
        ]);
    }

    public function test_hapus_pesan_sendiri()
    {
        Event::fake();

        $me = User::factory()->create();
        $chat = Chat::factory()->create(['sender_id' => $me->id]);

        $response = $this->actingAs($me)->delete(route('chats.destroy', $chat->id));

        $response->assertRedirect(); // Back

        // Cek Soft Delete
        $this->assertSoftDeleted('chats', [
            'id' => $chat->id
        ]);
    }

    public function test_tidak_bisa_hapus_pesan_orang_lain()
    {
        $me = User::factory()->create();
        $otherUser = User::factory()->create();
        $chat = Chat::factory()->create(['sender_id' => $otherUser->id]); // Pesan punya orang

        $response = $this->actingAs($me)->delete(route('chats.destroy', $chat->id));

        $response->assertStatus(403); // Forbidden
    }

    /**
     * TEST: Memastikan Logic Sorting & Counter Unread Berjalan Benar
     */
    public function test_halaman_index_memuat_daftar_percakapan_dengan_urutan_dan_counter_benar()
    {
        $me = User::factory()->create();
        $partnerBaru = User::factory()->create(['name' => 'Si Paling Baru']);
        $partnerLama = User::factory()->create(['name' => 'Si Masa Lalu']);
        $stranger = User::factory()->create(); // User yang tidak pernah chat

        // Skenario 1: Chat dengan Partner Lama (Terjadi Kemarin, Sudah Dibaca)
        // Saya -> Partner Lama
        Chat::factory()->create([
            'sender_id' => $me->id,
            'receiver_id' => $partnerLama->id,
            'message' => 'Halo masa lalu',
            'created_at' => now()->subDay(), // Kemarin
            'is_read' => true
        ]);

        // Skenario 2: Chat dengan Partner Baru (Terjadi 1 Jam Lalu, Belum Dibaca)
        // Partner Baru -> Saya (Pesan 1)
        Chat::factory()->create([
            'sender_id' => $partnerBaru->id,
            'receiver_id' => $me->id,
            'message' => 'Pesan pertama',
            'created_at' => now()->subHours(2),
            'is_read' => false
        ]);

        // Partner Baru -> Saya (Pesan 2 - Paling Baru)
        // Ini harus jadi 'last_message'
        Chat::factory()->create([
            'sender_id' => $partnerBaru->id,
            'receiver_id' => $me->id,
            'message' => 'Pesan paling baru nih',
            'created_at' => now()->subMinute(), // 1 Menit lalu
            'is_read' => false
        ]);

        // ACTION: Buka Halaman Chat Index
        $response = $this->actingAs($me)->get(route('chats.index'));

        // ASSERTION (Pengecekan Logic Controller)
        $response->assertStatus(200);

        $response->assertInertia(fn ($page) => $page
            ->component('Chats/Index')
            
            // 1. Pastikan total percakapan cuma 2 (Stranger tidak masuk)
            ->has('conversations', 2) 

            // 2. Cek Urutan PERTAMA (Harusnya Partner Baru karena chatnya paling fresh)
            ->where('conversations.0.id', $partnerBaru->id)
            ->where('conversations.0.last_message.message', 'Pesan paling baru nih') // Cek last message benar
            ->where('conversations.0.unread_count', 2) // Harusnya ada 2 pesan belum dibaca

            // 3. Cek Urutan KEDUA (Harusnya Partner Lama)
            ->where('conversations.1.id', $partnerLama->id)
            ->where('conversations.1.last_message.message', 'Halo masa lalu')
            ->where('conversations.1.unread_count', 0) // Karena sudah dibaca (is_read: true)
        );
    }

    /**
     * TEST 1: Cek Logika Sidebar (Sorting & Unread Count)
     * Menguji blok kode: $conversations = User::whereIn... ->map... ->sortByDesc...
     */
    public function test_sidebar_chat_mengurutkan_pesan_terbaru_dan_hitung_unread_benar()
    {
        $me = User::factory()->create();
        $partnerBaru = User::factory()->create(['name' => 'Partner Baru']);
        $partnerLama = User::factory()->create(['name' => 'Partner Lama']);

        // Chat Lama (Sudah dibaca)
        Chat::factory()->create([
            'sender_id' => $partnerLama->id,
            'receiver_id' => $me->id,
            'message' => 'Pesan lama',
            'created_at' => now()->subDay(),
            'is_read' => true
        ]);

        // Chat Baru (Belum dibaca, ada 2 pesan)
        Chat::factory()->count(2)->create([
            'sender_id' => $partnerBaru->id,
            'receiver_id' => $me->id,
            'message' => 'Pesan baru',
            'created_at' => now()->subMinute(),
            'is_read' => false
        ]);

        $response = $this->actingAs($me)->get(route('chats.index'));

        $response->assertStatus(200);

        // Cek Props Inertia
        $response->assertInertia(fn ($page) => $page
            ->component('Chats/Index')
            ->has('conversations', 2)
            // Urutan 0 harus Partner Baru (karena chat lebih baru)
            ->where('conversations.0.id', $partnerBaru->id)
            ->where('conversations.0.unread_count', 2)
            // Urutan 1 harus Partner Lama
            ->where('conversations.1.id', $partnerLama->id)
            ->where('conversations.1.unread_count', 0)
        );
    }

    /**
     * TEST 2: Cek Konteks dari URL (Prioritas 1)
     * Menguji blok kode: if ($request->booking_id) ... elseif ($request->service_id)
     */
    public function test_chat_memuat_konteks_booking_dan_service_via_url()
    {
        $me = User::factory()->create();
        $partner = User::factory()->create();
        $service = Service::factory()->create(['user_id' => $partner->id]);
        $booking = Booking::factory()->create(['customer_id' => $me->id, 'service_id' => $service->id]);

        $partnerHash = Hashids::encode($partner->id);
        $bookingHash = Hashids::encode($booking->id);

        // Case A: Ada Booking ID di URL
        $response = $this->actingAs($me)->get(route('chats.index', [
            'user_id' => $partnerHash,
            'booking_id' => $bookingHash
        ]));

        $response->assertInertia(fn ($page) => $page
            ->where('targetBooking.id', $booking->id)
            ->where('targetService.id', $service->id) // Service otomatis terload dari booking
        );

        // Case B: Hanya Service ID di URL
        $responseService = $this->actingAs($me)->get(route('chats.index', [
            'user_id' => $partnerHash,
            'service_id' => $service->id
        ]));

        $responseService->assertInertia(fn ($page) => $page
            ->where('targetBooking', null)
            ->where('targetService.id', $service->id)
        );
    }

    /**
     * TEST 3: Cek Konteks dari Pesan Terakhir (Prioritas 2 - Fallback)
     * Menguji blok kode: if (!$targetBooking && !$targetService) { $latestMessage = ... }
     */
    public function test_chat_memuat_konteks_otomatis_dari_pesan_terakhir()
    {
        $me = User::factory()->create();
        $partner = User::factory()->create();
        $booking = Booking::factory()->create(['customer_id' => $me->id]);

        // Buat history chat yang mengandung Booking ID
        Chat::factory()->create([
            'sender_id' => $partner->id,
            'receiver_id' => $me->id,
            'booking_id' => $booking->id, // <--- Kuncinya di sini
            'message' => 'Bahas booking ini dong',
            'created_at' => now()
        ]);

        $partnerHash = Hashids::encode($partner->id);

        // Panggil URL TANPA booking_id
        $response = $this->actingAs($me)->get(route('chats.index', [
            'user_id' => $partnerHash
        ]));

        // Harapannya: Controller pintar mencari booking dari pesan terakhir
        $response->assertInertia(fn ($page) => $page
            ->where('targetBooking.id', $booking->id)
        );
    }

    /**
     * TEST 4: Validasi User Tidak Ditemukan
     * Menguji blok kode: if (!$partnerId) abort(404)
     */
    public function test_chat_error_404_jika_hash_id_user_salah()
    {
        $me = User::factory()->create();
        
        $response = $this->actingAs($me)->get(route('chats.index', [
            'user_id' => 'hash-ngawur-xyz'
        ]));

        $response->assertNotFound();
    }

    /**
     * TEST 5: Mark as Read & Broadcast Event
     * Menguji blok kode: update(['is_read' => true]) dan broadcast(...)
     */
    public function test_chat_otomatis_tandai_dibaca_dan_kirim_event()
    {
        Event::fake(); // Mocking Event

        $me = User::factory()->create();
        $partner = User::factory()->create();
        $partnerHash = Hashids::encode($partner->id);

        // Pesan belum dibaca (Sender: Partner, Receiver: Me)
        Chat::factory()->create([
            'sender_id' => $partner->id,
            'receiver_id' => $me->id,
            'is_read' => false
        ]);

        // Buka Chat (Saya membaca pesan dari Partner)
        $this->actingAs($me)->get(route('chats.index', ['user_id' => $partnerHash]));

        // 1. Cek DB berubah jadi read
        $this->assertDatabaseHas('chats', [
            'sender_id' => $partner->id,
            'receiver_id' => $me->id,
            'is_read' => true
        ]);

        // 2. Cek Event terkirim dengan Properti yang BENAR
        Event::assertDispatched(\App\Events\MessageRead::class, function ($event) use ($me, $partner) {
            // reader_id = yang login (saya)
            // sender_id = pengirim pesan asli (partner)
            return $event->reader_id === $me->id && $event->sender_id === $partner->id;
        });
    }
}