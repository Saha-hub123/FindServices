<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up()
    {
        Schema::table('reports', function (Blueprint $table) {
            // Hapus kolom lama (jika datanya masih dummy/sedikit)
            // Jika data penting, Anda perlu script migrasi data, tapi untuk dev kita drop saja
            $table->dropColumn('proof_image'); 
            
            // Ganti dengan JSON untuk menampung banyak file
            $table->json('proof_images')->nullable()->after('description');
            
            // Soft Deletes
            $table->softDeletes();
        });
    }

    public function down()
    {
        Schema::table('reports', function (Blueprint $table) {
            $table->string('proof_image')->nullable();
            $table->dropColumn('proof_images');
            $table->dropSoftDeletes();
        });
    }
};
