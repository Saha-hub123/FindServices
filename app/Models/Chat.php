<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Chat extends Model
{
    use HasFactory, SoftDeletes;

    // Definisikan kolom apa saja yang boleh diisi
    protected $fillable = [
        'sender_id',
        'receiver_id',
        'service_id',
        'booking_id',
        'message',
        'is_read',
        'reply_to_id'
    ];

    // Mengizinkan semua kolom diisi (kecuali id)
    protected $guarded = ['id'];

    // Ubah format kolom is_read jadi boolean (true/false) agar mudah dibaca Vue
    protected $casts = [
        'is_read' => 'boolean',
        'created_at' => 'datetime',
    ];

    /**
     * Relasi ke User pengirim pesan
     */
    public function sender()
    {
        return $this->belongsTo(User::class, 'sender_id');
    }

    /**
     * Relasi ke User penerima pesan
     */
    public function receiver()
    {
        return $this->belongsTo(User::class, 'receiver_id');
    }

    /**
     * Relasi ke Service (Jasa)
     * Digunakan untuk mengetahui chat ini membahas jasa apa
     */
    public function service()
    {
        return $this->belongsTo(Service::class)->withTrashed();
    }

    /**
     * Relasi ke Booking
     * (Opsional) Jika chat ini terkait transaksi tertentu
     */
    public function booking()
    {
        return $this->belongsTo(Booking::class)->withTrashed();
    }

    // Relasi ke pesan yang dikutip/dibalas
    public function replyTo()
    {
        return $this->belongsTo(Chat::class, 'reply_to_id');
    }
}