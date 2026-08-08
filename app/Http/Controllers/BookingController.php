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
use Midtrans\Config;
use Midtrans\Snap;
use Intervention\Image\Laravel\Facades\Image; // Jika pakai Intervention
use Illuminate\Support\Str;
use Illuminate\Support\Facades\Storage;
use App\Notifications\NewBookingNotification;
use App\Notifications\BookingStatusUpdatedNotification; // <--- Tambahkan ini
use App\Notifications\PaymentConfirmedNotification; // Baru
use App\Notifications\NewReviewNotification; // Baru
use Vinkla\Hashids\Facades\Hashids; // Import Hashids

class BookingController extends Controller
{
    private $currentSystemFee = 2000;
    public function index(Request $request)
    {
        $user = Auth::user();

        // Daftar status yang dianggap "Aktif" (Butuh tindakan)
        $activeStatuses = ['unpaid', 'pending', 'paid', 'confirmed', 'in_progress', 'waiting_completion', 'rejected'];
        
        // Daftar status yang dianggap "Selesai/Arsip"
        $historyStatuses = ['completed', 'cancelled'];

        // 1. Booking Saya (Customer) - HANYA YANG AKTIF
        $myBookings = Booking::with(['service.galleries', 'provider'])
            ->where('customer_id', $user->id)
            ->whereIn('status', $activeStatuses)
            ->latest()
            ->paginate(6, ['*'], 'my_bookings_page') // Named Pagination
            ->withQueryString();

        // 2. Pesanan Masuk (Provider) - HANYA YANG AKTIF
        $incomingOrders = Booking::with(['service.galleries', 'customer'])
            ->where('provider_id', $user->id)
            ->whereIn('status', $activeStatuses)
            ->latest()
            ->paginate(6, ['*'], 'incoming_orders_page') // Named Pagination
            ->withQueryString();

        // 3. [BARU] Riwayat (Gabungan Customer & Provider)
        $history = Booking::with(['service.galleries', 'provider', 'customer'])
            ->where(function($q) use ($user) {
                $q->where('customer_id', $user->id)
                ->orWhere('provider_id', $user->id);
            })
            ->whereIn('status', $historyStatuses)
            ->latest()
            ->paginate(9, ['*'], 'history_page') // Named Pagination
            ->withQueryString();

        // [LOAD MORE LOGIC]
        if ($request->wantsJson()) {
            return response()->json([
                'myBookings' => $myBookings,
                'incomingOrders' => $incomingOrders,
                'history' => $history
            ]);
        }

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
        $providerSchedule = Booking::where('provider_id', $service->user_id) 
            ->whereIn('status', ['unpaid', 'pending', 'paid', 'confirmed', 'in_progress', 'waiting_completion', 'rejected']) 
            ->select('booking_date', DB::raw('count(*) as total'))
            ->groupBy('booking_date')
            ->get()
            ->mapWithKeys(function ($item) {
                // Kita format jadi Key-Value Pair: {'2023-12-01': 2, '2023-12-05': 5}
                return [Carbon::parse($item->booking_date)->format('Y-m-d') => $item->total];
            });

        return Inertia::render('Bookings/Create', [
            'service' => $service,
            // Kita kirim variabel ini. Tanggal yang ada di sini akan merah/disable.
            // Tanggal yang bookingnya cuma 1-4 TIDAK akan ada di sini, jadi bisa dipilih.
            'bookedDates' => $providerSchedule,
            // KIRIM DATA FEE KE FRONTEND
            'adminFee' => $this->currentSystemFee,
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
            'payment_method' => 'required|in:manual,gateway', // <--- WAJIB DITAMBAH
        ]);

        $service = Service::findOrFail($validated['service_id']);

        // LOGIKA BARU: Cek Kuota
        $existingBookingsCount = \App\Models\Booking::where('service_id', $service->id)
            ->where('booking_date', $validated['booking_date'])
            ->whereIn('status', ['unpaid', 'pending', 'paid', 'confirmed', 'in_progress', 'waiting_completion', 'completed'])
            ->count();

        if ($existingBookingsCount >= 5) {
            return back()
                ->withErrors(['booking_date' => 'Kuota penuh.']) // Tetap kasih merah di input
                ->with('error', 'Gagal membuat booking. Kuota tanggal tersebut penuh.'); // Tambahan popup merah di atas
        }

        $adminFee = 0;
    
        if ($request->payment_method === 'gateway') {
            // Ambil dari konfigurasi saat ini
            $adminFee = $this->currentSystemFee; 
        }

        // Tentukan Status Awal
        $initialStatus = 'pending'; // Default untuk Manual (Menunggu Konfirmasi)

        if ($request->payment_method === 'gateway') {
            $initialStatus = 'pending';
        }

        $booking = Booking::create([
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
            'admin_fee'     => $adminFee,
            'final_price' => null, // Biarkan kosong dulu
            'payment_method' => $request->payment_method, // 'manual'
            'status' => $initialStatus, // Menunggu Provider Konfirmasi
            'payment_status' => 'unpaid',
            'snap_token' => null,
        ]);

        // // Redirect Logic
        // if ($initialStatus === 'unpaid') {
        //     // Nanti: Redirect ke halaman pembayaran
        //     return redirect()->route('bookings.payment', $booking); 
        // }
        // 1. Tentukan penerima: Pemilik Jasa (Service Provider)
        // Asumsi: Booking berelasi dengan Service, Service berelasi dengan User (Provider)
        $serviceProvider = $booking->service->user; 

        // 2. Kirim Notifikasi hanya jika yang booking BUKAN pemilik jasa sendiri (untuk testing aman)
        if ($serviceProvider->id !== auth()->id()) {
            $serviceProvider->notify(new NewBookingNotification($booking));
        }
        
        // --- LOGIC NOTIFIKASI END ---


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
        // 1. Cek Hak Akses (Opsional)
        // if (auth()->id() !== $booking->provider_id && auth()->id() !== $booking->customer_id) abort(403);

        $status = $request->status;

        // ----------------------------------------------------
        // KONDISI A: JIKA STATUSNYA 'CONFIRMED' (Logika Approve)
        // ----------------------------------------------------
        if ($status === 'confirmed') {
            
            // Cek Authorisasi: Hanya Provider yang boleh confirm
            if (auth()->id() !== $booking->provider_id) abort(403);

            // LOGIKA BARU: CEK APAKAH SUDAH ADA FINAL PRICE (HASIL EDIT)?
            if (!empty($booking->final_price) && $booking->final_price > 0) {
                
                // --- SKENARIO 1: SUDAH DIEDIT (Final Price Ada) ---
                // Cukup ubah statusnya saja, JANGAN timpa harganya.
                $booking->update([
                    'status' => 'confirmed'
                ]);

                $finalPrice = $booking->final_price; // Ambil untuk pesan notifikasi
            
            } else {

                // --- SKENARIO 2: FRESH BOOKING (Final Price Kosong) ---
                // Lakukan perhitungan matematika (Initial + Fee)

                // Validasi Harga
                $request->validate([
                    'agreed_price' => 'required|numeric|min:10000'
                ]);

                // A. Ambil Harga & Fee
                $newServicePrice = floatval($request->agreed_price);
                $currentAdminFee = floatval($booking->admin_fee ?? 0);

                // [FAILSAFE] Koreksi Admin Fee jika 0 tapi Gateway
                if ($booking->payment_method === 'gateway' && $currentAdminFee <= 0) {
                    $currentAdminFee = $this->currentSystemFee; 
                }
                
                // Koreksi Manual
                if ($booking->payment_method === 'manual') {
                    $currentAdminFee = 0;
                }

                // Hitung Total
                $finalPrice = $newServicePrice + $currentAdminFee;

                // Update Data Harga & Status
                $booking->update([
                    'initial_price' => $newServicePrice,
                    'admin_fee'     => $currentAdminFee,
                    'final_price'   => $finalPrice,
                    'status'        => 'confirmed',
                ]);
            }

            // Reset Token Midtrans (Berlaku untuk kedua skenario jika status berubah ke confirmed)
            // Token lama dihapus agar user generate token baru dengan status/harga yang fix
            $booking->update(['snap_token' => null]);

            $message = 'Pesanan diterima. Harga deal: ' . number_format($finalPrice);
        } 
        
        // ----------------------------------------------------
        // KONDISI B: STATUS LAINNYA 
        // ----------------------------------------------------
        else {
            $booking->update(['status' => $status]);
            $message = 'Status pesanan diperbarui menjadi ' . $status;
        }

        // --- UPDATE NOTIFIKASI DI SINI ---
        
        // Logic: Kirim notifikasi ke PIHAK LAWAN (The Other Party)
        // Jika yang klik tombol adalah Provider, kirim ke Customer.
        // Jika yang klik tombol adalah Customer, kirim ke Provider.
        
        $recipient = null;
        if (auth()->id() === $booking->provider_id) {
            $recipient = $booking->customer;
        } elseif (auth()->id() === $booking->customer_id) {
            $recipient = $booking->provider;
        }

        if ($recipient) {
            $recipient->notify(new BookingStatusUpdatedNotification($booking));
        }

        // ----------------------------------------------------
        // 2. BROADCAST EVENT
        // ----------------------------------------------------
        broadcast(new BookingStatusUpdated($booking))->toOthers();

        return back()->with('message', $message);
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
            return redirect()->route('bookings.show', $booking)
                ->with('error', 'Pesanan tidak bisa diedit karena sudah diproses.');
        }

