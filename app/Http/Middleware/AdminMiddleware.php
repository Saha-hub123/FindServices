<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AdminMiddleware
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next)
    {
        // 1. Jika user login DAN role-nya admin, izinkan lewat
        if (auth()->check() && auth()->user()->role === 'admin') {
            return $next($request);
        }

        // --- TAMBAHAN KODE PENCEGAH LOOP ---
        // 2. Jika user SUDAH berada di halaman utama ('/'), jangan redirect lagi ke '/'
        // Biarkan request diteruskan (agar halaman Welcome bisa tampil)
        if ($request->is('/')) {
            return $next($request);
        }
        // ------------------------------------

        // 3. Jika bukan admin dan bukan di halaman utama, lempar ke '/'
        return redirect('/')->with('error', 'Anda tidak memiliki akses admin.');
    }
}