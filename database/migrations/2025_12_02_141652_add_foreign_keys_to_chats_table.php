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
        Schema::table('chats', function (Blueprint $table) {
            $table->foreign(['sender_id'], 'chats_ibfk_1')->references(['id'])->on('users')->onUpdate('no action')->onDelete('cascade');
            $table->foreign(['receiver_id'], 'chats_ibfk_2')->references(['id'])->on('users')->onUpdate('no action')->onDelete('cascade');
            $table->foreign(['booking_id'], 'chats_ibfk_3')->references(['id'])->on('bookings')->onUpdate('no action')->onDelete('set null');
            $table->foreign(['service_id'], 'chats_ibfk_4')->references(['id'])->on('services')->onUpdate('no action')->onDelete('set null');
            $table->foreign(['reply_to_id'])->references(['id'])->on('chats')->onUpdate('no action')->onDelete('set null');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('chats', function (Blueprint $table) {
            $table->dropForeign('chats_ibfk_1');
            $table->dropForeign('chats_ibfk_2');
            $table->dropForeign('chats_ibfk_3');
            $table->dropForeign('chats_ibfk_4');
            $table->dropForeign('chats_reply_to_id_foreign');
        });
    }
};
