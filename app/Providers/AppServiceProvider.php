<?php

namespace App\Providers;

use Illuminate\Support\Facades\Vite;
use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\URL;
use App\Models\Review;
use App\Observers\ReviewObserver;
use Illuminate\Auth\Notifications\ResetPassword; // Import ini di atas
use Illuminate\Notifications\Messages\MailMessage; // Import ini di atas

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

        // Custom Email Reset Password
        ResetPassword::toMailUsing(function (object $notifiable, string $token) {
            return (new MailMessage)
                ->subject('Permintaan Reset Password')
                ->greeting('Halo!')
                ->line('Anda menerima email ini karena kami menerima permintaan reset password untuk akun Anda.')
                ->action('Reset Password', url(route('password.reset', [
                    'token' => $token,
                    'email' => $notifiable->getEmailForPasswordReset(),
                ], false)))
                ->line('Link reset password ini akan kadaluarsa dalam 60 menit.')
                ->line('Jika Anda tidak meminta reset password, abaikan saja email ini.');
        });
    }
}
