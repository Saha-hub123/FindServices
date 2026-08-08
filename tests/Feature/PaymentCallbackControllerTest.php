<?php

namespace Tests\Feature;

use App\Models\Booking;
use App\Models\User;
use App\Models\Service;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\Notification;
use Vinkla\Hashids\Facades\Hashids;
use Tests\TestCase;

class PaymentCallbackControllerTest extends TestCase
{
    use RefreshDatabase;

    // Helper untuk membuat Signature Key palsu ala Midtrans
    private function generateSignature($orderId, $statusCode, $grossAmount, $serverKey)
    {
        return hash("sha512", $orderId . $statusCode . $grossAmount . $serverKey);
    }

    protected function setUp(): void
    {
        parent::setUp();
        // Set Server Key dummy untuk keperluan testing
        Config::set('services.midtrans.server_key', 'SB-Mid-server-TESTKEY123');
    }

    // 1. TEST PEMBAYARAN SUKSES (Settlement)
    public function test_midtrans_callback_success_settlement()
    {
        Notification::fake(); // Mock Notifikasi

        // A. Siapkan Data Booking
        $provider = User::factory()->create();
        $customer = User::factory()->create();
        $service = Service::factory()->create(['user_id' => $provider->id]);
        
        $booking = Booking::factory()->create([
            'customer_id' => $customer->id,
            'provider_id' => $provider->id,
            'service_id' => $service->id,
            'status' => 'pending',
            'payment_status' => 'unpaid',
            'final_price' => 100000, // Harga harus integer
        ]);

        // B. Rakit ORDER ID sesuai format Controller: BOOK-{hash}-{timestamp}
        $bookingHash = Hashids::encode($booking->id);
        $orderId = "BOOK-{$bookingHash}-" . time();

        // C. Siapkan Payload (Data Pura-pura dari Midtrans)
        $serverKey = config('services.midtrans.server_key');
        $grossAmount = '100000.00'; // Midtrans kirim string dengan desimal

        $payload = [
            'transaction_status' => 'settlement', // Status SUKSES
            'fraud_status' => 'accept',
            'order_id' => $orderId,
            'status_code' => '200',
            'gross_amount' => $grossAmount,
            // Generate Signature yang valid
            'signature_key' => $this->generateSignature($orderId, '200', $grossAmount, $serverKey),
        ];

        // D. Kirim POST Request ke Controller
        // Ganti 'payment.notification' sesuai nama route Anda di web.php/api.php
        // Jika belum ada nama route, pakai URL manual misal: '/payments/midtrans-notification'
        $response = $this->postJson(route('payment.notification'), $payload);

        // E. Assertions
        $response->assertStatus(200);

        // Cek Database Berubah
        $this->assertDatabaseHas('bookings', [
            'id' => $booking->id,
            'payment_status' => 'paid',     // Harusnya jadi paid
            'status' => 'confirmed',        // Harusnya jadi confirmed
        ]);

        // Cek Notifikasi Terkirim
        // Ke Provider (Uang Masuk)
        Notification::assertSentTo($provider, \App\Notifications\PaymentConfirmedNotification::class);
        // Ke Customer (Status Update)
        Notification::assertSentTo($customer, \App\Notifications\BookingStatusUpdatedNotification::class);
    }

    // 2. TEST PEMBAYARAN KADALUARSA (Expire)
    public function test_midtrans_callback_expire()
    {
        Notification::fake();

        $booking = Booking::factory()->create([
            'payment_status' => 'unpaid',
            'status' => 'pending',
            'final_price' => 50000
        ]);

        $bookingHash = Hashids::encode($booking->id);
        $orderId = "BOOK-{$bookingHash}-" . time();
        $serverKey = config('services.midtrans.server_key');
        $grossAmount = '50000.00';

        $payload = [
            'transaction_status' => 'expire', // Status EXPIRE
            'order_id' => $orderId,
            'status_code' => '200',
            'gross_amount' => $grossAmount,
            'signature_key' => $this->generateSignature($orderId, '200', $grossAmount, $serverKey),
        ];

        $response = $this->postJson(route('payment.notification'), $payload);

        $response->assertStatus(200);

        // Cek Database: Harusnya Cancelled & Expired
        $this->assertDatabaseHas('bookings', [
            'id' => $booking->id,
            'payment_status' => 'expired',
            'status' => 'cancelled',
        ]);
    }

    // 3. TEST KEAMANAN: SIGNATURE KEY SALAH
    public function test_midtrans_callback_rejects_invalid_signature()
    {
        $booking = Booking::factory()->create();
        $bookingHash = Hashids::encode($booking->id);
        $orderId = "BOOK-{$bookingHash}-" . time();

        $payload = [
            'transaction_status' => 'capture',
            'order_id' => $orderId,
            'status_code' => '200',
            'gross_amount' => '100000.00',
            'signature_key' => 'tanda_tangan_palsu_hacker', // <--- SIGNATURE SALAH
        ];

        $response = $this->postJson(route('payment.notification'), $payload);

        // Harusnya ditolak 403 Forbidden
        $response->assertStatus(403);
    }

