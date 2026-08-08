<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Category;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Illuminate\Support\Str;

class CategoryController extends Controller
{
    public function index(Request $request)
    {
        // PERBAIKAN: Tambahkan withTrashed() agar data terhapus tetap terambil
        $query = Category::withTrashed(); 

        if ($request->q) {
            $query->where('name', 'like', '%' . $request->q . '%');
        }

        // Ambil data
        $categories = $query->withCount('services')
            ->latest()
            ->orderBy('deleted_at', 'asc') // Yang aktif (null) di atas, yang terhapus (ada tanggal) di bawah
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('Admin/Categories/Index', [
            'categories' => $categories,
            'filters' => $request->only(['q'])
        ]);
    }

    public function store(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:50|unique:categories,name',
            // Validasi icon class
            'icon_class' => 'required|string|max:255',
        ]);

        Category::create([
            'name' => $request->name,
            'slug' => Str::slug($request->name),
            'icon_class' => $request->icon_class, // Simpan data
        ]);

        return back()->with('message', 'Kategori berhasil dibuat.');
    }

    // 1. Ubah parameter dari (Category $category) menjadi ($id)
    public function update(Request $request, $id) 
    {
        // 2. Cari data secara manual, izinkan pencarian data yang sudah dihapus (withTrashed)
        $category = Category::withTrashed()->findOrFail($id);

        $request->validate([
            // Validasi tetap sama
            'name' => 'required|string|max:50|unique:categories,name,' . $category->id,
            'icon_class' => 'required|string|max:255',
        ]);

        $category->update([
            'name' => $request->name,
            'slug' => \Illuminate\Support\Str::slug($request->name),
            'icon_class' => $request->icon_class,
        ]);

        return back()->with('message', 'Kategori berhasil diperbarui.');
    }

    public function destroy($id) // Terima ID saja agar bisa handle soft delete
    {
        $category = Category::findOrFail($id);
        
        if ($category->services()->count() > 0) {
            return back()->with('error', 'Gagal hapus: Kategori masih digunakan oleh Jasa.');
        }

        $category->delete(); // Soft Delete
        return back()->with('message', 'Kategori dipindahkan ke sampah.');
    }
    public function restore($id)
    {
        $category = Category::withTrashed()->findOrFail($id);
        $category->restore(); // Kembalikan data
        return back()->with('message', 'Kategori berhasil dipulihkan.');
    }
}
