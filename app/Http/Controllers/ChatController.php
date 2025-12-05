<?php

namespace App\Http\Controllers;

use App\Models\Chat;
use App\Models\User;
use App\Models\Service;
use App\Models\Booking;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use App\Events\MessageSent;
use App\Events\MessageRead; // <--- Import Event di atas
use App\Events\MessageDeleted;

class ChatController extends Controller
{
    public function index(Request $request)
    {
        $userId = Auth::id();

        // 1. Sidebar List (User yang pernah chat)
        $chatPartners = Chat::where('sender_id', $userId)
            ->orWhere('receiver_id', $userId)
            ->get()
            ->map(function ($chat) use ($userId) {
                return $chat->sender_id == $userId ? $chat->receiver_id : $chat->sender_id;
            })
            ->unique()
            ->values();

        $conversations = User::whereIn('id', $chatPartners)->get()->map(function($user) use ($userId) {
            $lastMessage = Chat::where(function($q) use ($userId, $user) {
                $q->where('sender_id', $userId)->where('receiver_id', $user->id);
            })->orWhere(function($q) use ($userId, $user) {
                $q->where('sender_id', $user->id)->where('receiver_id', $userId);
            })->latest()->first();

            $user->last_message = $lastMessage;

            $user->unread_count = Chat::where('sender_id', $user->id)
                ->where('receiver_id', $userId)
                ->where('is_read', false)
                ->count();
                
            return $user;
        })->sortByDesc('last_message.created_at')->values();


        // 2. Load Chat Aktif
        $activeChat = null;
        $messages = [];
        $targetService = null;
        $targetBooking = null;

        if ($request->user_id) {
            $partnerId = $request->user_id;
            $activeChat = User::find($partnerId);

            // AMBIL PESAN (FULL RELASI)
            $messages = Chat::with([
                'sender', 
                'replyTo',          
                'service.galleries', // Service langsung
                'booking.service.galleries' // [PENTING] Service di dalam Booking
            ])
            ->withTrashed() // <--- TAMBAHKAN INI (Agar pesan terhapus tetap terambil)
            ->where(function($q) use ($userId, $partnerId) {
                $q->where('sender_id', $userId)->where('receiver_id', $partnerId);
            })->orWhere(function($q) use ($userId, $partnerId) {
                $q->where('sender_id', $partnerId)->where('receiver_id', $userId);
            })
            ->orderBy('created_at', 'asc')
            ->orderBy('id', 'asc')
            ->get();

            // LOGIKA DETEKTIF KONTEKS (Agar header muncul otomatis)
            
            // A. Cek URL (Prioritas 1)
            if ($request->booking_id) {
                $targetBooking = Booking::with(['service.galleries'])->withTrashed()->find($request->booking_id);
                if ($targetBooking) $targetService = $targetBooking->service;
            } 
            elseif ($request->service_id) {
                $targetService = Service::with('galleries')->withTrashed()->find($request->service_id);
            }
            
            // B. Cek History Chat Terakhir (Prioritas 2)
            else {
                $latestMessage = $messages->last(); // Ambil dari collection yg sudah di-load

                if ($latestMessage) {
                    if ($latestMessage->booking_id) {
                        // Ambil dari relasi yang sudah ada di message (agar cepat)
                        $targetBooking = $latestMessage->booking;
                        
                        // Jika null (mungkin relasi tidak ke-load sempurna), query ulang dengan safe mode
                        if (!$targetBooking) {
                            $targetBooking = Booking::with(['service.galleries'])->withTrashed()->find($latestMessage->booking_id);
                        }
                        
                        if ($targetBooking) $targetService = $targetBooking->service;
                    }
                    elseif ($latestMessage->service_id) {
                        $targetService = $latestMessage->service;
                        if (!$targetService) {
                            $targetService = Service::with('galleries')->withTrashed()->find($latestMessage->service_id);
                        }
                    }
                }
            }

            $updatedRows = Chat::where('sender_id', $partnerId)
                ->where('receiver_id', $userId)
                ->where('is_read', false)
                ->update(['is_read' => true]);

            // --- LOGIC REALTIME READ ---
            // Jika ada setidaknya 1 pesan yang baru saja di-update jadi Read
            if ($updatedRows > 0) {
                // Beritahu Partner (Pengirim) bahwa "Saya (UserId) sudah baca pesanmu"
                broadcast(new MessageRead($userId, $partnerId));
            }
        }
        

        return Inertia::render('Chats/Index', [
            'conversations' => $conversations ?? [],
            'activeChat' => $activeChat,
            'messages' => $messages,
            'targetService' => $targetService,
            'targetBooking' => $targetBooking,
            'auth_id' => $userId
        ]);
    }

    public function store(Request $request)
    {
        $request->validate([
            'receiver_id' => 'required|exists:users,id',
            'message' => 'required|string',
            'service_id' => 'nullable|exists:services,id',
            'booking_id' => 'nullable|exists:bookings,id',
            'reply_to_id' => 'nullable|exists:chats,id'
        ]);

        $chat = Chat::create([
            'sender_id' => Auth::id(),
            'receiver_id' => $request->receiver_id,
            'service_id' => $request->service_id,
            'booking_id' => $request->booking_id,
            'reply_to_id' => $request->reply_to_id,
            'message' => $request->message,
            'is_read' => false
        ]);

        // [PERBAIKAN UTAMA DISINI]
        // Load relasi HARUS SAMA PERSIS dengan method index
        // Agar struktur JSON yang dikirim ke Frontend (Realtime/Redirect) lengkap
        $chat->load([
            'sender', 
            'replyTo', 
            'service.galleries', 
            'booking.service.galleries' // <-- INI YANG SEBELUMNYA KURANG
        ]);

        // Trigger Realtime
        broadcast(new MessageSent($chat))->toOthers(); 

        return redirect()->back();
    }

    public function markAsRead(Request $request)
    {
        $userId = Auth::id();
        $senderId = $request->sender_id;

        // Update semua pesan dari pengirim ini yang belum dibaca
        $updated = Chat::where('sender_id', $senderId)
            ->where('receiver_id', $userId)
            ->where('is_read', false)
            ->update(['is_read' => true]);

        // Jika ada yang diupdate, kirim sinyal ke pengirim
        if ($updated > 0) {
            broadcast(new MessageRead($userId, $senderId));
        }

        return response()->json(['status' => 'success']);
    }

    public function destroy(Chat $chat)
    {
        // Pastikan hanya pemilik pesan yang bisa hapus
        if ($chat->sender_id !== Auth::id()) {
            abort(403);
        }

        $chat->delete(); // Soft Delete

        // Trigger Realtime ke lawan bicara
        broadcast(new MessageDeleted($chat->id, $chat->receiver_id))->toOthers();

        return back();
    }
}