        // 1. Load Relasi Service & Provider
        $booking->load(['service.user', 'service.galleries', 'service.category']);

        // 2. Ambil Jadwal Provider (KECUALI Booking ini sendiri)
        $providerId = $booking->service->user_id;

        $bookedDates = \App\Models\Booking::where('provider_id', $providerId)
            ->where('id', '!=', $booking->id) // <--- PENTING: Jangan hitung diri sendiri
            ->whereIn('status', ['unpaid', 'pending', 'paid', 'confirmed', 'in_progress', 'waiting_completion', 'rejected'])
            ->select('booking_date', DB::raw('count(*) as total'))
            ->groupBy('booking_date')
            ->get()
            ->mapWithKeys(function ($item) {
                // Pastikan format Y-m-d
                return [\Carbon\Carbon::parse($item->booking_date)->format('Y-m-d') => $item->total];
            });

        return Inertia::render('Bookings/Edit', [
            'booking' => $booking,
            'bookedDates' => $bookedDates,
            // KIRIM DATA FEE KE FRONTEND
            'adminFee' => $this->currentSystemFee,
        ]);
    }

    public function update(Request $request, Booking $booking)
    {
        // 1. Cek Hak Akses & Status
        if (Auth::id() !== $booking->customer_id) abort(403);
        if (!in_array($booking->status, ['pending', 'rejected'])) abort(403);

        // 2. Validasi Input (offer_price diganti revised_price)
        $validated = $request->validate([
            'booking_date'   => 'required|date|after_or_equal:today',
            'booking_time'   => 'required',
            'location'       => 'required|string',
            'latitude'       => 'required|numeric',
            'longitude'      => 'required|numeric',
            'notes'          => 'nullable|string',
            'revised_price'  => 'required|numeric|min:0', // <--- GANTI NAMA
            'payment_method' => 'required|in:manual,gateway',
        ]);

        // 3. LOGIKA ADMIN FEE
        $newPaymentMethod = $validated['payment_method'];
        $oldPaymentMethod = $booking->payment_method;
        $storedFee        = floatval($booking->admin_fee ?? 0); 

        $adminFee = 0; 

        if ($newPaymentMethod === 'manual') {
            $adminFee = 0;
        } else { 
            if ($oldPaymentMethod === 'gateway') {
                $adminFee = $storedFee; // Pakai fee lama jika sudah ada
            } else {
                $adminFee = $this->currentSystemFee; // Pakai fee sistem baru
            }
        }

        // 4. HITUNG HARGA
        // revised_price adalah HARGA JASA BARU yang diinginkan user
        $revisedServicePrice = floatval($validated['revised_price']);
        
        // Total Akhir = Harga Revisi + Admin Fee
        $finalPrice = $revisedServicePrice + $adminFee;

        // 5. UPDATE DATABASE
        $booking->update([
            'booking_date'   => Carbon::parse($validated['booking_date'])->format('Y-m-d'),
            'booking_time'   => $validated['booking_time'],
            'location'       => $validated['location'],
            'latitude'       => $validated['latitude'],
            'longitude'      => $validated['longitude'],
            'notes'          => $validated['notes'],
            
            // HARGA:
            // 'initial_price' => ... JANGAN DIUPDATE! Biarkan tetap harga asli.
            'admin_fee'      => $adminFee,    
            'final_price'    => $finalPrice, // Simpan Total (Jasa Baru + Fee)
            
            'payment_method' => $validated['payment_method'] ?? $booking->payment_method,

            // Reset status ke pending jika sebelumnya rejected/pending
            'status' => 'pending', 
        ]);

        // 6. Reset Token Midtrans
        if ($booking->wasChanged('final_price') || $booking->wasChanged('payment_method')) {
            $booking->update(['snap_token' => null]);
        }

        // [TAMBAHAN BARU]
        // Kirim notifikasi ke Provider bahwa pesanan DIEDIT (masuk lagi sebagai pending)
        $booking->provider->notify(new NewBookingNotification($booking));

        // 7. Broadcast
        broadcast(new BookingStatusUpdated($booking))->toOthers();

        return redirect()->route('bookings.show', $booking)
            ->with('message', 'Pesanan berhasil diperbarui!');
    }

    public function storeReview(Request $request, Booking $booking)
    {
        // 1. Validasi
        $request->validate([
            'rating' => 'required|integer|min:1|max:5',
            'comment' => 'required|string|max:500',
            'images.*' => 'nullable|image|max:10240', // Max 10MB per foto
            'images' => 'nullable|array|max:3' // Maksimal 3 foto
        ]);

        $imagePaths = [];

        // 2. Upload Gambar (Jika ada)
        if ($request->hasFile('images')) {
            foreach ($request->file('images') as $file) {
                $filename = 'reviews/' . Str::random(20) . '.webp';
                
                // Resize & Convert (Optimization)
                $manager = Image::read($file);
                $encoded = $manager->scaleDown(width: 800) // Ukuran review tidak perlu HD
                                   ->toWebp(quality: 75);
                                   
                Storage::disk('public')->put($filename, (string) $encoded);
                $imagePaths[] = $filename;
            }
        }

        // 3. Simpan ke DB
        $review = Review::create([
            'booking_id' => $booking->id,
            'service_id' => $booking->service_id,
            'user_id'    => Auth::id(),
            'rating'     => $request->rating,
            'review'     => $request->comment,
            'images'     => $imagePaths // Simpan array path gambar
        ]);

        // --- TAMBAHAN NOTIFIKASI ---
        // Kirim notifikasi ke Provider Jasa
        $booking->provider->notify(new NewReviewNotification($review));

        broadcast(new ReviewSubmitted($review))->toOthers();

        return back()->with('message', 'Terima kasih atas ulasan Anda!');
    }

    // [BARU] Hapus Review
    public function destroyReview(Review $review)
    {
        // Pastikan yang hapus adalah pemilik review
        if (Auth::id() !== $review->user_id) abort(403);

        // Hapus file fisik gambar jika ada
        if ($review->images) {
            foreach ($review->images as $image) {
                Storage::disk('public')->delete($image);
            }
        }

        $review->delete(); // Soft delete atau Force delete tergantung kebutuhan

        return back()->with('message', 'Ulasan berhasil dihapus.');
    }

    public function updateReview(Request $request, Review $review)
    {
        // 1. Cek Hak Akses
        if (Auth::id() !== $review->user_id) abort(403);

        // 2. Validasi
        $request->validate([
            'rating' => 'required|integer|min:1|max:5',
            'comment' => 'required|string|max:500',
            'new_images.*' => 'nullable|image|max:5120', // Foto baru
            'deleted_images' => 'nullable|array', // Array path foto lama yang ingin dihapus
        ]);

        // 3. Ambil Array Gambar Saat Ini
        $currentImages = $review->images ?? [];

        // 4. Proses Hapus Gambar Lama (Jika user menghapus foto di form edit)
        if ($request->filled('deleted_images')) {
            foreach ($request->deleted_images as $imgToDelete) {
                // Hapus file fisik
                if (Storage::disk('public')->exists($imgToDelete)) {
                    Storage::disk('public')->delete($imgToDelete);
                }
                // Hapus dari array
                $currentImages = array_diff($currentImages, [$imgToDelete]);
            }
        }

        // 5. Cek Total Kuota Gambar (Sisa + Baru tidak boleh > 3)
        $newCount = $request->hasFile('new_images') ? count($request->file('new_images')) : 0;
        if (count($currentImages) + $newCount > 3) {
            return back()->withErrors(['new_images' => 'Maksimal total 3 foto per ulasan.']);
        }

        // 6. Proses Upload Gambar Baru
        if ($request->hasFile('new_images')) {
            foreach ($request->file('new_images') as $file) {
                $filename = 'reviews/' . Str::random(20) . '.webp';
                
                $manager = Image::read($file);
                $encoded = $manager->scaleDown(width: 800)->toWebp(quality: 75);
                                   
                Storage::disk('public')->put($filename, (string) $encoded);
                
                // Tambahkan path baru ke array
                $currentImages[] = $filename;
            }
        }

        // 7. Update Database
        $review->update([
            'rating' => $request->rating,
            'review' => $request->comment,
            'images' => array_values($currentImages) // Reindex array agar rapi (0, 1, 2)
        ]);

        return back()->with('message', 'Ulasan berhasil diperbarui!');
    }
    
    // public function approve(Request $request, Booking $booking)
    // {
    //     // 1. Cek Hak Akses
    //     if (auth()->id() !== $booking->provider_id) {
    //         abort(403);
    //     }

    //     // 2. Validasi Harga Jasa dari Provider
    //     $request->validate([
    //         'agreed_price' => 'required|numeric|min:10000'
    //     ]);

    //     // --- LOGIKA PERBAIKAN ---

    //     // A. Ambil Harga Jasa Baru (Kesepakatan)
    //     $newServicePrice = floatval($request->agreed_price);
        
    //     // B. Ambil Admin Fee yang tersimpan
    //     $currentAdminFee = floatval($booking->admin_fee ?? 0);

    //     // [FAILSAFE / PENGAMAN]
    //     // Jika ternyata di database feenya 0, TAPI metodenya Gateway,
    //     // Berarti ada yang salah saat save awal. Kita koreksi paksa di sini!
    //     if ($booking->payment_method === 'gateway' && $currentAdminFee <= 0) {
    //         $currentAdminFee = $this->currentSystemFee; // Ambil 4000 (atau sesuai config)
    //     }
        
    //     // C. Jika metode Manual, pastikan fee 0 (untuk jaga-jaga)
    //     if ($booking->payment_method === 'manual') {
    //         $currentAdminFee = 0;
    //     }

    //     // D. Hitung Total Akhir
    //     $finalPrice = $newServicePrice + $currentAdminFee;

    //     // 3. UPDATE DATABASE
    //     $booking->update([
    //         'initial_price' => $newServicePrice, // Update harga jasa
    //         'admin_fee'     => $currentAdminFee, // Update fee (jaga-jaga tadi dikoreksi)
    //         'final_price'   => $finalPrice,      // Total benar
    //         'status'        => 'confirmed',
    //     ]);

    //     // 4. Reset Token (Wajib karena harga berubah)
    //     if ($booking->wasChanged('final_price')) {
    //         $booking->update(['snap_token' => null]);
    //     }

    //     return back()->with('message', 'Pesanan diterima. Harga deal: ' . number_format($finalPrice));
    // }

    // UBAH parameter: Terima $hashId string, bukan langsung Model Binding
    public function pay(Request $request, $hashId)
    {
        // 1. DECODE HASH ID SECARA MANUAL (Lebih Aman)
        $decoded = Hashids::decode($hashId);
        $bookingIdInt = $decoded[0] ?? null;

        if (!$bookingIdInt) {
            return response()->json(['error' => 'ID Booking tidak valid.'], 404);
        }

        // 2. AMBIL DATA BOOKING
        $booking = Booking::find($bookingIdInt);

        if (!$booking) {
            return response()->json(['error' => 'Data Booking tidak ditemukan.'], 404);
        }

        // 3. VALIDASI USER (KEAMANAN)
        if (auth()->id() !== $booking->customer_id) {
            return response()->json(['error' => 'Unauthorized access.'], 403);
        }

        // 4. VALIDASI STATUS & HARGA
        // Pastikan status_payment logic Anda benar. Biasanya 'unpaid' atau 'pending'.
        if ($booking->payment_status === 'paid') {
            return response()->json(['error' => 'Pesanan ini sudah dibayar lunas.'], 400);
        }

        if ($booking->final_price <= 0) {
            return response()->json(['error' => 'Harga Final tidak valid (0 atau kosong).'], 400);
        }

        // 5. CEK SNAP TOKEN LAMA (OPTIMASI)
        // Jika token masih berlaku, pakai yang lama saja agar tidak spam ke Midtrans
        if ($booking->snap_token) {
            return response()->json(['snap_token' => $booking->snap_token]);
        }

        // 6. KONFIGURASI MIDTRANS
        // Pastikan key ini sesuai dengan file config/services.php Anda
        Config::$serverKey = config('services.midtrans.server_key');
        Config::$isProduction = config('services.midtrans.is_production');
        Config::$isSanitized = true;
        Config::$is3ds = true;

        if (!Config::$serverKey) {
            return response()->json(['error' => 'Server Key Midtrans belum dikonfigurasi.'], 500);
        }

        // 7. SIAPKAN PARAMETER (PAYLOAD)
        // [FIX UTAMA]: Gunakan $booking->hash_id atau $booking->id, JANGAN object $booking
        $orderId = 'BOOK-' . ($booking->hash_id ?? $booking->id) . '-' . time();
        
        $amountToPay = (int) $booking->final_price; // Pastikan Integer

        $params = [
            'transaction_details' => [
                'order_id' => $orderId,
                'gross_amount' => $amountToPay,
            ],
            'customer_details' => [
                'first_name' => auth()->user()->name,
                'email' => auth()->user()->email,
                'phone' => auth()->user()->phone ?? '08123456789',
            ],
            'item_details' => [[
                'id' => $booking->service_id,
                'price' => $amountToPay,
                'quantity' => 1,
                'name' => 'Jasa Booking #' . ($booking->hash_id ?? $booking->id),
            ]]
        ];

        try {
            // 8. REQUEST KE MIDTRANS
            $snapToken = Snap::getSnapToken($params);
            
            if (!$snapToken) {
                return response()->json(['error' => 'Gagal mendapatkan token dari Midtrans.'], 500);
            }

            // 9. SIMPAN TOKEN
            $booking->update(['snap_token' => $snapToken]);
            
            return response()->json(['snap_token' => $snapToken]);

        } catch (\Exception $e) {
            // Log error asli untuk developer (di storage/logs/laravel.log)
            \Illuminate\Support\Facades\Log::error('Midtrans Error: ' . $e->getMessage());
            
            return response()->json(['error' => 'Terjadi kesalahan gateway pembayaran: ' . $e->getMessage()], 500);
        }
    }

    public function confirmPayment(Booking $booking)
    {
        // 1. Cek Hak Akses (Hanya Provider)
        if (auth()->id() !== $booking->provider_id) abort(403);

        // 2. Cek apakah booking valid untuk dibayar
        if ($booking->status !== 'confirmed') {
            return back()->with('error', 'Pesanan harus status confirmed untuk konfirmasi pembayaran.');
        }

        // 3. Update Status Pembayaran
        $booking->update([
            'payment_status' => 'paid'
        ]);

        // Opsional: Kirim notifikasi ke customer "Pembayaran Diterima"
        // --- TAMBAHAN NOTIFIKASI ---
        $booking->customer->notify(new PaymentConfirmedNotification($booking));

        return back()->with('message', 'Pembayaran manual berhasil dikonfirmasi.');
    }

}