<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Notification;

class NewBookingNotification extends Notification
{
    use Queueable;

    public $booking;

    /**
     * Terima data booking saat notifikasi dibuat.
     */
    public function __construct($booking)
    {
        $this->booking = $booking;
    }

    /**
     * Tentukan jalur pengiriman (kita pakai database).
     */
    public function via($notifiable)
    {
        return ['database']; // Bisa tambah 'mail' jika ingin kirim email juga
    }

    /**
     * Format data yang disimpan ke tabel 'notifications' kolom 'data'.
     * Struktur ini HARUS COCOK dengan yang kita panggil di Vue (notification.data.message).
     */
    public function toArray($notifiable)
    {
        // Data pendukung
        $customerName = $this->booking->customer->name; // Nama pemesan
        $serviceTitle = $this->booking->service->title; // Judul jasa

        return [
            // Pesan dengan HTML bold agar estetik
            'message' => "<b>{$customerName}</b> membuat pesanan baru untuk jasa <b>{$serviceTitle}</b>.",
            
            // Link tujuan saat notifikasi diklik
            'action_url' => route('bookings.show', $this->booking),
            
            // Tipe notifikasi (opsional, untuk membedakan icon di frontend nanti)
            'type' => 'booking_new'
        ];
    }
}