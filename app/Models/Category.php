<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes; // <--- Import ini


class Category extends Model
{
    use HasFactory, SoftDeletes;

    protected $guarded = ['id'];

    protected $fillable = [
        'name', 
        'slug', 
        'description', 
        'icon_class' // <-- Tambahkan ini
    ];

    public function getRouteKeyName()
    {
        return 'slug';
    }

    // Relasi: Satu kategori punya banyak service
    public function services()
    {
        return $this->hasMany(Service::class);
    }
}