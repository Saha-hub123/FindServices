<?php

use App\Models\Booking; 
use App\Models\User;

// 1. Channel Chat
// GANTI {userId} jadi {user} agar otomatis decode Hash User ID
Broadcast::channel('chat.{user}', function ($currentUser, User $user) {
    return (int) $currentUser->id === (int) $user->id;
});

// 2. Channel Booking
// GANTI {bookingId} jadi {booking} agar otomatis decode Hash Booking ID
Broadcast::channel('booking.{booking}', function ($user, Booking $booking) {
    // Tidak perlu Booking::find() manual lagi. Laravel sudah melakukannya.
    
    return (int) $user->id === (int) $booking->customer_id || 
           (int) $user->id === (int) $booking->provider_id;
});

// 3. Channel Online (Opsional: return hash_id)
Broadcast::channel('online', function ($user) {
    if (Auth::check()) {
        return ['id' => $user->id, 'hash_id' => $user->hash_id, 'name' => $user->name];
    }
});