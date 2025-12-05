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
        Schema::create('services', function (Blueprint $table) {
            $table->increments('id');
            $table->unsignedBigInteger('user_id')->index('user_id');
            $table->unsignedInteger('category_id')->index('category_id');
            $table->string('title', 150);
            $table->text('description')->nullable();
            $table->decimal('price_min', 12);
            $table->decimal('price_max', 12);
            $table->text('location')->nullable();
            $table->decimal('latitude', 10, 8)->nullable();
            $table->decimal('longitude', 11, 8)->nullable();
            $table->float('rating_avg')->default(0);
            $table->enum('status', ['active', 'inactive', 'pending'])->nullable()->default('pending');
            $table->timestamps();
            $table->softDeletes();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('services');
    }
};
