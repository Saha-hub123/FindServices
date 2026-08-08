<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Notification;

class NewReviewNotification extends Notification
{
    use Queueable;

    public $review; // Kita terima object Review, bukan Booking

    public function __construct($review)
    {
        $this->review = $review;
    }

    public function via($notifiable)
    {
        return ['database'];
    }

    public function toArray($notifiable)
    {
        $customerName = $this->review->user->name;
        $stars = str_repeat('⭐', $this->review->rating); // Visual bintang

        return [
            'message' => "<b>{$customerName}</b> memberikan ulasan: {$stars}<br><i>\"{$this->review->review}\"</i>",
            'action_url' => route('bookings.show', $this->review->booking->hash_id),
            'type' => 'review_new'
        ];
    }
}