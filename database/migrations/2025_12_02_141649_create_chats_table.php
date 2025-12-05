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
        Schema::create('chats', function (Blueprint $table) {
            $table->increments('id');
            $table->unsignedInteger('reply_to_id')->nullable()->index('chats_reply_to_id_foreign');
            $table->unsignedBigInteger('sender_id')->index('sender_id');
            $table->unsignedBigInteger('receiver_id')->index('receiver_id');
            $table->unsignedInteger('booking_id')->nullable()->index('booking_id');
            $table->unsignedInteger('service_id')->nullable()->index('service_id');
            $table->text('message')->nullable();
            $table->boolean('is_read')->nullable()->default(false);
            $table->timestamps();
            $table->softDeletes();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('chats');
    }
};
