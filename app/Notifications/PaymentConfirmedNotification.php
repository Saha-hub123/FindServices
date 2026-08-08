<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Notification;

class PaymentConfirmedNotification extends Notification
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
        $hashId = $this->booking->hash_id;
        $isGateway = $this->booking->payment_method === 'gateway';

        // LOGIKA PESAN BERDASARKAN KONSEP
        if ($isGateway) {
            // KONSEP 2: Gateway (Otomatis)
            // Target: Provider
            // Pesan: Memberitahu Provider bahwa ada uang masuk / pesanan lunas otomatis
            $message = "Pesanan <b>#{$hashId}</b> telah <b>LUNAS</b> via Gateway (Otomatis). Silakan proses.";
        } else {
            // KONSEP 1: Manual
            // Target: Customer
            // Pesan: Memberitahu Customer bahwa bukti transfernya sudah di-ACC provider
            $message = "Pembayaran Manual pesanan <b>#{$hashId}</b> telah <b>DIKONFIRMASI</b> oleh Provider.";
        }
        
        return [
            'message' => $message,
            // Route show otomatis menggunakan getRouteKey (Hash ID)
            'action_url' => route('bookings.show', $this->booking), 
            'type' => 'payment_success',
            'icon_type' => 'check'
        ];
    }
}