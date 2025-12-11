<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class UpdateCategoriesSeeder extends Seeder
{
    public function run()
    {
        // 1. Update 3 Kategori Awal (Edit yang sudah ada)
        $updates = [
            1 => ['name' => 'Service AC & Elektronik', 'slug' => 'service-ac-elektronik'],
            2 => ['name' => 'Pertukangan & Renovasi', 'slug' => 'pertukangan-renovasi'],
            3 => ['name' => 'Kebersihan & Cleaning', 'slug' => 'kebersihan-cleaning'],
        ];

        foreach ($updates as $id => $data) {
            DB::table('categories')->where('id', $id)->update([
                'name' => $data['name'],
                'slug' => $data['slug'],
                'updated_at' => Carbon::now(),
            ]);
        }

        // 2. Tambahkan Sisanya (Insert Baru)
        $newCategories = [
            ['name' => 'Otomotif & Bengkel', 'slug' => 'otomotif-bengkel'],
            ['name' => 'Kecantikan & Salon', 'slug' => 'kecantikan-salon'],
            ['name' => 'Pijat & Kesehatan', 'slug' => 'pijat-kesehatan'],
            ['name' => 'Desain & Kreatif', 'slug' => 'desain-kreatif'],
            ['name' => 'IT & Komputer', 'slug' => 'it-komputer'],
            ['name' => 'Pendidikan & Les', 'slug' => 'pendidikan-les'],
            ['name' => 'Fotografi & Video', 'slug' => 'fotografi-video'],
            ['name' => 'Angkutan & Pindahan', 'slug' => 'angkutan-pindahan'],
            ['name' => 'Lain-lain', 'slug' => 'lain-lain'],
        ];

        foreach ($newCategories as $cat) {
            // Cek dulu agar tidak duplikat
            if (!DB::table('categories')->where('slug', $cat['slug'])->exists()) {
                DB::table('categories')->insert([
                    'name' => $cat['name'],
                    'slug' => $cat['slug'],
                    'created_at' => Carbon::now(),
                    'updated_at' => Carbon::now(),
                ]);
            }
        }
    }
}