<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase; // Gunakan ini biar bersih
use Tests\TestCase;

class ExampleTest extends TestCase
{
    use RefreshDatabase; // Tambahkan RefreshDatabase

    public function test_the_application_returns_a_successful_response(): void
    {
        $response = $this->get('/');
        $response->assertStatus(200);
    }
}