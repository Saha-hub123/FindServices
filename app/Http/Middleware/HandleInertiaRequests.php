<?php

namespace App\Http\Middleware;

use Illuminate\Http\Request;
use Inertia\Middleware;
use App\Models\Chat;

class HandleInertiaRequests extends Middleware
{
    /**
     * The root template that is loaded on the first page visit.
     *
     * @var string
     */
    protected $rootView = 'app';

    /**
     * Determine the current asset version.
     */
    public function version(Request $request): ?string
    {
        return parent::version($request);
    }

    /**
     * Define the props that are shared by default.
     *
     * @return array<string, mixed>
     */
    public function share(Request $request): array
    {
        // 1. Ambil data session
        // Kita gabungkan berbagai kemungkinan key ('message', 'success', 'status') jadi satu logika
        $message = $request->session()->get('message') ?? $request->session()->get('success') ?? $request->session()->get('status');
        $error = $request->session()->get('error') ?? $request->session()->get('danger');
        $warning = $request->session()->get('warning');

        $flashData = [];

        // 2. Format ulang menjadi object dengan TIMESTAMP
        if ($message) {
            $flashData = [
                'type' => 'success',
                'message' => $message,
                'timestamp' => microtime(true), // <--- KUNCI ANTI-LOOPING
            ];
        } elseif ($error) {
            $flashData = [
                'type' => 'error',
                'message' => $error,
                'timestamp' => microtime(true),
            ];
        } elseif ($warning) {
            $flashData = [
                'type' => 'warning',
                'message' => $warning,
                'timestamp' => microtime(true),
            ];
        }

        return [
            ...parent::share($request),
            'auth' => [
                'user' => $request->user(),
                // Notifikasi Header
                'notifications' => $request->user() 
                    ? $request->user()->notifications()->latest()->take(6)->get() 
                    : [],
                'unread_notifications_count' => $request->user() 
                    ? $request->user()->unreadNotifications()->count() 
                    : 0,
            ],

            // --- TAMBAHKAN INI ---
            // Hitung laporan pending KHUSUS jika user yang login adalah ADMIN
            'pending_reports_count' => ($request->user() && $request->user()->role === 'admin') 
                ? \App\Models\Report::where('status', 'pending')->count() 
                : 0,
                
            // 3. Kirim Flash Data yang sudah ada timestamp-nya
            'flash' => $flashData,
            
            // --- TAMBAHAN BARU ---
            // Hitung semua pesan dimana saya sebagai penerima DAN belum dibaca
            'unread_global_count' => $request->user() 
                ? Chat::where('receiver_id', $request->user()->id)
                    ->where('is_read', false)
                    ->count() 
                : 0,
            // ---------------------
        ];
    }
    
    
}
