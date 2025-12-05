<?php

namespace App\Events;

use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcastNow; // WAJIB NOW
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class MessageRead implements ShouldBroadcastNow
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public $reader_id; // ID Orang yang membaca pesan (Penerima)
    public $sender_id; // ID Orang yang mengirim pesan (Yang perlu dikabari)

    public function __construct($reader_id, $sender_id)
    {
        $this->reader_id = $reader_id;
        $this->sender_id = $sender_id;
    }

    public function broadcastOn(): array
    {
        // Kirim notifikasi ke channel PENGIRIM ASLI
        // Agar dia tahu pesannya sudah dibaca
        return [
            new PrivateChannel('chat.' . $this->sender_id),
        ];
    }
}