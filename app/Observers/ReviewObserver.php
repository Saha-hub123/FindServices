<?php

namespace App\Observers;

use App\Models\Review;
use App\Models\Service;

class ReviewObserver
{
    /**
     * Fungsi Helper: Menghitung ulang rata-rata rating Service
     * dan menyimpannya ke database.
     */
    private function recalculateRating($serviceId)
    {
        // 1. Cari Service-nya
        $service = Service::find($serviceId);

        if ($service) {
            // 2. Hitung rata-rata dari tabel reviews
            // avg() otomatis mengabaikan soft deleted records
            $newAvg = $service->reviews()->avg('rating');

            // 3. Update kolom rating_avg (jika null/kosong jadikan 0)
            $service->rating_avg = $newAvg ?? 0;
            
            // 4. Simpan tanpa mengubah updated_at (opsional, biar 'clean')
            $service->saveQuietly(); 
        }
    }

    /**
     * Handle the Review "created" event.
     * Jalan saat user baru submit review.
     */
    public function created(Review $review)
    {
        $this->recalculateRating($review->service_id);
    }

    /**
     * Handle the Review "updated" event.
     * Jalan saat user mengedit rating mereka.
     */
    public function updated(Review $review)
    {
        // Hanya hitung ulang jika kolom 'rating' yang berubah
        // (Kalau cuma edit komentar, tidak perlu hitung ulang rating)
        if ($review->isDirty('rating')) {
            $this->recalculateRating($review->service_id);
        }
    }

    /**
     * Handle the Review "deleted" event.
     * Jalan saat review dihapus (Soft Delete atau Hard Delete).
     */
    public function deleted(Review $review)
    {
        $this->recalculateRating($review->service_id);
    }

    /**
     * Handle the Review "restored" event.
     * Jalan saat review yang dihapus dikembalikan.
     */
    public function restored(Review $review)
    {
        $this->recalculateRating($review->service_id);
    }
}