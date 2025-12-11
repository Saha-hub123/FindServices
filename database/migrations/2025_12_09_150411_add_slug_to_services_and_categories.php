<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

return new class extends Migration
{
    public function up()
    {
        // 1. Tambah kolom slug di Services
        Schema::table('services', function (Blueprint $table) {
            $table->string('slug')->nullable()->after('title'); 
        });

        // 2. Tambah kolom slug di Categories
        Schema::table('categories', function (Blueprint $table) {
            $table->string('slug')->nullable()->after('name');
        });

        // 3. AUTO-FILL DATA LAMA (PENTING!)
        // Kita loop semua data yang ada, lalu buat slug-nya

        // Isi Service Slugs
        $services = DB::table('services')->get();
        foreach ($services as $s) {
            // Format: judul-service-idunik (agar tidak bentrok)
            $slug = Str::slug($s->title) . '-' . $s->id;
            DB::table('services')->where('id', $s->id)->update(['slug' => $slug]);
        }

        // Isi Category Slugs
        $categories = DB::table('categories')->get();
        foreach ($categories as $c) {
            $slug = Str::slug($c->name);
            DB::table('categories')->where('id', $c->id)->update(['slug' => $slug]);
        }

        // 4. Ubah jadi Unique & Not Null (Setelah data terisi)
        Schema::table('services', function (Blueprint $table) {
            $table->string('slug')->nullable(false)->unique()->change();
        });
        Schema::table('categories', function (Blueprint $table) {
            $table->string('slug')->nullable(false)->unique()->change();
        });
    }

    public function down()
    {
        Schema::table('services', function (Blueprint $table) { $table->dropColumn('slug'); });
        Schema::table('categories', function (Blueprint $table) { $table->dropColumn('slug'); });
    }
};