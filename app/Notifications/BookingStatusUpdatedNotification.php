<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Notification;

class BookingStatusUpdatedNotification extends Notification
{
    use Queueable;

    public $booking;

    public function __construct($booking)
    {
        $this->booking = $booking;
    }

    public function via($notifiable)
    {
        return ['database'];
    }

    public function toArray($notifiable)
    {
        $status = $this->booking->status;
        $serviceTitle = $this->booking->service->title;
        // [UBAH DISINI] Gunakan hash_id agar yang muncul bukan angka asli
        $bookingId = $this->booking->hash_id;
        
        // Tentukan siapa lawan bicaranya untuk pesan yang lebih personal
        // Jika notifikasi dikirim ke Provider, sebut "Customer". 
        // Jika ke Customer, sebut "Penyedia".
        $isProvider = $notifiable->id === $this->booking->provider_id;
        $actorName = $isProvider ? $this->booking->customer->name : $this->booking->provider->name;

        $message = '';
        $iconType = 'info'; // default

        switch ($status) {
            case 'confirmed':
                $message = "Pesanan <b>#{$bookingId}</b> ({$serviceTitle}) telah <b>DITERIMA</b>. Cek detail jadwal.";
                $iconType = 'check';
                break;
            
            case 'pending':
                $message = "Pesanan <b>#{$bookingId}</b> ({$serviceTitle}) diajukan ulang oleh customer.";
                $iconType = 'check';
                break;
                
            case 'rejected':
                $message = "Pesanan <b>#{$bookingId}</b> ({$serviceTitle}) <b>DITOLAK</b> oleh penyedia.";
                $iconType = 'cross';
                break;
                
            case 'cancelled':
                $message = "Pesanan <b>#{$bookingId}</b> ({$serviceTitle}) telah <b>DIBATALKAN</b> oleh <b>{$actorName}</b>.";
                $iconType = 'cross';
                break;
                
            case 'in_progress':
                if ($isProvider) {
                    $message = "Pesanan <b>#{$bookingId}</b> tidak dikonfirmasi selesai oleh Customer, silakan lanjutkan pengerjaan.";
                } else {
                    $message = "Penyedia mulai mengerjakan pesanan <b>#{$bookingId}</b> ({$serviceTitle}).";
                }
                $iconType = 'tools';
                break;
                
            case 'waiting_completion':
                $message = "Penyedia menyatakan pekerjaan <b>#{$bookingId}</b> selesai. Mohon konfirmasi.";
                $iconType = 'clock';
                break;
                
            case 'completed':
                // Pesan beda untuk Customer dan Provider
                if ($isProvider) {
                    $message = "Pesanan <b>#{$bookingId}</b> telah dikonfirmasi selesai oleh Customer.";
                } else {
                    $message = "Pesanan <b>#{$bookingId}</b> selesai. Terima kasih telah menggunakan jasa ini!";
                }
                $iconType = 'check';
                break;
                
            default:
                $message = "Status pesanan <b>#{$bookingId}</b> berubah menjadi <b>{$status}</b>.";
        }

        return [
            'message' => $message,
            'action_url' => route('bookings.show', $this->booking->hash_id),
            'type' => 'booking_status', 
            'icon_type' => $iconType, // Bisa dipakai di frontend untuk icon dinamis (fa-check, fa-times, dll)
            'status' => $status
        ];
    }
}