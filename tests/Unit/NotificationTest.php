<?php

namespace Tests\Unit;

use Tests\TestCase;
use App\Models\User;
use App\Models\Booking;
use App\Models\Service;
use App\Models\Report;
use App\Models\Review;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Config;

class NotificationTest extends TestCase
{
    use RefreshDatabase;

    // 1. Test NewBookingNotification
    public function test_new_booking_notification_format()
    {
        $customer = User::factory()->create(['name' => 'Budi Customer']);
        $service = Service::factory()->create(['title' => 'Cuci AC']);
        $booking = Booking::factory()->create([
            'customer_id' => $customer->id,
            'service_id' => $service->id
        ]);

        $notification = new \App\Notifications\NewBookingNotification($booking);
        
        // Simulasi notifiable (tidak dipakai di logic toArray, tapi butuh parameter)
        $data = $notification->toArray($customer);

        $this->assertStringContainsString('Budi Customer', $data['message']);
        $this->assertStringContainsString('Cuci AC', $data['message']);
        $this->assertEquals('booking_new', $data['type']);
        $this->assertStringContainsString(route('bookings.show', $booking), $data['action_url']);
    }

    // 2. Test ReportStatusUpdated (Resolved & Rejected)
    public function test_report_status_updated_notification_format()
    {
        // Case A: Resolved
        $reportResolved = Report::factory()->create(['status' => 'resolved', 'subject' => 'Masalah Login']);
        $notifResolved = new \App\Notifications\ReportStatusUpdated($reportResolved);
        $dataResolved = $notifResolved->toArray(new User());

        $this->assertStringContainsString('Diselesaikan', $dataResolved['message']);
        $this->assertEquals('check', $dataResolved['icon_type']);

        // Case B: Rejected
        $reportRejected = Report::factory()->create(['status' => 'rejected', 'subject' => 'Spam']);
        $notifRejected = new \App\Notifications\ReportStatusUpdated($reportRejected);
        $dataRejected = $notifRejected->toArray(new User());

        $this->assertStringContainsString('Ditolak', $dataRejected['message']);
        $this->assertEquals('cross', $dataRejected['icon_type']);
    }

    // 3. Test ReportActionNotification (Updated & Deleted)
    public function test_report_action_notification_format()
    {
        $user = User::factory()->create(['name' => 'Admin Ganteng']);
        $this->actingAs($user); // Login sebagai admin agar auth()->user()->name terbaca

        $report = Report::factory()->create(['subject' => 'Laporan Palsu']);

        // Case A: Deleted
        $notifDeleted = new \App\Notifications\ReportActionNotification($report, 'deleted');
        $dataDeleted = $notifDeleted->toArray($user);

        $this->assertStringContainsString('dibatalkan oleh pelapor', $dataDeleted['message']);
        $this->assertEquals('cross', $dataDeleted['icon_type']);

        // Case B: Updated
        $notifUpdated = new \App\Notifications\ReportActionNotification($report, 'updated');
        $dataUpdated = $notifUpdated->toArray($user);

        $this->assertStringContainsString('Revisi data masuk', $dataUpdated['message']);
        $this->assertEquals('tools', $dataUpdated['icon_type']);
    }

    // 4. Test NewReportNotification
    public function test_new_report_notification_format()
    {
        $report = Report::factory()->create(['subject' => 'Error 500']);
        $notification = new \App\Notifications\NewReportNotification($report);
        $data = $notification->toArray(new User());

        $this->assertStringContainsString('Laporan baru masuk', $data['message']);
        $this->assertStringContainsString('Error 500', $data['message']);
        $this->assertEquals('file', $data['icon_type']);
    }

    // 5. Test PaymentConfirmedNotification (Gateway & Manual)
    public function test_payment_confirmed_notification_format()
    {
        // Case A: Gateway
        $bookingGateway = Booking::factory()->create(['payment_method' => 'gateway']);
        $notifGateway = new \App\Notifications\PaymentConfirmedNotification($bookingGateway);
        $dataGateway = $notifGateway->toArray(new User());

        $this->assertStringContainsString('via Gateway', $dataGateway['message']);
        $this->assertEquals('payment_success', $dataGateway['type']);

        // Case B: Manual
        $bookingManual = Booking::factory()->create(['payment_method' => 'manual']);
        $notifManual = new \App\Notifications\PaymentConfirmedNotification($bookingManual);
        $dataManual = $notifManual->toArray(new User());

        $this->assertStringContainsString('Pembayaran Manual', $dataManual['message']);
    }

    // 6. Test NewReviewNotification
    public function test_new_review_notification_format()
    {
        $user = User::factory()->create(['name' => 'Reviewer Kejam']);
        $booking = Booking::factory()->create();
        $review = Review::factory()->create([
            'user_id' => $user->id,
            'booking_id' => $booking->id,
            'rating' => 5,
            'review' => 'Sangat bagus!'
        ]);

        $notification = new \App\Notifications\NewReviewNotification($review);
        $data = $notification->toArray(new User());

        $this->assertStringContainsString('Reviewer Kejam', $data['message']);
        $this->assertStringContainsString('⭐⭐⭐⭐⭐', $data['message']); // 5 Bintang
        $this->assertStringContainsString('Sangat bagus!', $data['message']);
        $this->assertEquals('review_new', $data['type']);
    }

    // 7. Test BookingStatusUpdatedNotification (Complex Logic)
    public function test_booking_status_updated_notification_format()
    {
        $provider = User::factory()->create(['name' => 'Provider Jasa']);
        $customer = User::factory()->create(['name' => 'Customer Setia']);
        $service = Service::factory()->create(['title' => 'Pijat Refleksi', 'user_id' => $provider->id]);
        
        $booking = Booking::factory()->create([
            'provider_id' => $provider->id,
            'customer_id' => $customer->id,
            'service_id' => $service->id,
            'status' => 'confirmed'
        ]);

        // Case A: Status Confirmed (Dilihat Customer)
        $booking->status = 'confirmed';
        $notif = new \App\Notifications\BookingStatusUpdatedNotification($booking);
        $data = $notif->toArray($customer); // Dikirim ke customer

        $this->assertStringContainsString('DITERIMA', $data['message']);
        $this->assertEquals('check', $data['icon_type']);

        // Case B: Status Rejected
        $booking->status = 'rejected';
        $notif = new \App\Notifications\BookingStatusUpdatedNotification($booking);
        $data = $notif->toArray($customer);

        $this->assertStringContainsString('DITOLAK', $data['message']);
        $this->assertEquals('cross', $data['icon_type']);

        // Case C: Status Completed (Sudut Pandang Provider)
        $booking->status = 'completed';
        $notif = new \App\Notifications\BookingStatusUpdatedNotification($booking);
        // Penting: Parameter toArray adalah 'Provider' agar logic $isProvider bernilai true
        $data = $notif->toArray($provider); 

        $this->assertStringContainsString('dikonfirmasi selesai oleh Customer', $data['message']);
        $this->assertEquals('check', $data['icon_type']);

        // Case D: Status Completed (Sudut Pandang Customer)
        $dataCustomer = $notif->toArray($customer);
        $this->assertStringContainsString('Terima kasih telah menggunakan jasa ini', $dataCustomer['message']);
    }
}