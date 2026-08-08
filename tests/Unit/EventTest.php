<?php

namespace Tests\Unit;

use Tests\TestCase;
use App\Models\User;
use App\Models\Chat;
use App\Models\Booking;
use App\Models\Review;
use App\Models\Service; // Tambahkan ini agar factory booking aman
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Foundation\Testing\RefreshDatabase;

class EventTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test 1: MessageRead Event
     */
    public function test_message_read_event_structure_and_channel()
    {
        $readerId = 1;
        $senderId = 2;

        // Instansiasi Event
        $event = new \App\Events\MessageRead($readerId, $senderId);

        // Cek Properti
        $this->assertEquals($readerId, $event->reader_id);
        $this->assertEquals($senderId, $event->sender_id);

        // Cek Channel Broadcast (HARUS ADA 'private-')
        $channels = $event->broadcastOn();
        $this->assertInstanceOf(PrivateChannel::class, $channels[0]);
        $this->assertEquals('private-chat.2', $channels[0]->name);
    }

    /**
     * Test 2: MessageSent Event
     */
    public function test_message_sent_event_structure_and_channel()
    {
        // [PERBAIKAN] Buat User dulu agar tidak error Foreign Key
        $sender = User::factory()->create();
        $receiver = User::factory()->create();

        // Mock Chat Model
        $chat = Chat::factory()->create([
            'sender_id' => $sender->id,
            'receiver_id' => $receiver->id,
            'message' => 'Test message'
        ]);

        $event = new \App\Events\MessageSent($chat);

        // Cek Properti
        $this->assertEquals($chat->id, $event->chat->id);

        // Cek Channel Broadcast (Target: receiver)
        $channels = $event->broadcastOn();
        // Channel otomatis tambah prefix 'private-'
        $this->assertEquals('private-chat.' . $receiver->id, $channels[0]->name);
    }

    /**
     * Test 3: MessageDeleted Event
     */
    public function test_message_deleted_event_structure_and_channel()
    {
        $chatId = 100;
        $receiverId = 50;

        $event = new \App\Events\MessageDeleted($chatId, $receiverId);

        // Cek Properti
        $this->assertEquals($chatId, $event->chatId);
        $this->assertEquals($receiverId, $event->receiverId);

        // Cek Channel Broadcast
        $channels = $event->broadcastOn();
        $this->assertEquals('private-chat.50', $channels[0]->name);
    }

    /**
     * Test 4: BookingStatusUpdated Event
     */
    public function test_booking_status_updated_event_structure_and_channel()
    {
        // Mock Booking (Factory otomatis buat user & service terkait)
        // Kita butuh HashID trait, pastikan booking ter-create di DB
        $booking = Booking::factory()->create(); 
        
        $event = new \App\Events\BookingStatusUpdated($booking);

        // Cek Properti
        $this->assertEquals($booking->id, $event->booking->id);

        // Cek Channel Broadcast
        $channels = $event->broadcastOn();
        // Format: private-booking.{hash_id}
        $this->assertEquals('private-booking.' . $booking->hash_id, $channels[0]->name);
    }

    /**
     * Test 5: ReviewSubmitted Event
     */
    public function test_review_submitted_event_structure_and_channel()
    {
        // Mock Review yang punya booking_id
        $booking = Booking::factory()->create();
        $review = Review::factory()->create([
            'booking_id' => $booking->id,
            'user_id' => User::factory()->create()->id, // Buat user penilai
            'service_id' => $booking->service_id
        ]);

        $event = new \App\Events\ReviewSubmitted($review);

        // Cek Properti
        $this->assertEquals($review->id, $event->review->id);

        // Cek Channel Broadcast
        $channels = $event->broadcastOn();
        // Format: private-booking.{booking_id}
        $this->assertEquals('private-booking.' . $booking->id, $channels[0]->name);
    }
}