<?php

use App\Http\Controllers\ProfileController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\ServiceController;
use App\Http\Controllers\MarketplaceController;
use App\Http\Controllers\BookingController;
use App\Http\Controllers\ChatController;
use Illuminate\Support\Facades\Broadcast;
use App\Http\Controllers\SearchController;

// Route::get('/', function () {
//     return Inertia::render('Welcome', [
//         'canLogin' => Route::has('login'),
//         'canRegister' => Route::has('register'),
//         'laravelVersion' => Application::VERSION,
//         'phpVersion' => PHP_VERSION,
//     ]);
// });

// 1. Route ROOT ('/') diarahkan ke DashboardController TANPA middleware auth
Route::get('/', [DashboardController::class, 'index'])->name('welcome');

Route::get('/dashboard', [DashboardController::class, 'index']) 
    ->middleware(['auth', 'verified'])
    ->name('dashboard');
// ------------------------------
// ...

Route::get('/marketplace', [MarketplaceController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('marketplace.index');

Route::middleware('auth')->group(function () {
    // Tampilan Visual Profil (Instagram Style)
    Route::get('/profile/me', [ProfileController::class, 'index'])->name('profile.index');
    Route::get('/user/{user}', [ProfileController::class, 'show'])->name('profile.show');

});

Route::middleware('auth')->group(function () {
    // Route Booking Index & Show
    Route::get('/bookings', [BookingController::class, 'index'])->name('bookings.index');
    Route::get('/bookings/{booking}', [BookingController::class, 'show'])->name('bookings.show');
    Route::get('/booking/create', [BookingController::class, 'create'])->name('bookings.create');
    Route::post('/booking', [BookingController::class, 'store'])->name('bookings.store');
    Route::patch('/bookings/{booking}/status', [BookingController::class, 'updateStatus'])->name('bookings.update-status');
    Route::post('/bookings/{booking}/review', [BookingController::class, 'storeReview'])->name('bookings.review');
    Route::get('/bookings/{booking}/edit', [BookingController::class, 'edit'])->name('bookings.edit');
    Route::put('/bookings/{booking}', [BookingController::class, 'update'])->name('bookings.update');
});

Route::middleware('auth')->group(function () {
    // Route Chat
    Route::get('/chats', [ChatController::class, 'index'])->name('chats.index');
    Route::post('/chats', [ChatController::class, 'store'])->name('chats.store');
    Route::post('/chats/mark-as-read', [ChatController::class, 'markAsRead'])->name('chats.markAsRead');
    Route::delete('/chats/{chat}', [ChatController::class, 'destroy'])->name('chats.destroy');
});



Route::middleware('auth')->group(function () {
    // Profil Visual
    Route::get('/profile/edit', [ProfileController::class, 'edit'])->name('profile.edit');
    
    // Pengaturan Akun (Baru)
    Route::get('/profile/settings', [ProfileController::class, 'settings'])->name('profile.settings');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
    Route::get('/service/{service}', [ServiceController::class, 'show'])
        ->name('service.show');
    Route::get('/services/create', [ServiceController::class, 'create'])->name('services.create');
    Route::post('/services', [ServiceController::class, 'store'])->name('services.store');
    Route::get('/services/{service}/edit', [ServiceController::class, 'edit'])->name('services.edit');
    Route::put('/services/{service}', [ServiceController::class, 'update'])->name('services.update'); // Pakai PUT
    Route::delete('/services/{service}', [ServiceController::class, 'destroy'])->name('services.destroy');
    // Route Sampah
    Route::get('/services/trash', [ServiceController::class, 'trash'])->name('services.trash');
    
    // Route Restore (Gunakan method POST atau PUT/PATCH)
    Route::post('/services/{id}/restore', [ServiceController::class, 'restore'])->name('services.restore');
    
    // Route Force Delete
    Route::delete('/services/{id}/force', [ServiceController::class, 'forceDelete'])->name('services.force-delete');
    // Nanti tambahkan route service di sini
    // Route::resource('services', ServiceController::class);
    Route::get('/search', [SearchController::class, 'index'])->name('search.index');
});

// Route::get('/dashboard', function () {
//     return Inertia::render('Dashboard');
// })->middleware(['auth', 'verified'])->name('dashboard');

// Route::middleware('auth')->group(function () {
//     Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
//     Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
//     Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
// });

Broadcast::channel('chat.{userId}', function ($user, $userId) {
    // Izinkan jika ID user yang login SAMA DENGAN ID channel yang dituju
    return (int) $user->id === (int) $userId;
});

require __DIR__.'/auth.php';
