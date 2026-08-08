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
use Vinkla\Hashids\Facades\Hashids; // <--- JANGAN LUPA IMPORT INI

class ChatController extends Controller
{
    public function index(Request $request)
    {
        $userId = Auth::id();

        // 1. Sidebar List (User yang pernah chat)
        // (Bagian ini tidak berubah, logic-nya sudah benar)
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


        // 2. Load Chat Aktif & Konteks
        $activeChat = null;
        $messages = [];
        $targetService = null;
        $targetBooking = null;

        // Cek apakah ada user_id di URL (Hash ID)
        if ($request->user_id) {
            
            // [A] DECODE USER ID
            $decoded = Hashids::decode($request->user_id);
            $partnerId = $decoded[0] ?? null; 

            if (!$partnerId) {
                abort(404, 'User tidak ditemukan'); 
            }

            $activeChat = User::find($partnerId);

            // [TAMBAHAN WAJIB] 
            // Pastikan hash_id terkirim ke frontend
            if ($activeChat) {
                // Opsi 1: Jika di Model User sudah ada getHashIdAttribute / appends
                // $activeChat->append('hash_id'); 

                // Opsi 2: Manual encode di sini (Paling aman jika Model belum disetup)
                $activeChat->hash_id = Hashids::encode($activeChat->id);
            }

            // [B] AMBIL PESAN
            $messages = Chat::with([
                'sender', 
                'replyTo',          
                'service.galleries', 
                'booking.service.galleries'
            ])
            ->withTrashed()
            ->where(function($q) use ($userId, $partnerId) {
                $q->where('sender_id', $userId)->where('receiver_id', $partnerId);
            })->orWhere(function($q) use ($userId, $partnerId) {
                $q->where('sender_id', $partnerId)->where('receiver_id', $userId);
            })
            ->orderBy('created_at', 'asc')
            ->orderBy('id', 'asc')
            ->get(); // Gunakan get() agar jadi Collection

            // [C] LOGIKA KONTEKS (BOOKING / SERVICE)
            
            // PRIORITAS 1: Cek URL Parameter
            
            // Cek Booking ID (Hash Encrypted)
            if ($request->booking_id) {
                $decodedBooking = \Vinkla\Hashids\Facades\Hashids::decode($request->booking_id);
                $bookingIdInt = $decodedBooking[0] ?? null;
                
                if ($bookingIdInt) {
                    $targetBooking = Booking::with(['service.galleries'])->withTrashed()->find($bookingIdInt);
                    if ($targetBooking) $targetService = $targetBooking->service;
                }
            } 
            // Cek Service ID (Integer / Tidak Dienkripsi)
            elseif ($request->service_id) {
                // Langsung pakai request->service_id karena integer
                $targetService = Service::with('galleries')->withTrashed()->find($request->service_id);
            }
            
            // PRIORITAS 2: Jika URL Kosong, Cek History Chat Terakhir
            if (!$targetBooking && !$targetService) {
                // Pastikan messages adalah collection
                $latestMessage = collect($messages)->last(); 

                if ($latestMessage) {
                    if ($latestMessage->booking_id) {
                        $targetBooking = $latestMessage->booking;
                        
                        // Safety check jika relasi null
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

            // [D] UPDATE STATUS READ
            $updatedRows = Chat::where('sender_id', $partnerId)
                ->where('receiver_id', $userId)
                ->where('is_read', false)
                ->update(['is_read' => true]);

            if ($updatedRows > 0) {
                broadcast(new \App\Events\MessageRead($userId, $partnerId));
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
        // 1. VALIDASI INPUT UMUM (Kecuali ID yang di-hash)
        $request->validate([
            'message' => 'required|string',
            'service_id' => 'nullable|integer', // Service ID tidak dienkripsi (sesuai request)
            'reply_to_id' => 'nullable|integer',
        ]);

        // 2. DECODE HASH ID
        
        // A. Decode Receiver ID
        $receiverId = null;
        if ($request->receiver_id) {
            // Coba decode string hash
            $decoded = Hashids::decode($request->receiver_id);
            $receiverId = $decoded[0] ?? null;
        }

        // Validasi Manual: Pastikan Receiver valid
        if (!$receiverId) {
            return back()->withErrors(['receiver_id' => 'User penerima tidak valid.']);
        }

        // B. Decode Booking ID (Jika ada)
        $bookingId = null;
        if ($request->booking_id) {
            $decodedBooking = Hashids::decode($request->booking_id);
            $bookingId = $decodedBooking[0] ?? null;
        }

        // 3. SIMPAN KE DATABASE (Gunakan ID Integer hasil decode)
        $chat = Chat::create([
            'sender_id'   => Auth::id(),
            'receiver_id' => $receiverId,       // <--- Pakai Integer
            'service_id'  => $request->service_id, // <--- Langsung dari request (Integer)
            'booking_id'  => $bookingId,        // <--- Pakai Integer
            'reply_to_id' => $request->reply_to_id,
            'message'     => $request->message,
            'is_read'     => false
        ]);

        // 4. LOAD RELASI (PENTING UNTUK REALTIME)
        // Struktur ini harus sama persis dengan index() agar Vue tidak error saat terima data baru
        $chat->load([
            'sender', 
            'replyTo', 
            'service.galleries', 
            'booking.service.galleries' // <-- Relasi dalam untuk konteks booking
        ]);

        // 5. BROADCAST EVENT
        broadcast(new \App\Events\MessageSent($chat))->toOthers(); 

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