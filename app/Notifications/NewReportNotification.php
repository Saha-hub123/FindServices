<?php

namespace App\Notifications;

use App\Models\Report;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Notification;

class NewReportNotification extends Notification
{
    use Queueable;
    public $report;

    public function __construct(Report $report)
    {
        $this->report = $report;
    }

    public function via($notifiable)
    {
        return ['database'];
    }

    public function toArray($notifiable)
    {
        return [
            'message' => "Laporan baru masuk: <b>{$this->report->subject}</b>.",
            // UBAH DARI 'clock' MENJADI 'file'
            'icon_type' => 'file',
            'link' => route('admin.reports.index', ['status' => 'pending']),
            'created_at' => now(),
        ];
    }
}