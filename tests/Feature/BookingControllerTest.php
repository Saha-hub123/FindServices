<?php

namespace Tests\Feature;

use App\Models\Booking;
use App\Models\User;
use App\Models\Service;
use App\Models\Category;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Notification;
use Tests\TestCase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Config;
use Vinkla\Hashids\Facades\Hashids;
use Mockery; // Untuk mocking Midtrans Snap

class BookingControllerTest extends TestCase
{
    use RefreshDatabase; 

    // 1. TEST HALAMAN INDEX 
    public function test_halaman_index_booking_bisa_diakses()
    {
        $user = User::factory()->create();
        $response = $this->actingAs($user)->get(route('bookings.index'));
        $response->assertStatus(200);
    }

    // 2. TEST HALAMAN CREATE
    public function test_halaman_create_booking_bisa_diakses()
    {
        $user = User::factory()->create();
        $category = Category::factory()->create(); 
        $provider = User::factory()->create();
        $service = Service::factory()->create([
            'user_id' => $provider->id,
            'category_id' => $category->id
        ]);

        $response = $this->actingAs($user)->get(route('bookings.create', [
            'service_id' => $service->id
        ]));

        $response->assertStatus(200);
    }

    // 3. TEST STORE (Simpan Booking Baru - Manual)
    public function test_customer_bisa_membuat_booking_manual()
    {
        Notification::fake();
        Event::fake();

        $customer = User::factory()->create();
        $provider = User::factory()->create();
        $category = Category::factory()->create();
        $service = Service::factory()->create([
            'user_id' => $provider->id,
            'category_id' => $category->id,
            'price_min' => 50000
        ]);

        $bookingData = [
            'service_id' => $service->id,
            'booking_date' => now()->addDays(2)->format('Y-m-d'),
            'booking_time' => '09:00',
            'location' => 'Rumah Saya',
            'latitude' => -6.200,
            'longitude' => 106.816,
            'notes' => 'Mohon tepat waktu',
            'payment_method' => 'manual',
        ];

        $response = $this->actingAs($customer)->post(route('bookings.store'), $bookingData);

        $response->assertRedirect(route('bookings.index'));
        
        $this->assertDatabaseHas('bookings', [
            'customer_id' => $customer->id,
            'service_id' => $service->id,
            'status' => 'pending',
        ]);
    }

    // 4. TEST PROVIDER KONFIRMASI PESANAN (Update Status)
    public function test_provider_bisa_konfirmasi_booking_dan_set_harga()
    {
        Notification::fake();
        Event::fake();

        $provider = User::factory()->create();
        $service = Service::factory()->create(['user_id' => $provider->id]);
        
        $booking = Booking::factory()->create([
            'provider_id' => $provider->id,
            'service_id' => $service->id,
            'status' => 'pending',
            'initial_price' => 50000,
            'final_price' => null, // <--- TAMBAHKAN INI (Kunci agar harga bisa diedit)
            'payment_method' => 'manual'
        ]);

        // PERBAIKAN: Gunakan $booking object, bukan $booking->id
        $response = $this->actingAs($provider)
            ->patch(route('bookings.update-status', $booking), [
                'status' => 'confirmed',
                'agreed_price' => 60000 
            ]);

        $response->assertRedirect(); 

        $this->assertDatabaseHas('bookings', [
            'id' => $booking->id,
            'status' => 'confirmed',
            'initial_price' => 60000, 
            'final_price' => 60000 
        ]);
    }

    // 5. TEST CUSTOMER EDIT PESANAN
    public function test_customer_bisa_edit_pesanan()
    {
        Notification::fake();
        Event::fake();

        $customer = User::factory()->create();
        
        $booking = Booking::factory()->create([
            'customer_id' => $customer->id,
            'status' => 'pending', 
            'payment_method' => 'manual'
        ]);

        $newData = [
            'booking_date' => now()->addDays(5)->format('Y-m-d'),
            'booking_time' => '14:00',
            'location' => 'Lokasi Baru',
            'latitude' => -6.500,
            'longitude' => 107.500,
            'payment_method' => 'manual',
            'revised_price' => 100000, 
            'notes' => 'Edit catatan',
        ];

        // PERBAIKAN: Gunakan $booking object, bukan $booking->id
        $response = $this->actingAs($customer)
            ->put(route('bookings.update', $booking), $newData);

        $response->assertRedirect();

        $this->assertDatabaseHas('bookings', [
            'id' => $booking->id,
            'location' => 'Lokasi Baru',
            'status' => 'pending' 
        ]);
    }

