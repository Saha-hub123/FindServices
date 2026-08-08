<?php

namespace App\Events;

use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcastNow;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class TestLatency implements ShouldBroadcastNow
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public $type;    // Jenis tes: 'simple', 'review', 'booking'
    public $payload; // Data isinya (objek review/booking)
    public $sent_at; 

    public function __construct($type, $payload)
    {
        $this->type = $type;
        $this->payload = $payload;
        $this->sent_at = microtime(true) * 1000; 
    }

    public function broadcastOn(): array
    {
        return [
            new Channel('test-channel'),
        ];
    }
}