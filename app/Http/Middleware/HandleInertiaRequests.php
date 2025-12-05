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
        return [
            ...parent::share($request),
            'auth' => [
                'user' => $request->user(),
            ],
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
