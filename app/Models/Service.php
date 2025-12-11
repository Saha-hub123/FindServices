<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Service extends Model
{
    use HasFactory, SoftDeletes;

    protected $guarded = ['id'];

    // Menentukan kolom mana saja yang boleh diisi secara massal (create/update)
    protected $fillable = [
        'user_id',      // ID Pemilik Jasa
        'category_id',  // ID Kategori
        'title',        // Judul Jasa
        'description',  // Deskripsi
        'price_min',    // Harga Terendah
        'price_max',    // Harga Tertinggi
        'location',     // Alamat Teks
        'latitude',     // Koordinat Map (Baru)
        'longitude',    // Koordinat Map (Baru)
        'status',       // active/inactive/pending
        'rating_avg',    // Rata-rata rating (opsional, jika ingin bisa diupdate langsung)
        'slug',
    ];

    // Relasi: Dimiliki oleh User (Provider)
    public function user()
    {
        return $this->belongsTo(User::class);
    }

    // Relasi: Termasuk dalam Kategori tertentu
    public function category()
    {
        return $this->belongsTo(Category::class);
    }

    // Relasi: Punya banyak foto galeri
    public function galleries()
    {
        return $this->hasMany(Gallery::class);
    }

    // Relasi: Punya banyak bookingan
    public function bookings()
    {
        return $this->hasMany(Booking::class);
    }

    // Relasi: Punya banyak review
    public function reviews()
    {
        return $this->hasMany(Review::class);
    }

    // Scope Helper: Untuk mempermudah query mengambil service yang aktif saja
    // Cara pakai di Controller: Service::active()->get();
    public function scopeActive($query)
    {
        return $query->where('status', 'active');
    }

    public function getRouteKeyName()
    {
        return 'slug';
    }
}