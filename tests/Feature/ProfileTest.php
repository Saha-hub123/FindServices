<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Storage;
use Illuminate\Http\UploadedFile;
use Tests\TestCase;

class ProfileTest extends TestCase
{
    use RefreshDatabase;

    public function test_profile_page_is_displayed(): void
    {
        $user = User::factory()->create();

        $response = $this
            ->actingAs($user)
            ->get(route('profile.index'));

        $response->assertOk();
    }

    public function test_settings_page_is_displayed(): void
    {
        $user = User::factory()->create();

        $response = $this
            ->actingAs($user)
            ->get(route('profile.settings'));

        $response->assertOk();
    }

    public function test_profile_information_can_be_updated(): void
    {
        Storage::fake('public');
        $user = User::factory()->create();

        $response = $this
            ->actingAs($user)
            ->patch(route('profile.update'), [
                'name' => 'Test User Updated',
                'email' => 'test@example.com',
                'avatar' => UploadedFile::fake()->image('avatar.jpg')
            ]);

        $response
            ->assertSessionHasNoErrors()
            ->assertRedirect(route('profile.index'));

        $user->refresh();

        $this->assertSame('Test User Updated', $user->name);
        $this->assertSame('test@example.com', $user->email);
        $this->assertNull($user->email_verified_at);
        $this->assertNotNull($user->avatar);
    }

    public function test_user_can_delete_their_account(): void
    {
        $user = User::factory()->create();

        $response = $this
            ->actingAs($user)
            ->delete(route('profile.destroy'), [
                'password' => 'password',
            ]);

        $response
            ->assertSessionHasNoErrors()
            ->assertRedirect('/');

        $this->assertGuest();

        // PERBAIKAN: Gunakan assertSoftDeleted karena user menggunakan SoftDeletes
        // Cek bahwa di tabel users, id tersebut sudah terisi kolom deleted_at-nya
        $this->assertSoftDeleted('users', [
            'id' => $user->id
        ]);
    }

    public function test_can_view_other_user_profile(): void
    {
        $me = User::factory()->create();
        $otherUser = User::factory()->create();

        // PERBAIKAN: Kirim object $otherUser, bukan ID-nya
        // Agar Laravel otomatis menghandle HashID / Route Binding
        $response = $this
            ->actingAs($me)
            ->get(route('profile.show', $otherUser));

        $response->assertOk();
    }

    // ... method lain ...

    // TAMBAHAN: Test Halaman Edit Visual (Avatar, Bio, dll)
    public function test_halaman_edit_profil_visual_bisa_diakses()
    {
        $user = User::factory()->create();

        // Sesuai web.php: Route::get('/profile/edit', ...)->name('profile.edit')
        $response = $this->actingAs($user)->get(route('profile.edit'));

        $response->assertStatus(200);

        $response->assertInertia(fn ($page) => $page
            ->component('Profile/Edit') // Pastikan nama komponen Vue benar
            ->has('mustVerifyEmail')
            ->has('status')
        );
    }
}