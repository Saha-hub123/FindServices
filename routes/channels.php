<?php

use Illuminate\Support\Facades\Broadcast;
use App\Models\Booking; // Jangan lupa import

// 1. Channel Chat Pribadi (Sudah ada)
Broadcast::channel('chat.{userId}', function ($user, $userId) {
    return (int) $user->id === (int) $userId;
});

Broadcast::channel('booking.{bookingId}', function ($user, $bookingId) {
    // Cari booking berdasarkan ID
    $booking = Booking::find($bookingId);
    
    if (!$booking) return false;

    // Izinkan JIKA user yang login adalah Costumer ATAU Provider dari booking tersebut
    return (int) $user->id === (int) $booking->customer_id || 
           (int) $user->id === (int) $booking->provider_id;
});

// 3. [BARU] Channel Presence 'online'
// Channel ini mengembalikan info user jika dia connect
Broadcast::channel('online', function ($user) {
    if (Auth::check()) {
        return ['id' => $user->id, 'name' => $user->name];
    }
});