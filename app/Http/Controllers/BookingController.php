<?php

namespace App\Http\Controllers;

use App\Models\Booking;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Illuminate\Support\Facades\Auth;
use App\Models\Service; 
use Illuminate\Support\Facades\DB;
use App\Models\Review;
use Carbon\Carbon;
use App\Events\BookingStatusUpdated; // Import Event
use App\Events\ReviewSubmitted;


class BookingController extends Controller
{
    public function index()
    {
        $user = Auth::user();

        // Daftar status yang dianggap "Aktif" (Butuh tindakan)
        $activeStatuses = ['unpaid', 'pending', 'paid', 'confirmed', 'in_progress', 'waiting_completion'];
        
        // Daftar status yang dianggap "Selesai/Arsip"
        $historyStatuses = ['completed', 'cancelled', 'rejected'];

        // 1. Booking Saya (Customer) - HANYA YANG AKTIF
        $myBookings = Booking::with(['service.galleries', 'provider'])
            ->where('customer_id', $user->id)
            ->whereIn('status', $activeStatuses)
            ->latest()
            ->get();

        // 2. Pesanan Masuk (Provider) - HANYA YANG AKTIF
        $incomingOrders = Booking::with(['service.galleries', 'customer'])
            ->where('provider_id', $user->id)
            ->whereIn('status', $activeStatuses)
            ->latest()
            ->get();

        // 3. [BARU] Riwayat (Gabungan Customer & Provider)
        $history = Booking::with(['service.galleries', 'provider', 'customer'])
            ->where(function($q) use ($user) {
                $q->where('customer_id', $user->id)
                ->orWhere('provider_id', $user->id);
            })
            ->whereIn('status', $historyStatuses)
            ->latest()
            ->get();

        return Inertia::render('Bookings/Index', [
            'myBookings' => $myBookings,
            'incomingOrders' => $incomingOrders,
            'history' => $history // Kirim data history
        ]);
    }

    // public function show(Booking $booking)
    // {
    //     // Pastikan yang akses cuma customer atau provider terkait
    //     if (Auth::id() !== $booking->customer_id && Auth::id() !== $booking->provider_id) {
    //         abort(403);
    //     }

    //     $booking->load(['service', 'customer', 'provider']);

    //     return Inertia::render('Bookings/Show', [
    //         'booking' => $booking
    //     ]);
    // }


    public function create(Request $request)
    {
        $serviceId = $request->service_id;
        $service = Service::with(['user', 'galleries', 'category'])->findOrFail($serviceId);

        if ($service->user_id === Auth::id()) {
            return redirect()->back()->with('error', 'Anda tidak bisa membooking jasa sendiri.');
        }

        // LOGIKA BARU: Cari tanggal yang SUDAH PENUH (>= 5 booking)
        $fullyBookedDates = \App\Models\Booking::where('service_id', $serviceId)
            ->whereIn('status', ['unpaid', 'pending', 'paid', 'confirmed', 'in_progress', 'waiting_completion', 'completed']) // Semua status aktif (kecuali cancelled/rejected)
            ->select('booking_date', DB::raw('count(*) as total'))
            ->groupBy('booking_date')
            ->having('total', '>=', 5) // LIMIT 5 SLOT
            ->pluck('booking_date')
            ->map(function($date) {
                return \Carbon\Carbon::parse($date)->format('Y-m-d');
            })
            ->toArray();

        return Inertia::render('Bookings/Create', [
            'service' => $service,
            // Kita kirim variabel ini. Tanggal yang ada di sini akan merah/disable.
            // Tanggal yang bookingnya cuma 1-4 TIDAK akan ada di sini, jadi bisa dipilih.
            'bookedDates' => $fullyBookedDates 
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'service_id' => 'required|exists:services,id',
            'booking_date' => 'required|date|after_or_equal:today',
            'booking_time' => 'required',
            'location' => 'required|string',
            'latitude' => 'required|numeric',
            'longitude' => 'required|numeric',
            'notes' => 'nullable|string',
        ]);

        $service = Service::findOrFail($validated['service_id']);

        // LOGIKA BARU: Cek Kuota
        $existingBookingsCount = \App\Models\Booking::where('service_id', $service->id)
            ->where('booking_date', $validated['booking_date'])
            ->whereIn('status', ['unpaid', 'pending', 'paid', 'confirmed', 'in_progress', 'waiting_completion', 'completed'])
            ->count();

        if ($existingBookingsCount >= 5) {
            return back()->withErrors(['booking_date' => 'Mohon maaf, kuota untuk tanggal ini sudah penuh (Max 5).']);
        }

        // Tentukan Status Awal
        $initialStatus = 'pending'; // Default untuk Manual (Menunggu Konfirmasi)

        if ($request->payment_method === 'gateway') {
            $initialStatus = 'unpaid';
        }

        \App\Models\Booking::create([
            'service_id' => $service->id,
            'customer_id' => Auth::id(),
            'provider_id' => $service->user_id,
            'booking_date' => $validated['booking_date'],
            'booking_time' => $validated['booking_time'],
            'location' => $validated['location'],
            'latitude' => $validated['latitude'],
            'longitude' => $validated['longitude'],
            'notes' => $validated['notes'],
            'initial_price' => $service->price_min, // Simpan sebagai Harga Awal
            'final_price' => null, // Biarkan kosong dulu
            'payment_method' => $request->payment_method, // 'manual'
            'status' => $initialStatus
        ]);

        // // Redirect Logic
        // if ($initialStatus === 'unpaid') {
        //     // Nanti: Redirect ke halaman pembayaran
        //     return redirect()->route('bookings.payment', $booking->id); 
        // }


        return redirect()->route('bookings.index')->with('message', 'Booking berhasil dibuat! Menunggu konfirmasi.');
    }

    

