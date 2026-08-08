<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Inertia\Inertia;

class NotificationController extends Controller
{
    /**
     * Menampilkan halaman daftar semua notifikasi.
     */
    public function index(Request $request)
    {
        // Ambil notifikasi dengan pagination (10 per load)
        $notifications = $request->user()
            ->notifications()
            ->latest()
            ->paginate(10); // Ubah angka sesuai kebutuhan

        // [TAMBAHAN PENTING] 
        // Jika request datang dari Axios (Load More), kirim JSON saja
        if ($request->wantsJson()) {
            return response()->json($notifications);
        }

        return Inertia::render('Notification/Index', [
            'notifications' => $notifications
        ]);
    }

    /**
     * Tandai satu notifikasi sebagai sudah dibaca.
     */
    public function markAsRead(Request $request, $id)
    {
        $notification = $request->user()
            ->notifications()
            ->where('id', $id)
            ->first();

        if ($notification) {
            $notification->markAsRead();
            
            // Jika ada link action di dalam data notifikasi, kita bisa redirect ke sana
            // Contoh: klik notif booking -> redirect ke booking.show
            if (isset($notification->data['action_url'])) {
                return redirect($notification->data['action_url']);
            }
        }

        return back(); // Kembali ke halaman sebelumnya
    }

    /**
     * Tandai SEMUA notifikasi sebagai sudah dibaca.
     */
    public function markAllRead(Request $request)
    {
        $request->user()->unreadNotifications->markAsRead();

        return back()->with('success', 'Semua notifikasi telah ditandai sudah dibaca.');
    }

    /**
     * Hapus notifikasi (Opsional, untuk bersih-bersih).
     */
    public function destroy(Request $request, $id)
    {
        $notification = $request->user()
            ->notifications()
            ->where('id', $id)
            ->first();

        if ($notification) {
            $notification->delete();
        }

        return back()->with('success', 'Notifikasi dihapus.');
    }
}