    // 6. TEST SHOW BOOKING
    public function test_halaman_detail_booking_bisa_diakses()
    {
        $customer = User::factory()->create();
        $provider = User::factory()->create();
        
        $booking = Booking::factory()->create([
            'customer_id' => $customer->id,
            'provider_id' => $provider->id
        ]);

        // PERBAIKAN: Gunakan $booking object, bukan $booking->id
        $response = $this->actingAs($customer)->get(route('bookings.show', $booking));

        $response->assertStatus(200);
    }
    
    /**
     * TEST: Beri Review Lengkap (Rating, Komen, Foto, Notif, Event)
     */
    public function test_customer_bisa_beri_review_lengkap_dengan_foto()
    {
        // 1. Mocking External Services
        Storage::fake('public'); // Mock Storage agar tidak simpan file asli
        Notification::fake();    // Mock Notifikasi
        Event::fake();           // Mock Event Broadcasting

        // 2. Setup Data
        $customer = User::factory()->create();
        $provider = User::factory()->create();
        $service = Service::factory()->create(['user_id' => $provider->id]);

        $booking = Booking::factory()->create([
            'customer_id' => $customer->id,
            'provider_id' => $provider->id,
            'service_id' => $service->id,
            'status' => 'completed' // Asumsi hanya yang completed bisa direview
        ]);

        // 3. Siapkan Dummy Images
        // Kita buat 2 file gambar palsu
        $file1 = UploadedFile::fake()->image('bukti1.jpg');
        $file2 = UploadedFile::fake()->image('bukti2.png');

        // 4. Action: Post ke route storeReview
        // Route: POST /bookings/{booking}/review
        $response = $this->actingAs($customer)
            ->post(route('bookings.review', $booking), [
                'rating' => 5,
                'comment' => 'Pelayanan sangat memuaskan, mantap!',
                'images' => [$file1, $file2] // Kirim array gambar
            ]);

        // 5. Assertions (Pengecekan)

        // A. Cek Redirect & Session
        $response->assertRedirect();
        $response->assertSessionHas('message', 'Terima kasih atas ulasan Anda!');

        // B. Cek Database (Tabel Reviews)
        $this->assertDatabaseHas('reviews', [
            'booking_id' => $booking->id,
            'service_id' => $service->id,
            'user_id' => $customer->id,
            'rating' => 5,
            'review' => 'Pelayanan sangat memuaskan, mantap!',
        ]);

        // C. Cek Upload Gambar (Storage & DB Array)
        // Ambil review yang baru dibuat
        $review = \App\Models\Review::where('booking_id', $booking->id)->first();
        
        // Pastikan kolom images terisi 2 item
        $this->assertCount(2, $review->images);

        // Pastikan file fisik ada di storage (nama file random, jadi kita cek berdasarkan DB)
        foreach ($review->images as $imagePath) {
            Storage::disk('public')->assertExists($imagePath);
        }

        // D. Cek Notifikasi Terkirim ke Provider
        Notification::assertSentTo(
            $provider, 
            \App\Notifications\NewReviewNotification::class
        );

        // E. Cek Event Broadcast
        Event::assertDispatched(\App\Events\ReviewSubmitted::class);
    }

    /**
     * TEST: Validasi Review (Max 3 Foto)
     */
    public function test_validasi_upload_review_gagal_jika_foto_lebih_dari_3()
    {
        Storage::fake('public');
        $customer = User::factory()->create();
        $booking = Booking::factory()->create(['customer_id' => $customer->id]);

        // Siapkan 4 Foto (Melanggar aturan max:3)
        $images = [
            UploadedFile::fake()->image('1.jpg'),
            UploadedFile::fake()->image('2.jpg'),
            UploadedFile::fake()->image('3.jpg'),
            UploadedFile::fake()->image('4.jpg'),
        ];

        $response = $this->actingAs($customer)
            ->post(route('bookings.review', $booking), [
                'rating' => 5,
                'comment' => 'Test',
                'images' => $images
            ]);

        // Harusnya error validasi pada field 'images'
        $response->assertSessionHasErrors(['images']);
    }

