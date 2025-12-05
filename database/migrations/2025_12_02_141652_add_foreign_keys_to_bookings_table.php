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
        Schema::table('bookings', function (Blueprint $table) {
            $table->foreign(['service_id'], 'bookings_ibfk_1')->references(['id'])->on('services')->onUpdate('no action')->onDelete('cascade');
            $table->foreign(['customer_id'], 'bookings_ibfk_2')->references(['id'])->on('users')->onUpdate('no action')->onDelete('cascade');
            $table->foreign(['provider_id'], 'bookings_ibfk_3')->references(['id'])->on('users')->onUpdate('no action')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('bookings', function (Blueprint $table) {
            $table->dropForeign('bookings_ibfk_1');
            $table->dropForeign('bookings_ibfk_2');
            $table->dropForeign('bookings_ibfk_3');
        });
    }
};
