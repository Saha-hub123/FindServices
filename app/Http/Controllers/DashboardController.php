<?php

namespace App\Http\Controllers;

use App\Models\Service;
use App\Models\Category;
use Illuminate\Http\Request;
use Inertia\Inertia;

class DashboardController extends Controller
{
    public function index()
    {
        // Ambil service yang statusnya 'active'
        // Eager load: user (penyedia), category, reviews, dan galleries
        $services = Service::with(['user', 'category', 'galleries'])
            ->withCount('reviews') // Hitung jumlah review
            ->where('status', 'active') 
            ->latest()
            ->paginate(10); // Gunakan pagination biar seperti infinite scroll nantinya

        $categories = Category::all();

        return Inertia::render('Dashboard', [
            'services' => $services,
            'categories' => $categories,
            'is_guest' => !auth()->check()
        ]);
    }

    public function show($event)
    {
        return Inertia::render('Event/Show', [
            'event' => $event->only(
                'id',
                'title',
                'start_date',
                'description',
            ),
        ]);
    }
}