    public function test_customer_bisa_akses_halaman_edit_booking()
    {
        $customer = User::factory()->create();
        $provider = User::factory()->create();
        $service = Service::factory()->create(['user_id' => $provider->id]);
        
        // Booking status pending (Boleh diedit)
        $booking = Booking::factory()->create([
            'customer_id' => $customer->id,
            'service_id' => $service->id,
            'status' => 'pending',
        ]);

        // Buat booking lain di tanggal yang sama (untuk simulasi bookedDates)
        Booking::factory()->create([
            'provider_id' => $provider->id,
            'booking_date' => $booking->booking_date,
            'status' => 'confirmed'
        ]);

        $response = $this->actingAs($customer)->get(route('bookings.edit', $booking));

        $response->assertStatus(200);
        
        $response->assertInertia(fn ($page) => $page
            ->component('Bookings/Edit')
            ->has('booking')
            ->has('bookedDates') // Pastikan jadwal provider terkirim
            ->has('adminFee')
        );
    }

    public function test_customer_tidak_bisa_edit_booking_yang_sudah_completed()
    {
        $customer = User::factory()->create();
        $booking = Booking::factory()->create([
            'customer_id' => $customer->id,
            'status' => 'completed', // Status terlarang edit
        ]);

        $response = $this->actingAs($customer)->get(route('bookings.edit', $booking));

        // Harusnya redirect ke show dengan pesan error
        $response->assertRedirect(route('bookings.show', $booking));
        $response->assertSessionHas('error');
    }


    public function test_customer_bisa_hapus_review_sendiri()
    {
        Storage::fake('public'); // Mock Storage
        
        $customer = User::factory()->create();
        
        // Buat review dengan gambar
        $review = \App\Models\Review::factory()->create([
            'user_id' => $customer->id,
            'images' => ['reviews/foto1.jpg']
        ]);

        // Buat file dummy di storage biar bisa dites hapusnya
        Storage::disk('public')->put('reviews/foto1.jpg', 'content');

        // Action: Hapus review
        $response = $this->actingAs($customer)->delete(route('reviews.destroy', $review->id));

        $response->assertRedirect(); // Back

        // [PERBAIKAN 1]: Gunakan assertSoftDeleted (Bukan assertDatabaseMissing)
        // Karena data tidak hilang fisik, cuma ditandai terhapus
        $this->assertSoftDeleted('reviews', [
            'id' => $review->id
        ]);
        
        // [PERBAIKAN 2]: Cek File Fisik Hilang
        // Jika IDE Anda memberi garis merah di 'assertMissing', abaikan saja.
        // Itu valid di Laravel saat testing.
        Storage::disk('public')->assertMissing('reviews/foto1.jpg');
    }

    public function test_customer_bisa_update_review_dan_tambah_gambar()
    {
        Storage::fake('public');
        $customer = User::factory()->create();
        $review = \App\Models\Review::factory()->create([
            'user_id' => $customer->id,
            'rating' => 3,
            'review' => 'Biasa aja'
        ]);

        $response = $this->actingAs($customer)->post(route('reviews.update', $review->id), [
            'rating' => 5,
            'comment' => 'Jadi bagus setelah revisi!',
            'new_images' => [
                UploadedFile::fake()->image('bukti_baru.jpg')
            ]
        ]);

        $response->assertRedirect();

        $this->assertDatabaseHas('reviews', [
            'id' => $review->id,
            'rating' => 5,
            'review' => 'Jadi bagus setelah revisi!'
        ]);
        
        // Cek apakah gambar tersimpan di DB (array tidak kosong)
        $updatedReview = $review->fresh();
        $this->assertNotEmpty($updatedReview->images);
    }

