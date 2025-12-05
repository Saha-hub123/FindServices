<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Category extends Model
{
    use HasFactory;

    protected $guarded = ['id'];

    // Relasi: Satu kategori punya banyak service
    public function services()
    {
        return $this->hasMany(Service::class);
    }
}