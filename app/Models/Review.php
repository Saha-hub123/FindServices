<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Review extends Model
{
    use HasFactory, SoftDeletes;

    protected $guarded = ['id'];

    // Relasi ke Booking asal review ini
    public function booking()
    {
        return $this->belongsTo(Booking::class);
    }

    // Relasi ke Service yang direview
    public function service()
    {
        return $this->belongsTo(Service::class);
    }

    // Relasi ke User penulis review
    public function user()
    {
        return $this->belongsTo(User::class);
    }
}