    public function test_update_review_validasi_kuota_gambar()
    {
        Storage::fake('public');
        $customer = User::factory()->create();
        
        // Review sudah punya 2 gambar
        $review = \App\Models\Review::factory()->create([
            'user_id' => $customer->id,
            'images' => ['img1.jpg', 'img2.jpg']
        ]);

        // User mau upload 2 lagi (Total jadi 4 -> Melanggar Max 3)
        $response = $this->actingAs($customer)->post(route('reviews.update', $review->id), [
            'rating' => 5,
            'comment' => 'Test',
            'new_images' => [
                UploadedFile::fake()->image('img3.jpg'),
                UploadedFile::fake()->image('img4.jpg')
            ]
        ]);

        // Harusnya ada error validasi pada field 'new_images'
        $response->assertSessionHasErrors('new_images');
    }

    public function test_customer_request_token_midtrans_sukses()
    {
        // 1. Setup Data
        $customer = User::factory()->create();
        $booking = Booking::factory()->create([
            'customer_id' => $customer->id,
            'final_price' => 150000,
            'payment_status' => 'unpaid',
            'snap_token' => null
        ]);

        // 2. Setup Config Dummy
        Config::set('services.midtrans.server_key', 'dummy-server-key');
        Config::set('services.midtrans.is_production', false);

        // 3. MOCKING MIDTRANS SNAP
        // Kita "bajak" class Midtrans\Snap agar tidak benar-benar nembak API
        $mock = Mockery::mock('alias:Midtrans\Snap');
        $mock->shouldReceive('getSnapToken')
             ->once() // Berharap dipanggil 1x
             ->andReturn('dummy-snap-token-123'); // Pura-pura balikin token ini

        // 4. Encode ID (Karena route pakai HashID)
        $hashId = Hashids::encode($booking->id);

        // 5. Hit Endpoint
        $response = $this->actingAs($customer)
                         ->postJson(route('bookings.pay', $hashId));

        // 6. Assertions
        $response->assertStatus(200)
                 ->assertJson(['snap_token' => 'dummy-snap-token-123']);

        // Cek Database: Token tersimpan
        $this->assertDatabaseHas('bookings', [
            'id' => $booking->id,
            'snap_token' => 'dummy-snap-token-123'
        ]);

        // Bersihkan Mockery setelah test
        Mockery::close();
    }

    public function test_request_payment_gagal_jika_booking_tidak_valid()
    {
        $customer = User::factory()->create();
        $booking = Booking::factory()->create([
            'customer_id' => $customer->id,
            'final_price' => 0, // Harga 0 tidak boleh bayar
        ]);

        $hashId = Hashids::encode($booking->id);

        $response = $this->actingAs($customer)
                         ->postJson(route('bookings.pay', $hashId));
        
        $response->assertStatus(400); // Bad Request
    }

    public function test_provider_konfirmasi_pembayaran_manual_sukses()
    {
        Notification::fake();
        $provider = User::factory()->create();
        $customer = User::factory()->create();

        $booking = Booking::factory()->create([
            'provider_id' => $provider->id,
            'customer_id' => $customer->id,
            'status' => 'confirmed', // Syarat wajib: harus confirmed
            'payment_status' => 'unpaid'
        ]);

        $response = $this->actingAs($provider)
                         ->post(route('bookings.confirm-payment', $booking));

        $response->assertRedirect();

        // Cek Status Pembayaran Berubah
        $this->assertDatabaseHas('bookings', [
            'id' => $booking->id,
            'payment_status' => 'paid'
        ]);

        // Cek Notifikasi ke Customer
        \Illuminate\Support\Facades\Notification::assertSentTo(
            $customer, 
            \App\Notifications\PaymentConfirmedNotification::class
        );
    }

    public function test_customer_tidak_bisa_konfirmasi_pembayaran_sendiri()
    {
        $customer = User::factory()->create();
        $booking = Booking::factory()->create([
            'customer_id' => $customer->id, // Milik customer ini
            'status' => 'confirmed'
        ]);

        $response = $this->actingAs($customer)
                         ->post(route('bookings.confirm-payment', $booking));

        $response->assertStatus(403); // Forbidden
    }
}