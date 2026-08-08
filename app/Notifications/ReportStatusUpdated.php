<?php

namespace App\Notifications;

use App\Models\Report;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Notification;

class ReportStatusUpdated extends Notification
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
        $isResolved = $this->report->status === 'resolved';
        
        // Tentukan tipe icon sesuai logika Vue
        $iconType = $isResolved ? 'check' : 'cross'; 
        $statusText = $isResolved ? 'Diselesaikan' : 'Ditolak';

        return [
            // Mendukung HTML (v-html) untuk menebalkan Judul
            'message' => "Laporan <b>{$this->report->subject}</b> telah {$statusText}.",
            
            // Key ini wajib ada agar icon muncul di Frontend
            'icon_type' => $iconType, 
            
            'link' => route('user.reports.index'),
            'created_at' => now(),
        ];
    }
}