<?php

namespace App\Events;

use App\Models\Chat;
use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Broadcasting\PresenceChannel;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcastNow; // Pakai Now agar instan
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

// PENTING: Tambahkan implements ShouldBroadcastNow
class MessageSent implements ShouldBroadcastNow
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public $chat;

    // Terima data chat di sini
    public function __construct(Chat $chat)
    {
        $this->chat = $chat;
    }

    // Tentukan Channel (Saluran) mana data ini dikirim
    public function broadcastOn(): array
    {
        // Kita pakai PrivateChannel agar orang lain tidak bisa nguping
        // Format channel: chat.{user_id_penerima}
        return [
            new PrivateChannel('chat.' . $this->chat->receiver_id),
        ];
    }
}