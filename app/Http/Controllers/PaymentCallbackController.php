<?php

namespace App\Http\Controllers;

use App\Models\Booking;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log; // Wajib import Log
use App\Notifications\PaymentConfirmedNotification; // Import Notif Sukses
use App\Notifications\BookingStatusUpdatedNotification; // Import Notif Status (Gagal/Cancel)
use Vinkla\Hashids\Facades\Hashids; // [WAJIB IMPORT]

class PaymentCallbackController extends Controller
{
    public function handle(Request $request)
    {
        try {
            // 1. Ambil Server Key dari Config
            $serverKey = config('services.midtrans.server_key');

            // 2. Validasi Signature Key (Keamanan)
            // Pastikan urutan hash benar: order_id + status_code + gross_amount + server_key
            $hashed = hash("sha512", $request->order_id . $request->status_code . $request->gross_amount . $serverKey);
            
            if ($hashed !== $request->signature_key) {
                Log::warning("Midtrans Invalid Signature: " . $request->order_id);
                return response()->json(['message' => 'Invalid signature'], 403);
            }

            // 3. PARSING & DECODE ID BOOKING [BAGIAN INI DIPERBAIKI]
            // Format Order ID: BOOK-{hash_id}-{timestamp} (Contoh: BOOK-4x1-17823612)
            $orderIdParts = explode('-', $request->order_id);
            
            // Ambil bagian Hash ID (index ke-1)
            $bookingHash = $orderIdParts[1] ?? null; 

            if (!$bookingHash) {
                return response()->json(['message' => 'Invalid Order ID Format'], 400);
            }

            // [FIX] DECODE Hash ID ke Integer
            $decoded = Hashids::decode($bookingHash);
            $bookingIdInt = $decoded[0] ?? null;

            if (!$bookingIdInt) {
                Log::error("Midtrans Error: Gagal decode hash '$bookingHash' dari order_id '$request->order_id'");
                return response()->json(['message' => 'Invalid Booking Hash'], 400);
            }
            
            // Cari Booking menggunakan ID Integer
            $booking = Booking::find($bookingIdInt);

            if (!$booking) {
                Log::error("Midtrans Error: Booking ID $bookingIdInt tidak ditemukan di DB.");
                return response()->json(['message' => 'Booking not found'], 404);
            }

            // 4. Cek Status Transaksi dari Midtrans
            $transactionStatus = $request->transaction_status;
            $fraudStatus = $request->fraud_status;
            
            // Siapkan variabel status baru
            $newPaymentStatus = null;
            $newBookingStatus = null;

            // --- LOGIKA STATUS MIDTRANS ---
            if ($transactionStatus == 'capture') {
                if ($fraudStatus == 'accept') {
                    $newPaymentStatus = 'paid';
                    $newBookingStatus = 'confirmed';
                }
            } else if ($transactionStatus == 'settlement') {
                // Lunas (Transfer/Gopay)
                $newPaymentStatus = 'paid';
                $newBookingStatus = 'confirmed'; 
            } else if ($transactionStatus == 'cancel' || $transactionStatus == 'deny') {
                $newPaymentStatus = 'failed';
                $newBookingStatus = 'cancelled'; 
            } else if ($transactionStatus == 'expire') {
                $newPaymentStatus = 'expired';
                $newBookingStatus = 'cancelled'; 
            } else if ($transactionStatus == 'pending') {
                $newPaymentStatus = 'pending';
            }

            // 5. Simpan & Kirim Notifikasi
            if ($newPaymentStatus) {
                
                // Cek agar tidak update berulang jika status sama
                if ($booking->payment_status !== $newPaymentStatus) {
                    
                    $updateData = ['payment_status' => $newPaymentStatus];
                    
                    // Update status booking hanya jika diperlukan (misal jadi confirmed atau cancelled)
                    if ($newBookingStatus && $booking->status !== 'completed' && $booking->status !== 'cancelled') {
                        $updateData['status'] = $newBookingStatus;
                    }

                    $booking->update($updateData);

                    // --- NOTIFIKASI START ---
                    
                    try {
                        // KASUS A: PEMBAYARAN SUKSES (GATEWAY)
                        if ($newPaymentStatus == 'paid') {
                            
                            // [PERBAIKAN LOGIC SESUAI KONSEP 2]
                            
                            // 1. Kirim Notif Pembayaran ke PROVIDER (Agar Provider tahu ada uang masuk)
                            // Notification Class ini akan mendeteksi 'gateway' dan menampilkan pesan: "LUNAS... Silakan proses"
                            $booking->provider->notify(new PaymentConfirmedNotification($booking));

                            // 2. Kirim Notif Status ke CUSTOMER (Agar Customer tahu statusnya sudah Confirmed)
                            // Notification Class ini memberitahu perubahan status biasa
                            $booking->customer->notify(new BookingStatusUpdatedNotification($booking));
                        }
                        // KASUS B: GAGAL / EXPIRED
                        else if ($newPaymentStatus == 'expired' || $newPaymentStatus == 'failed') {
                            $booking->customer->notify(new BookingStatusUpdatedNotification($booking));
                            $booking->provider->notify(new BookingStatusUpdatedNotification($booking));
                        }
                    } catch (\Exception $e) {
                        Log::error("Midtrans Notification Error: " . $e->getMessage());
                        // Lanjut terus, jangan return error cuma gara-gara notif gagal
                    }
                    // --- NOTIFIKASI END ---

                    Log::info("Midtrans Callback Success: Booking #$bookingIdInt ($bookingHash) changed to $newPaymentStatus");
                }
            }

            return response()->json(['message' => 'Callback received successfully']);

        } catch (\Exception $e) {
            Log::error("Midtrans Callback Exception: " . $e->getMessage());
            return response()->json(['message' => 'Server Error'], 500);
        }
    }
}