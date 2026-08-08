<?php

namespace Tests\Feature;

use App\Models\Service;
use App\Models\User;
use App\Models\Category;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use Tests\TestCase;
use App\Models\Gallery; // <--- Jangan lupa import ini

class ServiceControllerTest extends TestCase
{
    use RefreshDatabase;

    // 1. TEST HALAMAN CREATE (Form Tambah Jasa)
    public function test_halaman_create_service_bisa_diakses()
    {
        $user = User::factory()->create();
        
        // Kita butuh kategori karena di form create biasanya ngeloop kategori
        Category::factory()->count(3)->create();

        $response = $this->actingAs($user)->get(route('services.create'));

        $response->assertStatus(200);
    }

    // 2. TEST STORE (Simpan Jasa Baru) - PERBAIKAN
    public function test_user_bisa_membuat_service_baru()
    {
        Storage::fake('public'); 

        $user = User::factory()->create();
        $category = Category::factory()->create();

        $serviceData = [
            'title' => 'Jasa Desain Logo Profesional',
            'category_id' => $category->id,
            'description' => 'Desain logo mantap cepat jadi.',
            'price_min' => 100000,
            'price_max' => 500000,
            'location' => 'Jakarta Selatan',
            'latitude' => -6.200000,
            'longitude' => 106.816666,
            'images' => [
                UploadedFile::fake()->image('logo1.jpg'),
                UploadedFile::fake()->image('logo2.jpg')
            ]
        ];

        $response = $this->actingAs($user)->post(route('services.store'), $serviceData);

        $response->assertRedirect(); 

        // PERBAIKAN: Hapus pengecekan 'slug' dan ubah status jadi 'active'
        $this->assertDatabaseHas('services', [
            'user_id' => $user->id,
            'title' => 'Jasa Desain Logo Profesional',
            // 'slug' => ... (JANGAN DICEK karena ada string random unik)
            'status' => 'active', // Sesuaikan dengan logika controller Anda
        ]);
        
        $this->assertDatabaseCount('galleries', 2);
    }

    // 3. TEST HALAMAN EDIT
    public function test_halaman_edit_service_bisa_diakses()
    {
        $user = User::factory()->create();
        // Buat service milik user tersebut
        $service = Service::factory()->create(['user_id' => $user->id]);

        // Gunakan Object $service agar route binding slug berjalan
        $response = $this->actingAs($user)->get(route('services.edit', $service));

        $response->assertStatus(200);
    }

    public function test_user_bisa_update_service_kompleks()
    {
        Storage::fake('public'); // Mock Storage

        $user = User::factory()->create();
        $category = Category::factory()->create();

        // 1. SETUP DATA AWAL
        // Buat service dengan judul lama
        $service = Service::factory()->create([
            'user_id' => $user->id,
            'category_id' => $category->id,
            'title' => 'Judul Lama',
            'slug' => 'judul-lama-xyz', // Slug awal
            'price_min' => 50000
        ]);

        // Buat 2 Gambar Galeri Lama (Fisik & DB)
        $oldImage1 = 'services/old1.jpg';
        $oldImage2 = 'services/old2.jpg';
        
        // Pura-pura file fisik ada
        Storage::disk('public')->put($oldImage1, 'konten gambar 1');
        Storage::disk('public')->put($oldImage2, 'konten gambar 2');

        $gallery1 = Gallery::create(['service_id' => $service->id, 'image' => $oldImage1]);
        $gallery2 = Gallery::create(['service_id' => $service->id, 'image' => $oldImage2]);

        // 2. SIAPKAN DATA UPDATE
        $updateData = [
            'title' => 'Judul Baru Revisi', // Judul berubah -> Slug HARUS berubah
            'category_id' => $category->id,
            'description' => 'Deskripsi baru lengkap.',
            'price_min' => 100000,
            'price_max' => 200000,
            'location' => 'Bandung Kota',
            'latitude' => -6.910,
            'longitude' => 107.610,
            
            // SKENARIO: Hapus Gallery 1, Pertahankan Gallery 2
            'deleted_gallery_ids' => [$gallery1->id],

            // SKENARIO: Tambah 1 Gambar Baru
            'new_images' => [
                UploadedFile::fake()->image('baru.jpg')
            ]
        ];

        // 3. EKSEKUSI
        $response = $this->actingAs($user)->put(route('services.update', $service), $updateData);

        // 4. ASSERTIONS (Pengecekan)

        // A. Cek Redirect & Pesan
        $response->assertRedirect(route('profile.index'));
        $response->assertSessionHas('message', 'Jasa berhasil diperbarui!');

        // B. Cek Data Utama Service
        $updatedService = $service->fresh(); // Reload data dari DB
        $this->assertEquals('Judul Baru Revisi', $updatedService->title);
        $this->assertEquals(100000, $updatedService->price_min);
        
        // Cek Slug Berubah (Karena judul ganti)
        // Karena controller pakai Str::random(5), kita cek prefix-nya saja
        $this->assertStringStartsWith('judul-baru-revisi', $updatedService->slug);
        $this->assertNotEquals('judul-lama-xyz', $updatedService->slug);

        // C. Cek Galeri (Database)
        // Gallery 1 harus hilang
        $this->assertDatabaseMissing('galleries', ['id' => $gallery1->id]);
        // Gallery 2 harus tetap ada
        $this->assertDatabaseHas('galleries', ['id' => $gallery2->id]);
        
        // Total galeri harusnya 2 (1 sisa lama + 1 baru)
        $this->assertEquals(2, $updatedService->galleries()->count());

        // D. Cek Storage (Fisik File)
        // File lama 1 harus terhapus
        Storage::disk('public')->assertMissing($oldImage1);
        // File lama 2 harus aman
        Storage::disk('public')->assertExists($oldImage2);
        
        // File baru harus ada (karena namanya random, kita asumsikan jika DB nambah, file nambah)
        // Tapi kita bisa cek apakah ada file baru di folder services/
        $filesInFolder = Storage::disk('public')->files('services');
        // Harusnya ada: old2.jpg + file baru (total >= 2)
        $this->assertGreaterThanOrEqual(2, count($filesInFolder));
    }

