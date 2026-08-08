<?php
namespace Database\Factories;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

class ReportFactory extends Factory
{
    public function definition(): array
    {
        return [
            'user_id' => User::factory(),
            'subject' => $this->faker->sentence(3),
            'description' => $this->faker->paragraph(),
            'status' => 'pending',
            'proof_images' => [],
        ];
    }
}