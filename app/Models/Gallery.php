<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Gallery extends Model
{
    use HasFactory;

    protected $guarded = ['id'];

    // Relasi ke Service induknya
    public function service()
    {
        return $this->belongsTo(Service::class);
    }
    
    // Opsional: Accessor untuk mendapatkan URL gambar full
    // Di Vue nanti tinggal panggil: gallery.image_url
    public function getImageUrlAttribute()
    {
        return asset('storage/' . $this->image);
    }
}