<?php

namespace Tests\Feature;

use App\Models\User;
use App\Models\Service;
use App\Models\Category;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class SearchControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_halaman_search_bisa_diakses()
    {
        $response = $this->get(route('search.index'));
        $response->assertStatus(200);
    }

    public function test_search_menemukan_service_dan_user()
    {
        $user = User::factory()->create(['name' => 'Budi Tukang']);
        $category = Category::factory()->create();
        
        Service::factory()->create([
            'title' => 'Jasa Perbaikan Atap',
            'description' => 'Ahli bocor',
            'user_id' => $user->id,
            'category_id' => $category->id,
            'status' => 'active'
        ]);

        // Cari kata kunci "Bocor" (ada di deskripsi jasa)
        $response = $this->get(route('search.index', ['q' => 'Bocor']));

        $response->assertStatus(200);
        
        // Pastikan Jasa ditemukan
        $response->assertInertia(fn ($page) => $page
            ->component('Search/Index')
            ->has('services.data', 1)
            ->where('services.data.0.title', 'Jasa Perbaikan Atap')
        );

        // Cari kata kunci "Budi" (nama user)
        $responseUser = $this->get(route('search.index', ['q' => 'Budi']));
        
        // Pastikan User ditemukan
        $responseUser->assertInertia(fn ($page) => $page
            ->has('users.data', 1)
            ->where('users.data.0.name', 'Budi Tukang')
        );
    }
    
    public function test_search_load_more_json()
    {
        $response = $this->getJson(route('search.index', ['q' => 'test']));
        $response->assertStatus(200)
                 ->assertJsonStructure(['services', 'users']);
    }
}