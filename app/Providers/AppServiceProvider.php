<?php

namespace App\Providers;

use Illuminate\Support\Facades\Vite;
use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\URL;
use App\Models\Review;
use App\Observers\ReviewObserver;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        Vite::prefetch(concurrency: 3);

        // nyalakan ini dan coment yang vite diatas
        // if (config('app.env') !== 'local') { 
        //     URL::forceScheme('https');
        // }
        
        // URL::forceScheme('https');

        // 2. Daftarkan di sini
        Review::observe(ReviewObserver::class);
    }
}
