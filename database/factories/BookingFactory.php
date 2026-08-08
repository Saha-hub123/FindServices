<?php

namespace Database\Factories;

use App\Models\Service;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

class BookingFactory extends Factory
{
    public function definition(): array
    {
        return [
            'service_id' => Service::factory(),
            'customer_id' => User::factory(),
            'provider_id' => User::factory(),
            'booking_date' => now()->addDays(3),
            'booking_time' => '10:00:00',
            'initial_price' => 50000,
            'admin_fee' => 2000,
            'final_price' => 52000,
            'location' => 'Jl. Test No. 1',
            'latitude' => -6.9175,
            'longitude' => 107.6191,
            'status' => 'pending',
            'payment_method' => 'manual',
            'payment_status' => 'unpaid',
            'notes' => 'Testing notes',
        ];
    }
}