    public function show(Booking $booking)
    {
        // Cek Hak Akses
        $userId = Auth::id();
        if ($userId !== $booking->customer_id && $userId !== $booking->provider_id) {
            abort(403);
        }

        $booking->load(['service.galleries', 'customer', 'provider', 'review']);

        return Inertia::render('Bookings/Show', [
            'booking' => $booking,
            'isProvider' => $userId === $booking->provider_id,
            'isCustomer' => $userId === $booking->customer_id,
            'user_id' => $userId
        ]);
    }

    public function updateStatus(Request $request, Booking $booking)
    {
        if ($request->status === 'confirmed') {
            
            // LOGIKA KUNCI:
            // Jika final_price masih NULL (artinya customer tidak pernah edit harga),
            // Maka kita 'lock' harga deal sama dengan harga initial.
            if ($booking->final_price === null) {
                $booking->final_price = $booking->initial_price;
            }
            
            // Jika customer SUDAH edit (final_price ada isinya), biarkan saja (itu harga dealnya).
            
            $booking->status = 'confirmed';
            $booking->save();
        } 
        else {
            // Untuk status lain (rejected/cancelled/completed)
            $booking->update(['status' => $request->status]);
        }

        broadcast(new BookingStatusUpdated($booking))->toOthers();

        return back()->with('message', 'Status pesanan diperbarui.');
    }

    // // Contoh Logic Update Status oleh Provider (Masa Depan)
    // public function updateStatus(Request $request, Booking $booking)
    // {
    //     if ($request->status === 'confirmed') {
    //         // 1. Kunci Harga Final
    //         // Jika provider tidak input harga baru, pakai harga awal
    //         $dealPrice = $request->input('new_price', $booking->initial_price); 
    //         $booking->update([
    //             'final_price' => $dealPrice,
    //         ]);
    //         // 2. Cek Metode Bayar
    //         if ($booking->payment_method === 'gateway') {
    //             // JANGAN langsung 'confirmed', tapi suruh bayar dulu
    //             $booking->update(['status' => 'unpaid']); 
    //             // Trigger kirim notif ke customer: "Silakan bayar tagihan Anda"
    //         } else {
    //             // Kalau Manual (COD), langsung confirm
    //             $booking->update(['status' => 'confirmed']);
    //         }
    //     }
    // }

    // ...

    public function edit(Booking $booking)
    {
        // 1. Cek Hak Akses
        if (Auth::id() !== $booking->customer_id) abort(403);

        // 2. Cek Status
        if (!in_array($booking->status, ['pending', 'rejected'])) {
            return redirect()->route('bookings.show', $booking->id)
                ->with('error', 'Pesanan tidak bisa diedit karena sudah diproses.');
        }

        // --- PERBAIKAN DISINI ---
        // Memuat relasi service beserta user (penyedia), galeri, dan kategori
        $booking->load(['service.user', 'service.galleries', 'service.category']);
        // ------------------------

        // Ambil booked dates
        $bookingCounts = \App\Models\Booking::where('service_id', $booking->service_id)
            ->where('id', '!=', $booking->id)
            ->whereIn('status', ['unpaid', 'pending', 'paid', 'confirmed', 'in_progress', 'waiting_completion', 'completed'])
            ->select('booking_date', DB::raw('count(*) as total'))
            ->groupBy('booking_date')
            ->get()
            ->mapWithKeys(function ($item) {
                return [$item->booking_date->format('Y-m-d') => $item->total];
            });

        return Inertia::render('Bookings/Edit', [
            'booking' => $booking,
            'bookedDates' => $bookingCounts
        ]);
    }

    public function update(Request $request, Booking $booking)
    {
        if (Auth::id() !== $booking->customer_id) abort(403);
        if (!in_array($booking->status, ['pending', 'rejected'])) abort(403);

        $validated = $request->validate([
            'booking_date' => 'required|date|after_or_equal:today',
            'booking_time' => 'required',
            'location' => 'required|string',
            'latitude' => 'required|numeric',
            'longitude' => 'required|numeric',
            'notes' => 'nullable|string',
            'offer_price' => 'required|numeric|min:0',
        ]);

        // Update Data
        $booking->update([
            // FIX: Parsing tanggal menggunakan Carbon agar formatnya pasti Y-m-d
            'booking_date' => Carbon::parse($validated['booking_date'])->format('Y-m-d'),
            
            'booking_time' => $validated['booking_time'],
            'location' => $validated['location'],
            'latitude' => $validated['latitude'],
            'longitude' => $validated['longitude'],
            'notes' => $validated['notes'],
            'final_price' => $validated['offer_price'],
        ]);

        // 2. Broadcast Event (INI KUNCINYA)
        // Pastikan object $booking yang dikirim adalah data TERBARU (sudah terupdate)
        broadcast(new BookingStatusUpdated($booking))->toOthers();

        return redirect()->route('bookings.show', $booking->id)->with('message', 'Pesanan berhasil diperbarui!');
    }

    public function storeReview(Request $request, Booking $booking)
    {
        $request->validate([
            'rating' => 'required|integer|min:1|max:5',
            'comment' => 'required|string|max:500'
        ]);

        $review = Review::create([
            'booking_id' => $booking->id,
            'service_id' => $booking->service_id,
            'user_id' => Auth::id(),
            'rating' => $request->rating,
            'review' => $request->comment // Sesuaikan nama kolom di DB
        ]);

        // --- TAMBAHAN REALTIME ---
        broadcast(new ReviewSubmitted($review))->toOthers();
        // -------------------------

        return back()->with('message', 'Terima kasih atas ulasan Anda!');
    }

}