<?php

namespace App\Http\Controllers;

use App\Models\Service;
use App\Models\Category;
use Illuminate\Http\Request;
use Inertia\Inertia;

class MarketplaceController extends Controller
{
    public function index(Request $request)
    {
        $query = Service::query()->with(['user', 'category', 'galleries']);

        // Filter Pencarian (Search)
        if ($request->search) {
            $query->where('title', 'like', '%' . $request->search . '%')
                  ->orWhere('description', 'like', '%' . $request->search . '%');
        }

        // Filter Kategori
        if ($request->category) {
            $query->whereHas('category', function($q) use ($request) {
                $q->where('slug', $request->category); // Pastikan tabel categories punya kolom slug
            });
        }

        // Ambil data (Active only), paginate 12 per halaman
        $services = $query->where('status', 'active')
                          ->latest()
                          ->paginate(12)
                          ->withQueryString();

        $categories = Category::all();

        return Inertia::render('Marketplace/Index', [
            'services' => $services,
            'categories' => $categories,
            'filters' => $request->only(['search', 'category'])
        ]);
    }
}