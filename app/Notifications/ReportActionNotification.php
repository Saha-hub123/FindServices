<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Notification;

class ReportActionNotification extends Notification
{
    use Queueable;
    public $report; // Bisa berupa Object Report atau Array data (jika deleted)
    public $action; // 'updated' atau 'deleted'

    public function __construct($report, $action)
    {
        $this->report = $report;
        $this->action = $action;
    }

    public function via($notifiable)
    {
        return ['database'];
    }

    public function toArray($notifiable)
    {
        // Handle jika report sudah dihapus (ambil subject dari array/object clone)
        $subject = $this->report->subject ?? $this->report['subject'] ?? 'Tanpa Judul';
        $userName = auth()->user()->name;

        if ($this->action === 'deleted') {
            return [
                'message' => "Laporan <b>{$subject}</b> dibatalkan oleh pelapor ({$userName}).",
                'icon_type' => 'cross', // Menampilkan icon silang merah (fas fa-times-circle)
                'link' => route('admin.reports.index'),
                'created_at' => now(),
            ];
        }

        // Action: Updated
        return [
            'message' => "Revisi data masuk pada laporan <b>{$subject}</b>.",
            'icon_type' => 'tools', // Menampilkan icon obeng (fas fa-tools)
            'link' => route('admin.reports.index', ['status' => 'pending']),
            'created_at' => now(),
        ];
    }
}