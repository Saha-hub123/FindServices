<?php

namespace Tests\Feature\Auth;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Notification;
use Tests\TestCase;

class EmailVerificationNotificationTest extends TestCase
{
    use RefreshDatabase;

    // 1. Test: User yang belum verifikasi BISA minta link baru
    public function test_email_verification_link_can_be_requested(): void
    {
        Notification::fake(); // Pura-pura kirim email (biar gak error SMTP)

        // Buat user yang status emailnya BELUM verifikasi (unverified)
        // Biasanya factory Laravel punya state 'unverified'
        $user = User::factory()->unverified()->create();

        // Login & Request ke route 'verification.send'
        // (Pastikan nama route di auth.php Anda adalah 'verification.send')
        $response = $this->actingAs($user)->post(route('verification.send'));

        // Harapannya: Redirect Back (ke halaman sebelumnya)
        $response->assertRedirect();
        
        // Harapannya: Ada pesan session 'status' -> 'verification-link-sent'
        $response->assertSessionHas('status', 'verification-link-sent');
    }

    // 2. Test: User yang SUDAH verifikasi akan diredirect ke Dashboard jika minta link lagi
    public function test_verified_user_is_redirected_if_requesting_verification_link(): void
    {
        // Buat user yang SUDAH verifikasi (default factory biasanya verified)
        $user = User::factory()->create([
            'email_verified_at' => now()
        ]);

        $response = $this->actingAs($user)->post(route('verification.send'));

        // Harapannya: Langsung dilempar ke Dashboard
        $response->assertRedirect(route('dashboard'));
    }
}