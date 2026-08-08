<?php

namespace App\Traits;

use Vinkla\Hashids\Facades\Hashids;
use Illuminate\Database\Eloquent\Casts\Attribute;

trait Hashidable
{
    // 1. Saat Laravel membuat URL (route('bookings.show', $booking)),
    // dia akan memanggil fungsi ini. Kita ganti return-nya jadi HASH.
    public function getRouteKey()
    {
        return Hashids::encode($this->getKey());
    }

    // 2. Saat Laravel menerima URL (/bookings/Nk7x),
    // dia memanggil fungsi ini untuk mencari data di DB. Kita decode dulu.
    public function resolveRouteBinding($value, $field = null)
    {
        $decoded = Hashids::decode($value);

        if (empty($decoded)) {
            return null; // Jika hash ngawur, return 404
        }

        return $this->where($this->getKeyName(), $decoded[0])->firstOrFail();
    }

    // 3. (Opsional) Tambahkan attribute 'hash_id' agar mudah diakses di Vue
    // $booking->hash_id
    protected function hashId(): Attribute
    {
        return Attribute::make(
            get: fn () => Hashids::encode($this->getKey()),
        );
    }
}