    // 5. TEST SOFT DELETE (Masuk ke Sampah)
    public function test_user_bisa_hapus_service_soft_delete()
    {
        $user = User::factory()->create();
        $service = Service::factory()->create(['user_id' => $user->id]);

        $response = $this->actingAs($user)->delete(route('services.destroy', $service));

        $response->assertRedirect();

        // Cek Soft Delete (Data masih ada di DB, tapi kolom deleted_at terisi)
        $this->assertSoftDeleted('services', [
            'id' => $service->id
        ]);
    }

    // 6. TEST TOGGLE STATUS (Active <-> Inactive)
    public function test_user_bisa_ganti_status_service()
    {
        $user = User::factory()->create();
        $service = Service::factory()->create([
            'user_id' => $user->id,
            'status' => 'active'
        ]);

        // Route: services.toggle-status (PATCH)
        $response = $this->actingAs($user)->patch(route('services.toggle-status', $service));

        $response->assertRedirect();

        // Cek apakah berubah jadi inactive
        $this->assertDatabaseHas('services', [
            'id' => $service->id,
            'status' => 'inactive'
        ]);
    }

    // 7. TEST HALAMAN SAMPAH (Trash)
    public function test_halaman_sampah_bisa_diakses()
    {
        $user = User::factory()->create();
        
        // Buat service yang sudah dihapus (soft deleted)
        Service::factory()->create(['user_id' => $user->id, 'deleted_at' => now()]);

        $response = $this->actingAs($user)->get(route('services.trash'));

        $response->assertStatus(200);
    }

    // 8. TEST RESTORE (Mengembalikan Data Sampah)
    public function test_user_bisa_restore_service()
    {
        $user = User::factory()->create();
        
        // Service status terhapus
        $service = Service::factory()->create(['user_id' => $user->id, 'deleted_at' => now()]);

        // Perhatikan route restore di web.php biasanya pakai {id}, bukan slug 
        // karena slug mungkin conflict atau tidak terbaca kalau soft deleted bindingnya belum diset withTrashed
        // Cek web.php: Route::post('/services/{id}/restore', ...)
        $response = $this->actingAs($user)->post(route('services.restore', $service->id));

        $response->assertRedirect();

        // Cek kolom deleted_at jadi NULL
        $this->assertNotSoftDeleted('services', [
            'id' => $service->id
        ]);
    }

    // 9. TEST FORCE DELETE (Hapus Permanen)
    public function test_user_bisa_force_delete_service()
    {
        $user = User::factory()->create();
        
        // Service di tong sampah
        $service = Service::factory()->create(['user_id' => $user->id, 'deleted_at' => now()]);

        // Cek web.php: Route::delete('/services/{id}/force', ...)
        $response = $this->actingAs($user)->delete(route('services.force-delete', $service->id));

        $response->assertRedirect();

        // Cek data HILANG TOTAL dari database
        $this->assertDatabaseMissing('services', [
            'id' => $service->id
        ]);
    }

    // TAMBAHAN: Test Detail Service + Hitung Booking Completed
    public function test_halaman_detail_service_memuat_data_relasi_dan_hitungan_booking()
    {
        $user = User::factory()->create();
        $provider = User::factory()->create();
        $category = Category::factory()->create();

        // 1. Buat Service
        $service = Service::factory()->create([
            'user_id' => $provider->id,
            'category_id' => $category->id,
            'slug' => 'jasa-test-detail'
        ]);

        // 2. Simulasi Booking:
        // A. Booking Selesai (Harus dihitung)
        \App\Models\Booking::factory()->create([
            'service_id' => $service->id,
            'status' => 'completed'
        ]);
        
        // B. Booking Pending (JANGAN dihitung)
        \App\Models\Booking::factory()->create([
            'service_id' => $service->id,
            'status' => 'pending'
        ]);

        // 3. Akses Halaman Show
        // Pastikan route 'service.show' ada di web.php
        $response = $this->actingAs($user)->get(route('service.show', $service));

        $response->assertStatus(200);

        // 4. Cek Data di Frontend (Inertia)
        $response->assertInertia(fn ($page) => $page
            ->component('Service/Show')
            ->where('service.id', $service->id)
            ->where('service.bookings_count', 1) // Hanya 1 yang completed
            ->has('service.user')     // Relasi user terload
            ->has('service.category') // Relasi category terload
            ->has('service.galleries')// Relasi galleries terload
            ->where('auth_user_id', $user->id)
        );
    }

    /**
     * TEST KEAMANAN: Cek Hak Akses
     */
    public function test_user_tidak_bisa_update_service_orang_lain()
    {
        $owner = User::factory()->create();
        $thief = User::factory()->create(); // User lain

        $service = Service::factory()->create(['user_id' => $owner->id]);

        $response = $this->actingAs($thief)->put(route('services.update', $service), [
            'title' => 'Hacked Title',
            'category_id' => 1,
            'description' => 'Hack',
            'price_min' => 1000,
            'price_max' => 2000,
            'location' => 'X',
            'latitude' => 0,
            'longitude' => 0,
        ]);

        $response->assertStatus(403); // Forbidden
    }
    
}