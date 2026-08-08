<?php

namespace Tests\Unit;

use Tests\TestCase;
use App\Models\User;
use Illuminate\Auth\Notifications\ResetPassword;
use Illuminate\Notifications\Messages\MailMessage;

class AppServiceProviderTest extends TestCase
{
    /**
     * Test Custom Email Reset Password.
     * Meng-cover baris kode di dalam ResetPassword::toMailUsing(...)
     */
    public function test_reset_password_notification_format_is_correct()
    {
        // 1. Siapkan Data Dummy
        // Gunakan make() agar tidak perlu simpan ke DB, cukup object di memori
        $user = User::factory()->make([
            'email' => 'test@example.com'
        ]);
        $token = 'dummy-token-123456';

        // 2. Ambil Callback yang didaftarkan di AppServiceProvider
        // Laravel menyimpan closure yang kamu tulis di AppServiceProvider
        // ke dalam static property $toMailCallback pada class ResetPassword.
        $callback = ResetPassword::$toMailCallback;

        // Pastikan callback berhasil didaftarkan (artinya AppServiceProvider:boot jalan)
        $this->assertNotNull($callback, 'Custom ResetPassword callback belum terdaftar.');

        // 3. Eksekusi Callback Tersebut secara Manual
        // Ini akan memaksa baris-baris di dalam function(...) { return (new MailMessage)... } berjalan
        $mailMessage = $callback($user, $token);

        // 4. Assertions (Pengecekan Isi Pesan)
        $this->assertInstanceOf(MailMessage::class, $mailMessage);

        // Cek Subject
        $this->assertEquals('Permintaan Reset Password', $mailMessage->subject);

        // Cek Greeting
        $this->assertEquals('Halo!', $mailMessage->greeting);

        // Cek Content (Intro Lines)
        $this->assertStringContainsString(
            'Anda menerima email ini karena kami menerima permintaan reset password', 
            $mailMessage->introLines[0]
        );

        // Cek Action URL
        // Kita cek apakah token dan email ada di dalam link
        $this->assertStringContainsString($token, $mailMessage->actionUrl);
        $this->assertStringContainsString('test%40example.com', $mailMessage->actionUrl); // URL encoded email

        // Cek Expiry Message (Outro Lines)
        $this->assertStringContainsString(
            'Link reset password ini akan kadaluarsa dalam 60 menit', 
            $mailMessage->outroLines[0]
        );
    }
}