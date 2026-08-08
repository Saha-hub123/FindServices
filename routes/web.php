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
use App\Http\Controllers\NotificationController;
use App\Http\Controllers\Admin\AdminDashboardController;
use App\Http\Controllers\Admin\CategoryController;
use App\Http\Controllers\Admin\ReportController;
use App\Http\Middleware\AdminMiddleware;
use \App\Http\Controllers\UserReportController;


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
    ->name('dashboard');
// ------------------------------
// ...

Route::get('/marketplace', [MarketplaceController::class, 'index'])
    ->name('marketplace.index');
Route::get('/service/{service}', [ServiceController::class, 'show'])
    ->name('service.show');
Route::get('/search', [SearchController::class, 'index'])->name('search.index');
    
Route::get('/user/{user}', [ProfileController::class, 'show'])->name('profile.show');

Route::middleware('auth')->group(function () {
    // Tampilan Visual Profil (Instagram Style)
    Route::get('/profile/me', [ProfileController::class, 'index'])->name('profile.index');
    Route::get('/reports', [UserReportController::class, 'index'])->name('user.reports.index');
    Route::post('/reports', [UserReportController::class, 'store'])->name('user.reports.store');
    // Tambahan Route Edit & Delete
    Route::post('/reports/{report}', [UserReportController::class, 'update'])->name('user.reports.update'); // Pakai POST untuk update file (method spoofing inertia)
    Route::delete('/reports/{report}', [UserReportController::class, 'destroy'])->name('user.reports.destroy');
});

Route::middleware('auth')->group(function () {
    // Route Booking Index & Show
    Route::get('/bookings', [BookingController::class, 'index'])->name('bookings.index');
    Route::get('/bookings/{booking}', [BookingController::class, 'show'])->name('bookings.show');
    Route::get('/booking/create', [BookingController::class, 'create'])->name('bookings.create');
    Route::post('/booking', [BookingController::class, 'store'])->name('bookings.store');
    Route::patch('/bookings/{booking}/status', [BookingController::class, 'updateStatus'])->name('bookings.update-status');
    Route::post('/bookings/{booking}/review', [BookingController::class, 'storeReview'])->name('bookings.review');
    Route::delete('/reviews/{review}', [BookingController::class, 'destroyReview'])->name('reviews.destroy');
    // Tambahkan route ini di bawah route store/destroy review yang sudah ada
    Route::post('/reviews/{review}', [App\Http\Controllers\BookingController::class, 'updateReview'])->name('reviews.update');
    Route::get('/bookings/{booking}/edit', [BookingController::class, 'edit'])->name('bookings.edit');
    Route::put('/bookings/{booking}', [BookingController::class, 'update'])->name('bookings.update');
    // Route untuk Request Token Midtrans
    Route::post('/bookings/{booking}/pay', [BookingController::class, 'pay'])->name('bookings.pay');
    Route::post('/bookings/{booking}/confirm-payment', [BookingController::class, 'confirmPayment'])->name('bookings.confirm-payment');
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
    Route::patch('/services/{service}/toggle-status', [ServiceController::class, 'toggleStatus'])->name('services.toggle-status');
    // Route Notifikasi
    Route::prefix('notifications')->name('notifications.')->group(function () {
        Route::get('/', [NotificationController::class, 'index'])->name('index'); // Halaman Lihat Semua
        Route::post('/read-all', [NotificationController::class, 'markAllRead'])->name('readAll'); // Tandai Semua Baca
        Route::post('/{id}/read', [NotificationController::class, 'markAsRead'])->name('read'); // Tandai Satu Baca
        Route::delete('/{id}', [NotificationController::class, 'destroy'])->name('destroy'); // Hapus
    });
});

// Group Route Admin
Route::middleware(['auth', AdminMiddleware::class])->prefix('admin')->name('admin.')->group(function () {
    
    // Dashboard
    Route::get('/dashboard', [AdminDashboardController::class, 'index'])->name('dashboard');

    // Laporan
    Route::get('reports', [ReportController::class, 'index'])->name('reports.index');
    // Kita gunakan PATCH karena hanya update 1 kolom (status)
    Route::patch('reports/{report}', [ReportController::class, 'updateStatus'])->name('reports.update');

    Route::post('categories/{id}/restore', [CategoryController::class, 'restore'])->name('categories.restore');
    // Route Restore Laporan
    Route::post('reports/{id}/restore', [ReportController::class, 'restore'])->name('reports.restore');
    // Kategori (CRUD + Restore)
    Route::resource('categories', CategoryController::class)->except(['show']);

    
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
