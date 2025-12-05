<?php

namespace App\Http\Controllers;

use App\Http\Requests\ProfileUpdateRequest;
use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Redirect;
use Inertia\Inertia;
use Inertia\Response;
use App\Models\Service;
use App\Models\Booking;
use App\Models\User;

class ProfileController extends Controller
{
    /**
     * Display the user's profile form.
     */
    public function edit(Request $request): Response
    {
        return Inertia::render('Profile/Edit', [
            'mustVerifyEmail' => $request->user() instanceof MustVerifyEmail,
            'status' => session('status'),
        ]);
    }

    /**
     * Update the user's profile information.
     */
    public function update(ProfileUpdateRequest $request): RedirectResponse
    {
        $request->user()->fill($request->validated());

        if ($request->user()->isDirty('email')) {
            $request->user()->email_verified_at = null;
        }

        $request->user()->save();

        return Redirect::route('profile.edit');
    }

    /**
     * Delete the user's account.
     */
    public function destroy(Request $request): RedirectResponse
    {
        $request->validate([
            'password' => ['required', 'current_password'],
        ]);

        $user = $request->user();

        Auth::logout();

        $user->delete();

        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return Redirect::to('/');
    }

    public function index(Request $request)
    {
        $user = $request->user();

        // 1. Ambil Jasa milik user
        $services = Service::where('user_id', $user->id)
            ->with(['user','category', 'galleries']) // Load relasi gambar & kategori
            ->withCount('reviews') // Load jumlah review
            ->latest()
            ->get();

        // 2. Hitung Statistik untuk Header Profile
        $stats = [
            'services_count' => $services->count(),
            // Hitung berapa kali jasa user ini dipesan orang (Incoming Orders)
            'orders_completed' => Booking::where('provider_id', $user->id)
                                        ->where('status', 'completed')
                                        ->count(),
            // Total rating rata-rata (Opsional)
            'rating_avg' => $services->avg('rating_avg') ?? 0,
        ];

        return Inertia::render('Profile/Index', [
            'mustVerifyEmail' => $user instanceof MustVerifyEmail,
            'status' => session('status'),
            'services' => $services,
            'stats' => $stats,
            'auth_user' => $user // Kirim data user lengkap (bio, avatar, dll)
        ]);
    }

    public function show(User $user)
    {
        // Jika user melihat profilnya sendiri, redirect ke halaman 'My Profile' yang ada tombol editnya
        if (Auth::id() === $user->id) {
            return redirect()->route('profile.index');
        }

        // 1. Ambil Jasa milik user tersebut (HANYA YANG ACTIVE)
        $services = Service::where('user_id', $user->id)
            ->where('status', 'active') // Hanya tampilkan yang aktif
            ->with(['category', 'galleries', 'user']) // Load user untuk card
            ->withCount('reviews')
            ->latest()
            ->get();

        // 2. Hitung Statistik
        $stats = [
            'services_count' => $services->count(),
            'orders_completed' => \App\Models\Booking::where('provider_id', $user->id)
                                        ->where('status', 'completed')
                                        ->count(),
            'rating_avg' => $services->avg('rating_avg') ?? 0,
        ];

        return Inertia::render('Profile/Show', [
            'user' => $user, // Data user yang dilihat
            'services' => $services,
            'stats' => $stats,
            'auth_id' => Auth::id() // ID kita sendiri (untuk keperluan chat)
        ]);
    }
}
