<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes; // 1. Import SoftDeletes

class Report extends Model
{
    use HasFactory, SoftDeletes; // 2. Pakai Trait

    protected $fillable = [
        'user_id',
        'subject',
        'description',
        'proof_images', // 3. Sesuaikan nama kolom
        'status',
    ];

    // 4. Otomatis ubah JSON di database jadi Array PHP
    protected $casts = [
        'proof_images' => 'array',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}