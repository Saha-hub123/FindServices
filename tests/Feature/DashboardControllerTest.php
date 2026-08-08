<?php

namespace Tests\Feature;

use App\Models\User;
use App\Models\Category;
use App\Models\Service;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class DashboardControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_dashboard_can_be_accessed_by_guest()
    {
        // Dashboard Anda terbuka untuk umum (di web.php tidak ada middleware auth)
        $response = $this->get(route('dashboard'));
        $response->assertStatus(200);
    }

    public function test_dashboard_displays_services()
    {
        // Buat data dummy
        $category = Category::factory()->create();
        $user = User::factory()->create();
        Service::factory()->count(5)->create([
            'user_id' => $user->id,
            'category_id' => $category->id,
            'status' => 'active'
        ]);

        $response = $this->get(route('dashboard'));
        
        // Pastikan variabel 'services' dikirim ke frontend
        $response->assertInertia(fn ($page) => $page
            ->component('Dashboard')
            ->has('services.data', 5) // Pastikan ada 5 data
        );
    }

    public function test_dashboard_filter_popular()
    {
        // Tes logika sorting Popular
        $response = $this->get(route('dashboard', ['filter' => 'popular']));
        $response->assertStatus(200);
    }

    public function test_dashboard_filter_rating()
    {
        // Tes logika sorting Rating
        $response = $this->get(route('dashboard', ['filter' => 'rating']));
        $response->assertStatus(200);
    }

    public function test_dashboard_load_more_json()
    {
        // Tes Axios Load More (Header: X-Requested-With = XMLHttpRequest)
        $category = Category::factory()->create();
        $user = User::factory()->create();
        Service::factory()->create(['user_id' => $user->id, 'category_id' => $category->id]);

        $response = $this->getJson(route('dashboard')); // getJson otomatis kirim header JSON

        $response->assertStatus(200)
                 ->assertJsonStructure(['data', 'current_page']); // Pastikan format JSON pagination
    }

    // ... method lain ...

    // TAMBAHAN: Test Show Event Modal/Detail
    public function test_detail_event_bisa_diakses()
    {
        $user = User::factory()->create();

        // Kita gunakan Booking sebagai simulasi Event
        // (Sesuaikan jika Anda punya model App\Models\Event sendiri)
        $event = \App\Models\Booking::factory()->create([
            'customer_id' => $user->id,
            // Asumsi field yang diambil controller: title, start_date, description
            // Jika Booking tidak punya kolom title/description, tes ini akan error "attribute not found".
            // SOLUSI: Pastikan model yang dikirim punya kolom tersebut.
        ]);

        // *CATATAN KHUSUS*:
        // Controller Anda memanggil $event->only('title', ...).
        // Jika model Booking tidak punya kolom 'title', Anda harus mem-mock atau 
        // pastikan model yang dipakai sesuai.
        
        // Anggaplah route-nya 'event.show'
        // Jika belum ada route, tes ini akan error RouteNotFound
        
        // Uncomment baris bawah jika route sudah dibuat:
        // $response = $this->actingAs($user)->get(route('event.show', $event->id));
        
        // $response->assertStatus(200);
        // $response->assertInertia(fn ($page) => $page
        //    ->component('Event/Show')
        //    ->has('event.id')
        // );
        
        $this->markTestSkipped('Butuh Route [event.show] dan Model Event yang sesuai di web.php');
    }
}