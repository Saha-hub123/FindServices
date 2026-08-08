<?php

namespace App\Http\Controllers;

use App\Models\Service;
use App\Models\User;
use Illuminate\Http\Request;
use Inertia\Inertia;

class SearchController extends Controller
{
    public function index(Request $request)
    {
        $query = $request->input('q');

        // Jika tidak ada query, kembalikan array kosong
        if (!$query) {
            return Inertia::render('Search/Index', [
                'services' => [],
                'users' => [],
                'query' => ''
            ]);
        }

        // 1. Cari Jasa (Hanya yang Active)
        $services = Service::where('status', 'active')
            ->where(function($q) use ($query) {
                $q->where('title', 'like', "%{$query}%")
                  ->orWhere('description', 'like', "%{$query}%");
            })
            ->with(['user', 'category', 'galleries'])
            ->withCount('reviews')
            ->latest()
            ->paginate(12, ['*'], 'services_page') // <--- Named Pagination
            ->withQueryString();

        // 2. Cari User (Provider)
        $users = User::where('name', 'like', "%{$query}%")
            ->orWhere('email', 'like', "%{$query}%")
            ->withCount('services') // Hitung punya jasa berapa
            ->paginate(12, ['*'], 'users_page') // <--- Named Pagination
            ->withQueryString();

        // [LOGIKA LOAD MORE]
        // Jika request JSON (dari Axios), kirim data array
        if ($request->wantsJson()) {
            return response()->json([
                'services' => $services,
                'users' => $users
            ]);
        }

        return Inertia::render('Search/Index', [
            'services' => $services,
            'users' => $users,
            'query' => $query
        ]);
    }
}