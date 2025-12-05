<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('bookings', function (Blueprint $table) {
            $table->increments('id');
            $table->unsignedInteger('service_id')->index('service_id');
            $table->unsignedBigInteger('customer_id')->index('customer_id');
            $table->unsignedBigInteger('provider_id')->index('provider_id');
            $table->date('booking_date');
            $table->time('booking_time')->nullable();
            $table->decimal('initial_price', 12);
            $table->decimal('final_price', 12)->nullable();
            $table->text('notes')->nullable();
            $table->string('location')->nullable();
            $table->decimal('latitude', 10, 8)->nullable();
            $table->decimal('longitude', 11, 8)->nullable();
            $table->enum('status', ['unpaid', 'pending', 'paid', 'confirmed', 'in_progress', 'waiting_completion', 'completed', 'cancelled', 'rejected'])->nullable()->default('pending');
            $table->string('payment_method')->default('manual');
            $table->timestamps();
            $table->softDeletes();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('bookings');
    }
};
