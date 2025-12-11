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
use Illuminate\Support\Facades\Storage; // Jangan lupa import
use App\Models\Review; // Import Review

class ProfileController extends Controller
{
    /**
     * Display the user's profile form.
     */
    // 1. HALAMAN EDIT PROFIL (Visual: Avatar, Bio, Nama)
    public function edit(Request $request)
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
        $user = $request->user();
        $data = $request->validated();

        // 1. Handle Avatar Upload
        if ($request->hasFile('avatar')) {
            // Hapus avatar lama jika ada (dan bukan default/ui-avatar)
            if ($user->avatar) {
                Storage::disk('public')->delete($user->avatar);
            }
            // Simpan avatar baru
            $data['avatar'] = $request->file('avatar')->store('avatars', 'public');
        } 
        else {
            // [PENTING] Jika tidak ada file baru, HAPUS key 'avatar' dari array $data
            // Agar data lama di database TIDAK tertimpa dengan NULL
            unset($data['avatar']);
        }

        // 2. Isi Model dengan Data Baru (Tanpa merusak avatar lama)
        $user->fill($data);

        // 3. Cek Perubahan Email
        if ($user->isDirty('email')) {
            $user->email_verified_at = null;
        }

        $user->save();

        return Redirect::route('profile.index')->with('message', 'Profil berhasil diperbarui.');
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
        
        // 2. Ambil Review yang DITERIMA (Untuk evaluasi)
        $reviews = \App\Models\Review::whereHas('service', function($q) use ($user) {
                $q->where('user_id', $user->id);
            })
            ->with(['user', 'service']) // Load pembeli & nama jasa
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
            'total_reviews' => $reviews->count()
        ];

        // 3. [BARU] Review DIBERIKAN (Kita ke Orang lain)
        $givenReviews = \App\Models\Review::where('user_id', $user->id)
            ->with(['service.user', 'service.galleries']) // Load Service & Providernya
            ->latest()
            ->get();

        return Inertia::render('Profile/Index', [
            'mustVerifyEmail' => $user instanceof MustVerifyEmail,
            'status' => session('status'),
            'services' => $services,
            'reviews' => $reviews,
            'givenReviews' => $givenReviews, // Keluar (Baru)
            'stats' => $stats,
            'auth_user' => $user // Kirim data user lengkap (bio, avatar, dll)
        ]);
    }

    public function show(User $user)
    {
        if (Auth::id() === $user->id) {
            return redirect()->route('profile.index');
        }

        // 1. Ambil Jasa (Existing)
        $services = \App\Models\Service::where('user_id', $user->id)
            ->where('status', 'active')
            ->with(['category', 'galleries', 'user'])
            ->withCount('reviews')
            ->latest()
            ->get();

        // 2. [BARU] Ambil Review yang DITERIMA user ini
        // Caranya: Cari review dimana service_id-nya adalah milik user ini
        $reviews = Review::whereHas('service', function($q) use ($user) {
                $q->where('user_id', $user->id);
            })
            ->with(['user', 'service']) // Load siapa yang komen & jasa apa
            ->latest()
            ->take(20) // Ambil 20 review terakhir saja agar tidak berat
            ->get();

        // 3. Statistik (Existing)
        $stats = [
            'services_count' => $services->count(),
            'orders_completed' => \App\Models\Booking::where('provider_id', $user->id)
                                        ->where('status', 'completed')
                                        ->count(),
            'rating_avg' => $services->avg('rating_avg') ?? 0,
            'reviews_count' => $reviews->count() // Tambahan info jumlah review
        ];

        return Inertia::render('Profile/Show', [
            'user' => $user,
            'services' => $services,
            'reviews' => $reviews, // Kirim ke frontend
            'stats' => $stats,
            'auth_id' => Auth::id()
        ]);
    }

    // 2. HALAMAN PENGATURAN AKUN (Security: Email, Phone, Password)
    public function settings(Request $request)
    {
        return Inertia::render('Profile/Settings', [
            'mustVerifyEmail' => $request->user() instanceof MustVerifyEmail,
            'status' => session('status'),
        ]);
    }
}
