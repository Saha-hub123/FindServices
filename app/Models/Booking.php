<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;


class Booking extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        'service_id',
        'customer_id',
        'provider_id',
        'booking_date',
        'booking_time',
        'location',      // Nama Lokasi
        'latitude',      // Koordinat
        'longitude',     // Koordinat
        'notes',
        'initial_price', // Harga Awal (Estimasi saat booking)
        'final_price',   // Harga Akhir (Deal/Setelah pengerjaan)
        'payment_method',// Metode Pembayaran
        'status'
    ];


    protected $guarded = ['id'];

    // Casting agar kolom tanggal otomatis jadi objek Carbon (mudah diformat di Vue)
    protected $casts = [
        'booking_date' => 'date',
        // 'booking_time' => 'datetime',
    ];

    // Relasi ke Service yang dipesan
    public function service()
    {
        return $this->belongsTo(Service::class)->withTrashed();;
    }

    // Relasi ke User yang menyewa (Customer)
    public function customer()
    {
        return $this->belongsTo(User::class, 'customer_id');
    }

    // Relasi ke User pemilik jasa (Provider)
    public function provider()
    {
        return $this->belongsTo(User::class, 'provider_id');
    }

    // Relasi ke Review (Satu booking punya satu review)
    public function review()
    {
        return $this->hasOne(Review::class);
    }
}