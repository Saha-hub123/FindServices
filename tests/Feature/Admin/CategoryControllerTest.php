<?php

namespace Tests\Feature\Admin;

use App\Models\User;
use App\Models\Category;
use App\Models\Service;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CategoryControllerTest extends TestCase
{
    use RefreshDatabase;

    // Helper: Buat user admin
    private function createAdmin()
    {
        return User::factory()->create([
            'role' => 'admin', // Pastikan middleware mengecek kolom ini
            'email_verified_at' => now(),
        ]);
    }

    public function test_admin_bisa_akses_halaman_kategori()
    {
        $admin = $this->createAdmin();
        $response = $this->actingAs($admin)->get(route('admin.categories.index'));
        $response->assertStatus(200);
    }

    public function test_user_biasa_tidak_bisa_akses_halaman_kategori()
    {
        $user = User::factory()->create(['role' => 'user']); // Role user biasa
        $response = $this->actingAs($user)->get(route('admin.categories.index'));
        
        // Tergantung middleware Anda, bisa 403 (Forbidden) atau 302 (Redirect)
        // Kita asumsikan middleware melempar 403 atau redirect
        $this->assertTrue(in_array($response->status(), [403, 302]));
    }

    public function test_admin_bisa_membuat_kategori()
    {
        $admin = $this->createAdmin();

        $response = $this->actingAs($admin)->post(route('admin.categories.store'), [
            'name' => 'Elektronik',
            'icon_class' => 'fa-laptop'
        ]);

        $response->assertRedirect();
        
        $this->assertDatabaseHas('categories', [
            'name' => 'Elektronik',
            'slug' => 'elektronik',
            'icon_class' => 'fa-laptop'
        ]);
    }

    public function test_admin_bisa_update_kategori()
    {
        $admin = $this->createAdmin();
        $category = Category::factory()->create(['name' => 'Lama']);

        $response = $this->actingAs($admin)->put(route('admin.categories.update', $category->id), [
            'name' => 'Baru',
            'icon_class' => 'fa-edit'
        ]);

        $response->assertRedirect();
        
        $this->assertDatabaseHas('categories', [
            'id' => $category->id,
            'name' => 'Baru',
            'slug' => 'baru'
        ]);
    }

    public function test_admin_bisa_hapus_kategori_soft_delete()
    {
        $admin = $this->createAdmin();
        $category = Category::factory()->create();

        $response = $this->actingAs($admin)->delete(route('admin.categories.destroy', $category->id));

        $response->assertRedirect();
        
        // Cek Soft Delete
        $this->assertSoftDeleted('categories', ['id' => $category->id]);
    }

    public function test_tidak_bisa_hapus_kategori_jika_sedang_dipakai_service()
    {
        $admin = $this->createAdmin();
        $category = Category::factory()->create();
        
        // Buat service yang menggunakan kategori ini
        Service::factory()->create([
            'category_id' => $category->id,
            'user_id' => $admin->id // pinjam id admin buat owner service biar cepat
        ]);

        $response = $this->actingAs($admin)->delete(route('admin.categories.destroy', $category->id));

        // Harus gagal hapus (Redirect back with error)
        // Data harus masih ada (Not Soft Deleted)
        $this->assertDatabaseHas('categories', [
            'id' => $category->id,
            'deleted_at' => null
        ]);
    }

    public function test_admin_bisa_restore_kategori()
    {
        $admin = $this->createAdmin();
        // Kategori dalam tong sampah
        $category = Category::factory()->create(['deleted_at' => now()]);

        $response = $this->actingAs($admin)->post(route('admin.categories.restore', $category->id));

        $response->assertRedirect();
        
        $this->assertNotSoftDeleted('categories', ['id' => $category->id]);
    }
}