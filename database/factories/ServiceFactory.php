<?php

namespace Database\Factories;

use App\Models\Category;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

class ServiceFactory extends Factory
{
    public function definition(): array
    {
        $title = $this->faker->sentence(3);
        return [
            'user_id' => User::factory(), // Ini penting! Auto-create user provider
            'category_id' => Category::factory(), // Ini penting! Auto-create kategori
            'title' => $title,
            'slug' => Str::slug($title),
            'description' => $this->faker->paragraph(),
            'price_min' => 50000,
            'price_max' => 100000,
            'location' => 'Bandung',
            'latitude' => -6.9175,
            'longitude' => 107.6191,
            'rating_avg' => 0,
            'status' => 'active',
        ];
    }
}