    // 4. TEST FORMAT ORDER ID SALAH (Gagal Decode)
    public function test_midtrans_callback_rejects_invalid_order_id_format()
    {
        $payload = [
            'transaction_status' => 'capture',
            'order_id' => 'BOOK-ngawur-123', // Hash ngawur tidak bisa didecode
            'status_code' => '200',
            'gross_amount' => '100000.00',
        ];
        
        // Kita hitung signature yang benar supaya lolos validasi tahap 1
        $serverKey = config('services.midtrans.server_key');
        $payload['signature_key'] = $this->generateSignature($payload['order_id'], '200', '100000.00', $serverKey);

        $response = $this->postJson(route('payment.notification'), $payload);

        // Harusnya error 400 karena gagal decode booking ID
        $response->assertStatus(400); 
    }

    public function test_midtrans_callback_capture_accept_credit_card()
    {
        Notification::fake();

        // 1. Setup Booking
        $booking = Booking::factory()->create([
            'payment_status' => 'unpaid',
            'status' => 'pending',
            'final_price' => 100000
        ]);

        $bookingHash = Hashids::encode($booking->id);
        $orderId = "BOOK-{$bookingHash}-" . time();
        $serverKey = config('services.midtrans.server_key');
        $grossAmount = '100000.00';

        // 2. Payload Capture + Accept
        $payload = [
            'transaction_status' => 'capture', // <--- Capture
            'fraud_status' => 'accept',        // <--- Accept
            'order_id' => $orderId,
            'status_code' => '200',
            'gross_amount' => $grossAmount,
            'signature_key' => $this->generateSignature($orderId, '200', $grossAmount, $serverKey),
        ];

        // 3. Hit Endpoint
        $response = $this->postJson(route('payment.notification'), $payload);

        // 4. Assert
        $response->assertStatus(200);

        $this->assertDatabaseHas('bookings', [
            'id' => $booking->id,
            'payment_status' => 'paid',      // Harusnya Paid
            'status' => 'confirmed',         // Harusnya Confirmed
        ]);
    }

    public function test_midtrans_callback_deny_or_cancel()
    {
        $booking = Booking::factory()->create([
            'payment_status' => 'unpaid',
            'final_price' => 100000
        ]);

        $bookingHash = Hashids::encode($booking->id);
        $orderId = "BOOK-{$bookingHash}-" . time();
        $serverKey = config('services.midtrans.server_key');
        $grossAmount = '100000.00';

        // Payload Deny
        $payload = [
            'transaction_status' => 'deny', // <--- Deny
            'order_id' => $orderId,
            'status_code' => '202',
            'gross_amount' => $grossAmount,
            'signature_key' => $this->generateSignature($orderId, '202', $grossAmount, $serverKey),
        ];

        $response = $this->postJson(route('payment.notification'), $payload);

        $response->assertStatus(200);

        $this->assertDatabaseHas('bookings', [
            'id' => $booking->id,
            'payment_status' => 'failed',    // Harusnya Failed
            'status' => 'cancelled',         // Harusnya Cancelled
        ]);
    }

    public function test_midtrans_callback_pending_status()
    {
        $booking = Booking::factory()->create([
            'payment_status' => 'unpaid',
            'status' => 'pending',
            'final_price' => 100000
        ]);

        $bookingHash = Hashids::encode($booking->id);
        $orderId = "BOOK-{$bookingHash}-" . time();
        $serverKey = config('services.midtrans.server_key');
        $grossAmount = '100000.00';

        // Payload Pending
        $payload = [
            'transaction_status' => 'pending', // <--- Pending
            'order_id' => $orderId,
            'status_code' => '201',
            'gross_amount' => $grossAmount,
            'signature_key' => $this->generateSignature($orderId, '201', $grossAmount, $serverKey),
        ];

        $response = $this->postJson(route('payment.notification'), $payload);

        $response->assertStatus(200);

        // Status Booking TIDAK boleh berubah jadi confirmed
        $this->assertDatabaseHas('bookings', [
            'id' => $booking->id,
            'payment_status' => 'pending',
            'status' => 'pending', 
        ]);
    }

    public function test_midtrans_callback_server_error_exception()
    {
        // 1. Setup Data Valid
        $booking = Booking::factory()->create(['final_price' => 100000]);
        $bookingHash = Hashids::encode($booking->id);
        $orderId = "BOOK-{$bookingHash}-" . time();
        $serverKey = config('services.midtrans.server_key');
        $grossAmount = '100000.00';

        // 2. SABOTASE: Paksa error saat Booking di-update
        // Kita pasang "jebakan" di event updating model
        \App\Models\Booking::updating(function ($booking) {
            throw new \Exception('Simulasi Database Error');
        });

        $payload = [
            'transaction_status' => 'settlement',
            'order_id' => $orderId,
            'status_code' => '200',
            'gross_amount' => $grossAmount,
            'signature_key' => $this->generateSignature($orderId, '200', $grossAmount, $serverKey),
        ];

        // 3. Hit Endpoint
        $response = $this->postJson(route('payment.notification'), $payload);

        // 4. Assert: Harusnya Error 500 (Server Error)
        $response->assertStatus(500);
        $response->assertJson(['message' => 'Server Error']);
    }
}