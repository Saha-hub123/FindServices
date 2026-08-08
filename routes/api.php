<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\PaymentCallbackController; // <--- Jangan lupa import ini
use App\Events\TestLatency;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::post('/midtrans/callback', [PaymentCallbackController::class, 'handle'])->name('payment.notification');

// Route ini menerima tembakan dari k6, lalu meneruskannya ke Reverb
Route::post('/test-latency', function (Request $request) {
    $type = $request->input('type', 'simple');
    $data = [];

    // Simulasi Struktur Data Asli
    if ($type === 'review') {
        // Pura-pura ini data dari Model Review
        $data = [
            'id' => 101,
            'rating' => 5,
            'comment' => 'Layanan sangat memuaskan, teknisi datang tepat waktu!',
            'technician' => ['name' => 'Budi Santoso', 'badge' => 'Gold'],
            'created_at' => now()->toDateTimeString(),
            'photos' => ['url1.jpg', 'url2.jpg'] // Simulasi data agak besar
        ];
    } 
    elseif ($type === 'booking') {
        // Pura-pura ini data dari Model Booking
        $data = [
            'booking_hash' => 'ABC-123-XYZ',
            'status' => 'confirmed',
            'estimated_arrival' => now()->addHour()->toDateTimeString(),
            'steps' => [
                ['name' => 'Pending', 'completed' => true],
                ['name' => 'Confirmed', 'completed' => true],
                ['name' => 'On The Way', 'completed' => false],
            ]
        ];
    } 
    else {
        $data = "Tes Ping Sederhana";
    }

    // Dispatch Event dengan data tersebut
    TestLatency::dispatch($type, $data);

    return response()->json(['status' => 'fired', 'type' => $type]);
});