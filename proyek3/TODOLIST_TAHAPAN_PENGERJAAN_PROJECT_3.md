TODOLIST PROYEK 3: FindServices
(Optimalisasi Algoritma & Implementasi Alternatif Split Payment)

PEMBAGIAN PERAN
Faidil Zahpar: Pilar I (Optimalisasi Algoritma Pencarian & Perankingan)

Mohammad Isa Widianto: Pilar II (Eksplorasi & Integrasi Alternatif Split Payment/Disbursement)

CHECKLIST TAHAPAN PENGERJAAN
FASE 0: PERSIAPAN & DATABASE (Bersama)
[ ] Setup Git: Buat branch feature/algorithm dan feature/payment-alternative.

[ ] Migrasi Database: Tambahkan kolom rekening di users, detail harga/jarak di services, status payout di bookings, dan tabel baru payout_logs.

[ ] Seeder Data: Buat 100-5.000 data dummy jasa (lengkap dengan koordinat dan rating) untuk keperluan pengujian.

FASE 1: OPTIMALISASI ALGORITMA (Faidil)
[ ] Audit Awal: Catat metrik execution time dan memory peak dari kueri pencarian lama.

[ ] MySQL Full-Text Search: Terapkan indeks FULLTEXT pada tabel services dan ubah kueri LIKE menjadi MATCH() AGAINST().

[ ] Bounding Box Filtering: Terapkan pre-filter koordinat sebelum menggunakan rumus Haversine agar kalkulasi spasial lebih ringan.

[ ] Weighted Ranking: Gabungkan skor Relevansi Teks, Jarak, dan Rating Bayes ke dalam satu skor final (final_score).

[ ] Frontend & Benchmark: Perbarui UI halaman Marketplace dan lakukan perbandingan performa (algoritma lama vs baru) untuk data laporan.

FASE 2: PENGGANTI MIDTRANS IRIS & INTEGRASI (Isa)
[ ] Riset Pengganti Iris: Cari dan bandingkan alternatif payment gateway untuk disbursement/split payment (Contoh: Xendit XenDisburse, Oy! Indonesia, Flip for Business, atau sistem manual withdrawal approval).

[ ] Registrasi & Kredensial: Buat akun sandbox di layanan pengganti terpilih dan pasang API Key di .env.

[ ] Manajemen Rekening Mitra: Buat UI dan endpoint untuk menyimpan dan memvalidasi data rekening bank/e-wallet penyedia jasa.

[ ] Alur Transaksi & Escrow: Hitung final_price dan admin_fee. Tahan dana di platform (status pesanan in_progress) sebelum dicairkan.

[ ] Integrasi API Disbursement Baru: Buat Service Class untuk memicu pencairan otomatis (provider_earnings) saat pesanan selesai.

[ ] Keamanan Transaksi: Terapkan validasi Webhook/Callback, idempotency lock (cegah double transfer), dan simpan riwayat ke payout_logs.

FASE 3: INTEGRASI & PENGUJIAN AKHIR (Bersama)
[ ] Merge Repository: Gabungkan kode ke branch main dan atasi merge conflict.

[ ] End-to-End Testing: Simulasikan alur penuh: Cari Jasa -> Booking -> Bayar -> Pekerjaan Selesai -> Dana Cair ke Mitra.

[ ] Concurrency Testing: Uji klik ganda pada tombol "Pesanan Selesai" untuk memastikan tidak ada pencairan ganda (gunakan Atomic Lock).

FASE 4: LAPORAN & PRESENTASI (Bersama)
[ ] Penyusunan Bab IV: Masukkan grafik performa algoritma (Faidil) dan dokumentasi alur pembayaran gateway baru (Isa).

[ ] Persiapan Sidang: Siapkan akun demo (Customer, Mitra, Admin) dan siapkan dashboard sandbox gateway terpilih untuk live demo.