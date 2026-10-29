# PROPOSAL PENGAJUAN PROYEK 3 (TUGAS AKHIR / CAPSTONE PROJECT)

**JUDUL PROYEK:**  
**OPTIMALISASI ALGORITMA DAN IMPLEMENTASI SPLIT PAYMENT MIDTRANS PADA WEBSITE FINDSERVICES**

---

## LEMBAR PERNYATAAN KONTRIBUSI

Saya menyatakan bahwa proposal ini disusun untuk proyek yang menjadi tanggung jawab saya. Apabila terdapat kolaborasi, pustaka, template, API, kode pihak ketiga, atau alat AI generatif, penggunaannya akan dijelaskan secara transparan. Saya bersedia menunjukkan bukti kontribusi dan mempertanggungjawabkan rancangan serta implementasi proyek di hadapan dosen pembimbing/penguji.

### 1. Pernyataan Kontribusi: Mohammad Isa Widianto

| Identitas | Isian |
| :--- | :--- |
| **Nama / NIM** | **Mohammad Isa Widianto / 714240013** |
| **Judul Proyek** | **Optimalisasi Algoritma dan Implementasi Split Payment Midtrans pada Website FindServices** |
| **Ruang Lingkup Kontribusi** | 1. **Perancangan Arsitektur Transaksi Finansial:** Merancang alur transaksi *multi-party payment* berbasis *escrow hold* dan *automated disbursement* antara Pelanggan, Platform, dan Mitra Penyedia Jasa.<br>2. **Implementasi Midtrans Snap API:** Mengembangkan integrasi tokenisasi pembayaran *Snap Token* di backend Laravel (`BookingController`), konfigurasi payload transaksi, serta integrasi UI modal pembayaran (*Snap Popup*) di frontend Vue.js/Inertia.js.<br>3. **Implementasi Midtrans Iris API (Disbursement Engine):** Merancang dan mengimplementasikan mekanisme pencairan dana otomatis (*automated payout*) ke rekening bank atau dompet digital mitra saat status pekerjaan divalidasi selesai (`completed`).<br>4. **Sistem Perhitungan Bagi Hasil (*Revenue Sharing*):** Mengembangkan logika pemotongan otomatis komisi platform (*system/admin fee*) dan pencatatan buku besar transfer (*payout ledger/transaction history*) di basis data.<br>5. **Keamanan Webhook & Callback:** Memperkuat keamanan `PaymentCallbackController` melalui verifikasi enkripsi tanda tangan digital *SHA-512 signature key*, proteksi serangan *replay attack*, serta penerapan *idempotency check* guna mencegah risiko pembayaran ganda (*double-payout*).<br>6. **Modul Pengaturan Finansial Mitra:** Membangun antarmuka pengelolaan rekening bank/dompet digital mitra penyedia jasa.<br>7. **Pengujian Sistem Pembayaran:** Melakukan *Black-Box Testing* alur pemesanan dan simulasi siklus transaksi finansial menyeluruh pada lingkungan *Midtrans Sandbox*. |
| **Rencana Penggunaan Sumber/Alat Pihak Ketiga** | 1. **Pustaka & SDK Pihak Ketiga:** Menggunakan pustaka resmi `midtrans/midtrans-php` untuk komunikasi API Midtrans Snap, `guzzlehttp/guzzle` untuk pemanggilan HTTP client endpoint Midtrans Iris API, dan `vinkla/hashids` untuk enkripsi ID transaksi; diungkapkan melalui deklarasi dependensi pada berkas `composer.json`.<br>2. **Layanan Pihak Ketiga:** Layanan *Payment Gateway* dan *Disbursement Engine* Midtrans (Sandbox Environment); seluruh kredensial rahasia (*Server Key, Client Key, Iris Merchant Key*) diungkapkan dan dikelola aman melalui variabel lingkungan `.env`.<br>3. **Framework & Pustaka UI:** Kerangka kerja Laravel 12 dan pustaka Tailwind CSS untuk perancangan antarmuka transaksi; struktur kode dan komponen diungkapkan secara terbuka dalam repositori.<br>4. **Alat AI Generatif:** Menggunakan asisten AI (Google Antigravity / Gemini) secara etis untuk membantu penulisan kode kerangka awal (*boilerplate code*), telaah sintaks dokumentasi SDK Midtrans, dan *code review* keamanan; seluruh logika bisnis, validasi webhook, dan integrasi diuji, diverifikasi, dan dipertanggungjawabkan secara mandiri. |
| **Tanggal dan Tanda Tangan** | 22 Oktober 2026<br><br><br><br><br>**(Mohammad Isa Widianto)** |

<br>

### 2. Pernyataan Kontribusi: Faidil Zahpar

| Identitas | Isian |
| :--- | :--- |
| **Nama / NIM** | **Faidil Zahpar / 714240007** |
| **Judul Proyek** | **Optimalisasi Algoritma dan Implementasi Split Payment Midtrans pada Website FindServices** |
| **Ruang Lingkup Kontribusi** | 1. **Audit & Analisis Algoritma Eksisting:** Melakukan analisis beban komputasi dan profil latensi pada fitur pencarian teks berbasis `LIKE '%query%'` dan komputasi trigonometri *Haversine Formula* tanpa indeks pada berkas `SearchController.php` dan `MarketplaceController.php`.<br>2. **Implementasi Optimasi Pencarian Teks:** Merancang dan mengimplementasikan *MySQL Full-Text Search (Natural Language Mode)* dengan pembuatan struktur *Inverted Index* pada kolom `title` dan `description` tabel `services` untuk menghasilkan nilai relevansi teks secara instan.<br>3. **Implementasi Optimasi Geospasial (Bounding Box):** Merancang fungsi penyaringan awal berbasis kotak batas koordinat bujur dan lintang (*Bounding Box Pre-Filtering*) sebelum eksekusi rumus *Haversine* guna memangkas *Full Table Scan* dan menurunkan beban komputasi CPU basis data secara signifikan.<br>4. **Formulasi & Implementasi Multi-Criteria Weighted Ranking:** Merumuskan model perankingan hibrida terbobot dengan mengintegrasikan tiga variabel: skor relevansi teks ($S_{\text{text}}$), skor kedekatan jarak lokasi ($S_{\text{distance}}$), dan skor reputasi rating terbobot (*Bayesian Weighted Average Rating* - $S_{\text{rating}}$).<br>5. **Pengembangan Antarmuka Penyaringan Dinamis:** Membangun dan mengoptimalkan antarmuka filter pencarian multikriteria di halaman Marketplace menggunakan Vue.js 3 dan Inertia.js.<br>6. **Pengujian & Benchmarking Algoritma:** Merancang skenario pengujian performa (*Performance Benchmarking*) serta mengukur perbandingan waktu eksekusi kueri (*Query Latency*) dan penggunaan memori antara algoritma lama vs algoritma teroptimasi menggunakan dataset simulasi (skala 100 hingga 5.000 record jasa). |
| **Rencana Penggunaan Sumber/Alat Pihak Ketiga** | 1. **Fitur & Mesin Basis Data:** Mengoptimalkan fitur bawaan MySQL 8.0+ berupa *Full-Text Index*, indeks komposit geospasial numerik, serta ekspresi matematika kueri; diungkapkan melalui berkas *Laravel Database Migrations* (`database/migrations`).<br>2. **ORM & Query Builder:** Menggunakan Laravel Eloquent ORM dan Query Builder (`selectRaw`, `whereRaw`, subquery) untuk mengeksekusi kueri teroptimasi; diungkapkan secara eksplisit pada berkas pengontrol pencarian.<br>3. **Alat Uji & Benchmarking:** Memanfaatkan alat pengujian kinerja seperti Laravel Telescope / Apache Benchmark / Microtime Profiler untuk merekam data kuantitatif latensi kueri; metodologi dan hasil pengukuran diungkapkan transparan dalam bab hasil dan pembahasan.<br>4. **Pustaka Komponen UI:** Menggunakan komponen Vue.js 3 (Composition API) dan library antarmuka yang telah terpasang; diungkapkan dalam struktur direktori `resources/js`.<br>5. **Alat AI Generatif:** Menggunakan asisten AI (Google Antigravity / Gemini) secara etis untuk membantu formulasi formula matematis normalisasi skor dan skenario pembuatan data uji (*dummy seeder*); implementasi kueri basis data dan analisis hasil benchmarking dikerjakan dan dipertanggungjawabkan secara mandiri. |
| **Tanggal dan Tanda Tangan** | 22 Oktober 2026<br><br><br><br><br>**(Faidil Zahpar)** |

---

## RINGKASAN

Perkembangan ekonomi digital mendorong tingginya kebutuhan masyarakat terhadap akses penyedia jasa lokal secara cepat, aman, dan transparan. *FindServices* hadir sebagai platform *marketplace* berbasis web (menggunakan ekosistem Laravel, Vue.js, dan MySQL) yang mempertemukan pelanggan (*customer*) dengan penyedia jasa (*service provider*). Namun, dalam evaluasi sistem berjalan, ditemukan dua permasalahan fundamental yang membatasi skalabilitas dan efisiensi platform. Pertama, algoritma pencarian dan penemuan jasa saat ini masih mengandalkan pencocokan teks sederhana (*pattern matching* SQL `LIKE`) dan komputasi jarak *Haversine Formula* yang dieksekusi secara mentah (*raw query*) tanpa indeks geospasial serta belum mempertimbangkan pembobotan multi-kriteria (relevansi kata kunci, jarak kedekatan, serta rekam jejak *rating*), sehingga waktu respons melambat seiring pertumbuhan data dan hasil pencarian kurang akurat. Kedua, sistem transaksi pembayaran saat ini masih bertumpu pada penampungan dana ke satu rekening utama (*single merchant* Midtrans Snap), yang mengharuskan proses pembagian komisi platform (*platform fee*) dan penyaluran hak pendapatan mitra jasa (*provider payout*) dilakukan secara manual, rawan kesalahan manusia (*human error*), serta memperlambat penyelesaian transaksi (*settlement*). Berdasarkan permasalahan tersebut, penelitian dan pengembangan Proyek 3 ini bertujuan untuk melakukan optimasi menyeluruh pada algoritma pencarian dan komputasi spasial, serta merancang dan mengimplementasikan mekanisme *split payment* otomatis terintegrasi Midtrans pada platform *FindServices*.

Untuk menyelesaikan permasalahan tersebut, solusi yang ditawarkan berlandaskan kajian pustaka mencakup dua pilar utama. Pada pilar optimasi algoritma, diterapkan model perankingan hibrida multi-kriteria (*Multi-Criteria Weighted Ranking*) yang menggabungkan *Full-Text Search Relevance Scoring*, *Pre-filtered Bounding Box* pada komputasi *Haversine Formula* untuk memangkas beban pemrosesan geospasial, serta normalisasi rata-rata ulasan (*Bayesian weighted rating*), guna menyajikan urutan rekomendasi jasa yang paling relevan dan presisi dengan beban latensi query yang minimal. Pada pilar transaksi finansial, diterapkan arsitektur *split payment* dan *automated disbursement* terintegrasi Midtrans (memanfaatkan Midtrans Snap untuk pembayaran konsumen berfitur *escrow hold* dan Midtrans Iris API untuk penyaluran dana otomatis ke rekening mitra setelah pesanan berstatus selesai/*completed*), yang memisahkan pendapatan bersih mitra dan komisi admin platform secara *real-time*, aman, dan akuntabel. Pelaksanaan proyek ini menggunakan metodologi *Agile Development* yang meliputi tahapan: (1) Analisis kebutuhan sistem dan audit performa algoritma eksisting; (2) Perancangan arsitektur sistem, skema basis data, dan model pembobotan algoritma; (3) Implementasi teknis optimasi algoritma serta integrasi API *split payment* dan *webhook security*; (4) Pengujian komprehensif mencakup *Black-Box Testing* untuk validasi fungsional, pengujian *Stress/Benchmark Query Latency* untuk mengukur efisiensi algoritma, dan pengujian keandalan *webhook* serta transaksi pembayaran; dan (5) Dokumentasi serta evaluasi hasil akhir. Diharapkan luaran proyek ini menghasilkan platform *FindServices* yang berkinerja tinggi, berdaya saing, dan siap diadopsi secara komersial.

**Kata Kunci:** *FindServices, Optimalisasi Algoritma, Haversine Formula, Multi-Criteria Ranking, Split Payment, Midtrans Iris, Marketplace Jasa.*

---

## BAB I: PENDAHULUAN

### 1.1 Latar Belakang
Transformasi digital telah mengubah lanskap transaksi jasa sektor informal dan profesional di Indonesia. Platform *marketplace* jasa menjadi jembatan krusial antara masyarakat yang memerlukan layanan jasa (seperti teknisi, servis elektronik, kebersihan, perawatan diri, hingga perbaikan rumah tangga) dengan para penyedia jasa mandiri (*service provider*). Dalam menjawab tantangan tersebut, platform **FindServices** telah dibangun menggunakan arsitektur web modern berbasis *Laravel*, *Inertia.js (Vue.js)*, *MySQL*, *Laravel Reverb (WebSocket)*, dan integrasi awal pembayaran digital menggunakan *Midtrans Snap*.

Meskipun fondasi fungsional *FindServices* telah terbentuk, analisis teknis mendalam terhadap sistem eksisting menunjukkan adanya kesenjangan (*gap*) performa dan fungsionalitas yang menghambat skalabilitas sistem ketika volume data dan transaksi meningkat, khususnya pada dua ranah utama:

1. **Kelemahan dan Ketidakefisienan Algoritma Eksisting:**
   - **Algoritma Pencarian dan Perankingan Teks:** Fitur pencarian saat ini (`SearchController` dan `MarketplaceController`) masih menggunakan klausa SQL sederhana `LIKE '%query%'` dengan pengurutan mutlak berdasarkan tanggal pembuatan (`latest()`). Metode ini memiliki kompleksitas tinggi pada basis data berskala menengah hingga besar (*full table scan*), rentan menimbulkan latensi tinggi, serta tidak memiliki mekanisme pengukuran derajat relevansi (*relevance scoring*). Pengguna sering kali disajikan hasil yang kurang kontekstual dengan kebutuhan mereka.
   - **Beban Komputasi Geolokasi (*Haversine Formula*):** Pencarian berbasis radius saat ini mengeksekusi perhitungan trigonometri *Haversine* langsung pada seluruh baris tabel jasa tanpa mekanisme penyaringan awal (*spatial pre-filtering* atau *bounding box*). Hal ini menyebabkan utilisasi CPU basis data meningkat drastis seiring bertambahnya jumlah penyedia jasa yang terdaftar.
   - **Belum Ada Model Pembobotan Terpadu:** Sistem belum mengintegrasikan variabel jarak lokasi, relevansi kata kunci, histori reputasi (*rating & review*), dan ketersediaan slot kuota provider ke dalam satu fungsi skor matematis terpadu untuk merekomendasikan jasa terbaik bagi pengguna.

2. **Ketiadaan Mekanisme *Split Payment* pada Alur Transaksi Finansial:**
   - Sebagai platform *multi-sided marketplace*, *FindServices* bertindak sebagai fasilitator transaksi antara dua entitas independen (Pelanggan dan Penyedia Jasa). Saat ini, integrasi Midtrans Snap yang diterapkan masih bersifat rekening tunggal penampung (*single merchant gateway*), di mana seluruh pembayaran pelanggan (biaya jasa ditambah biaya admin platform) masuk ke satu rekening penampungan pengelola.
   - Konsekuensinya, pembagian hak pendapatan bersih penyedia jasa (*provider share*) dan komisi keuntungan platform (*platform fee*) masih harus dihitung dan ditransfer secara manual oleh administrator setelah pekerjaan selesai. Skema manual ini menimbulkan sejumlah risiko serius, antara lain: beban operasional rekonsiliasi finansial yang lambat, kerentanan terhadap *human error*, potensi keterlambatan pencairan dana bagi mitra penyedia jasa, serta risiko ketidaktransparanan pencatatan arus kas perantara.
   - Ketiadaan pemisahan dana otomatis (*split payment / disbursement*) juga berpotensi menimbulkan kendala kepatuhan regulasi finansial di mana platform yang bukan lembaga keuangan dilarang menahan dana pihak ketiga dalam waktu lama tanpa mekanisme distribusi escrow yang terotomatisasi dan berizin.

Oleh karena itu, diperlukan proyek pengembangan lanjutan berupa **"OPTIMALISASI ALGORITMA DAN IMPLEMENTASI SPLIT PAYMENT MIDTRANS PADA WEBSITE FINDSERVICES"** sebagai fokus utama Proyek 3 ini guna mentransformasikan *FindServices* menjadi platform yang tangguh secara komputasi dan mandiri secara operasional finansial.

---

### 1.2 Rumusan Masalah
Berdasarkan latar belakang tersebut, rumusan masalah dalam Proyek 3 ini adalah:
1. Bagaimana mengoptimalkan algoritma pencarian dan komputasi geospasial *Haversine* pada website *FindServices* agar menghasilkan latensi eksekusi *query* yang lebih cepat dan efisien?
2. Bagaimana merancang dan menerapkan algoritma perankingan hibrida multi-kriteria (*Multi-Criteria Weighted Ranking*) yang menggabungkan relevansi kata kunci, kedekatan jarak, dan reputasi rating jasa secara objektif?
3. Bagaimana merancang dan mengimplementasikan sistem *split payment* otomatis terintegrasi API Midtrans (Snap dan Iris Disbursement) yang aman dan andal untuk memisahkan komisi platform dan hak pendapatan mitra penyedia jasa?
4. Bagaimana memastikan keandalan, integritas data transaksi, dan keamanan komunikasi *webhook* antara Midtrans dan sistem *FindServices* dari ancaman pemalsuan status (*tampering/spoofing*)?

---

### 1.3 Batasan Pengembangan (Ruang Lingkup)
Agar penelitian dan pengerjaan proyek ini terarah dan mendalam, ditetapkan batasan pengembangan sebagai berikut:
1. **Lingkup Sistem & Teknologi:**
   - Pengembangan dilakukan pada basis kode website *FindServices* dengan *stack* utama: *PHP 8.2+*, *Laravel 12 (Framework)*, *Inertia.js*, *Vue.js 3*, *Tailwind CSS*, dan *MySQL 8.0+*.
   - Komunikasi waktu-nyata (*realtime notification & chat*) tetap memanfaatkan *Laravel Reverb*.
2. **Lingkup Optimalisasi Algoritma:**
   - Optimalisasi pencarian dibatasi pada penerapan *MySQL Full-Text Search (Natural Language Mode / Boolean Mode)* dengan normalisasi bobot relevansi kata kunci.
   - Optimalisasi perhitungan geolokasi dibatasi pada penerapan teknik *Bounding Box Pre-Filtering* berbasis koordinat lintang dan bujur (*latitude/longitude*) sebelum komputasi *Haversine Formula* dijalankan, guna mengeliminasi data di luar radius secara dini.
   - Algoritma rekomendasi perankingan menerapkan model pembobotan linier terbobot (*Weighted Scoring Model*) dengan tiga parameter utama: *Relevance Score*, *Proximity Distance Score*, dan *Bayesian Weighted Rating Average*.
3. **Lingkup Pembayaran & Split Payment:**
   - Integrasi *gateway* pembayaran menggunakan Midtrans Environment (Sandbox untuk tahap pengujian dan simulasi produksi).
   - Skema *Split Payment* diimplementasikan menggunakan kombinasi **Midtrans Snap API** (untuk penampungan pembayaran pelanggan/escrow terproteksi) dan **Midtrans Iris API / Automated Disbursement** (untuk transfer otomatis pencairan dana bersih ke rekening bank atau dompet digital mitra penyedia jasa) yang dipicu secara otomatis saat pesanan jasa tervalidasi berstatus `completed`.
   - Pemotongan biaya sistem (*admin fee*) dihitung berdasarkan konfigurasi nominal tetap (*fixed fee*) dan/atau persentase komisi platform yang ditentukan oleh pengelola sistem.
4. **Lingkup Pengujian:**
   - Pengujian fungsionalitas menggunakan metode *Black-Box Testing*.
   - Pengujian performa algoritma dievaluasi melalui perbandingan *Execution Time (Query Latency)* antara algoritma lama (`LIKE %query%` + raw *Haversine*) versus algoritma hasil optimasi (*Indexed Full-Text + Bounding Box Haversine*).
   - Pengujian keamanan pembayaran dibatasi pada validasi *SHA-512 Signature Key*, pencegahan serangan *replay attack*, serta penanganan *concurrency/idempotency* pada *webhook callback*.

---

### 1.4 Tujuan Proyek
Tujuan yang ingin dicapai dalam pengembangan Proyek 3 ini mencakup tujuan umum dan tujuan khusus:

#### 1.4.1 Tujuan Umum
Mewujudkan website *marketplace* jasa *FindServices* yang memiliki performa pencarian tinggi, cerdas dalam menyajikan rekomendasi jasa lokal, serta memiliki sistem pengelolaan transaksi pembayaran yang terotomatisasi, aman, dan transparan melalui integrasi *split payment*.

#### 1.4.2 Tujuan Khusus
1. Mengembangkan dan menerapkan teknik optimasi pada algoritma geolokasi dan pencarian jasa untuk mereduksi waktu komputasi basis data (*query execution time*).
2. Merumuskan dan mengimplementasikan algoritma *Multi-Criteria Weighted Ranking* untuk meningkatkan akurasi dan kualitas perankingan penyedia jasa bagi pelanggan.
3. Merancang arsitektur dan mengimplementasikan mekanisme *Split Payment* otomatis menggunakan API Midtrans (Snap & Iris) sehingga pembagian antara pendapatan mitra dan komisi admin berjalan secara mandiri (*hands-free*) tanpa intervensi manual.
4. Mengamankan alur komunikasi pembayaran dengan menerapkan mekanisme verifikasi *signature*, *idempotent transaction handling*, dan *state machine* booking yang ketat untuk mencegah inkonsistensi data.
5. Mengevaluasi performa sistem melalui pengujian *benchmarking* latensi respon serta pengujian keandalan fungsional transaksi secara menyeluruh.

---

### 1.5 Manfaat Proyek
Pengembangan proyek ini diharapkan memberikan manfaat konkret bagi berbagai pihak:
1. **Bagi Pelanggan (*Customer*):**
   - Mendapatkan hasil pencarian penyedia jasa yang lebih cepat, tepat, dan relevan sesuai lokasi terdekat dan reputasi terbaik.
   - Merasa aman dalam bertransaksi karena pembayaran tersimpan dalam sistem *escrow* terproteksi hingga jasa tuntas dikerjakan.
2. **Bagi Penyedia Jasa (*Service Provider / Mitra*):**
   - Menerima hak bayaran secara transparan, pasti, dan tepat waktu secara otomatis ke rekening/dompet digital mereka tanpa menunggu proses transfer manual dari admin.
   - Peluang mendapatkan pesanan lebih adil berkat algoritma perankingan yang berbasis reputasi dan kedekatan jarak.
3. **Bagi Pengelola Platform (*Admin FindServices*):**
   - Mengeliminasi beban operasional rekonsiliasi manual dan transfer dana individual kepada ratusan mitra.
   - Pendapatan platform (*fee admin*) terakumulasi secara terpisah dan otomatis dengan audit pencatatan keuangan yang rapi.
   - Infrastruktur server lebih hemat sumber daya berkat optimasi query dan algoritma.
4. **Bagi Mahasiswa dan Akademisi:**
   - Menjadi rujukan ilmiah dan studi kasus implementasi nyata teknologi *FinTech (Split Payment/Disbursement Gateway)* dan optimasi algoritma geospasial pada aplikasi *marketplace* berbasis web modern.

---

## BAB II: KAJIAN PUSTAKA DAN LANDASAN TEORI

### 2.1 Kajian Pustaka (State-of-the-Art)
Sejumlah penelitian terdahulu menjadi landasan pijak dalam perancangan solusi pada proyek ini:

1. **Penelitian Algoritma Pencarian dan Perankingan Jasa:**
   Penelitian oleh Pratama dkk. (2022) mengenai sistem pencarian direktori layanan membuktikan bahwa penggunaan klausa `LIKE` pada SQL menyebabkan degradasi performa eksponensial ketika entri data melampaui 10.000 record. Penerapan *Full-Text Search* dengan pembobotan *TF-IDF* atau skor relevansi bawaan basis data relasional mampu memangkas waktu pemrosesan hingga 65% dibandingkan metode konvensional.
2. **Penelitian Optimasi Komputasi Geospasial:**
   Studi oleh Santoso & Rahardjo (2021) tentang aplikasi layanan berbasis lokasi (*Location-Based Services/LBS*) menunjukkan bahwa komputasi trigonometri *Haversine Formula* yang melibatkan fungsi `cos`, `sin`, dan `acos` memerlukan beban pemrosesan matematis intensif. Penelitian tersebut menyimpulkan bahwa penambahan filter *Bounding Box* (koordinat batas bujur dan lintang $\Delta lat, \Delta lon$) sebelum formula *Haversine* dijalankan dapat mengeliminasi lebih dari 80% baris data yang berada jauh di luar radius, sehingga mempercepat waktu kueri secara signifikan.
3. **Penelitian Integrasi Payment Gateway dan Split Payment pada Marketplace:**
   Kajian oleh Wibowo dkk. (2023) mengenai ekosistem platform multi-pihak menggarisbawahi bahwa kendala utama pertumbuhan platform rintisan adalah masalah kepercayaan finansial (*financial trust*). Penerapan gerbang pembayaran (*payment gateway*) berfitur *automated escrow* dan *split settlement* terbukti mengurangi tingkat pembatalan transaksi (*cancellation rate*) dan meningkatkan kepuasan mitra penyedia jasa karena adanya kepastian pencairan dana otomatis (*automated payout*).

---

### 2.2 Landasan Teori

#### 2.2.1 Konsep Multi-Sided Marketplace dan Layanan Berbasis Lokasi (LBS)
*Multi-sided platform* adalah model bisnis yang memfasilitasi interaksi dan pertukaran nilai ekonomi langsung antara dua kelompok pengguna atau lebih yang saling bergantung (*two-sided network effects*). Dalam konteks *FindServices*, platform menjembatani Pelanggan yang membutuhkan solusi jasa di satu sisi, dan Penyedia Jasa mandiri di sisi lain. 

Layanan Berbasis Lokasi (*Location-Based Services / LBS*) adalah layanan informasi yang dapat diakses melalui perangkat komputer atau telepon pintar menggunakan kemampuan geolokasi pengguna. Karakteristik jasa lokal menuntut bahwa jasa yang ditawarkan harus relevan secara fisik (jarak tempuh operasional yang terjangkau antara pelanggan dan penyedia jasa).

#### 2.2.2 Algoritma Pencarian Teks dan Full-Text Search
Pencarian teks menggunakan klausa konvensional `LIKE '%term%'` mengharuskan mesin basis data melakukan *Full Table Scan* karena penggunaan karakter *wildcard* di awal string menonaktifkan penggunaan indeks B-Tree standar. Sebaliknya, teknik *Full-Text Search (FTS)* membangun indeks terbalik (*Inverted Index*) dari setiap token kata yang unik dalam kolom dokumen.

Pada basis data MySQL, indeks *Full-Text* mengevaluasi relevansi dokumen terhadap kueri pencarian dalam mode bahasa alami (*Natural Language Mode*) berdasarkan frekuensi kemunculan kata kunci dan bobot keunikan kata dalam kumpulan dokumen (*document collection*), menghasilkan nilai skor relevansi kontinu:

$$\text{Relevance Score} = \sum_{t \in Q} \text{TF-IDF}(t, D)$$

Skor ini dapat diakses secara efisien melalui fungsi `MATCH(col1, col2) AGAINST('keyword' IN NATURAL LANGUAGE MODE)` tanpa membebani memori server.

#### 2.2.3 Algoritma Geospasial: Haversine Formula dan Bounding Box Optimization
*Haversine Formula* adalah persamaan navigasi penting yang digunakan untuk menghitung jarak lingkaran besar (*great-circle distance*) antara dua titik koordinat pada permukaan bola bumi berdasarkan garis lintang (*latitude*) dan garis bujur (*longitude*):

$$a = \sin^2\left(\frac{\Delta \varphi}{2}\right) + \cos(\varphi_1) \cdot \cos(\varphi_2) \cdot \sin^2\left(\frac{\Delta \lambda}{2}\right)$$

$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1 - a}\right)$$

$$d = R \cdot c$$

Di mana:
- $\varphi_1, \varphi_2$ : Lintang lokasi pelanggan dan lokasi penyedia jasa (dalam satuan radian).
- $\Delta \varphi = \varphi_2 - \varphi_1$ : Selisih garis lintang.
- $\Delta \lambda = \lambda_2 - \lambda_1$ : Selisih garis bujur.
- $R$ : Radius rata-rata kelengkungan bumi ($\approx 6.371\text{ km}$).
- $d$ : Jarak garis lurus antara dua titik koordinat (dalam satuan kilometer).

**Optimalisasi Bounding Box (Penyaringan Awal Segiempat):**  
Untuk menghindari eksekusi fungsi trigonometri berat pada seluruh baris di tabel `services`, dibuat batas persegi (*bounding box*) berdasarkan radius maksimum yang dicari ($r$ km):

$$\Delta \text{lat} = \frac{r}{R} \times \frac{180}{\pi}$$

$$\Delta \text{lon} = \frac{r}{R \cdot \cos(\text{lat}_{\text{user}} \times \frac{\pi}{180})} \times \frac{180}{\pi}$$

Kueri SQL menyaring koordinat penyedia jasa terlebih dahulu menggunakan indeks numerik standar:

$$\text{latitude} \in [\text{lat}_{\text{user}} - \Delta \text{lat}, \text{lat}_{\text{user}} + \Delta \text{lat}]$$
$$\text{longitude} \in [\text{lon}_{\text{user}} - \Delta \text{lon}, \text{lon}_{\text{user}} + \Delta \text{lon}]$$

Baris data yang lolos penyaringan kotak batas inilah yang kemudian dihitung jarak pastinya dengan rumus *Haversine*, menghasilkan reduksi pemrosesan hingga 70–90%.

#### 2.2.4 Algoritma Perankingan Multi-Kriteria (Multi-Criteria Weighted Ranking)
Untuk menyajikan rekomendasi terbaik, sistem menerapkan perankingan terbobot yang mengintegrasikan tiga dimensi evaluasi:
1. **Skor Relevansi Teks ($S_{\text{text}}$):** Dinormalisasi ke skala $[0, 1]$ dari hasil *Full-Text Match*.
2. **Skor Kedekatan Jarak ($S_{\text{distance}}$):** Dihitung berbanding terbalik dengan jarak ($d$), di mana jarak yang semakin dekat memberikan nilai skor yang mendekati 1:
   $$S_{\text{distance}} = \max\left(0, 1 - \frac{d}{r_{\text{max}}}\right)$$
3. **Skor Reputasi Rating Bayes ($S_{\text{rating}}$):** Menggunakan *Weighted Rating* untuk menghindari distorsi jasa baru dengan 1 ulasan bintang 5 mengalahkan jasa berperingkat 4.8 dengan ratusan ulasan:
   $$S_{\text{rating}} = \frac{v}{v + m} \cdot R_s + \frac{m}{v + m} \cdot C$$
   Di mana $v$ adalah jumlah ulasan jasa, $m$ adalah ambang batas minimum ulasan, $R_s$ adalah rata-rata rating jasa, dan $C$ adalah rata-rata rating seluruh jasa di platform.

Skor akhir ($S_{\text{final}}$) ditentukan melalui kombinasi linier terbobot:

$$S_{\text{final}} = (w_1 \cdot S_{\text{text}}) + (w_2 \cdot S_{\text{distance}}) + (w_3 \cdot S_{\text{rating}})$$

Dengan bobot normalisasi: $w_1 + w_2 + w_3 = 1.0$.

#### 2.2.5 Financial Technology, Payment Gateway, dan Midtrans Lifecycle
*Payment Gateway* adalah infrastruktur perantara yang mengotorisasi dan memproses transaksi finansial elektronik secara aman antara pihak pembeli, pedagang (*merchant*), dan lembaga perbankan/penerbit kartu/dompet digital. 

**Siklus Transaksi Midtrans:**
1. *Customer* membuat pesanan booking jasa yang disepakati (*deal price*).
2. Sistem *FindServices* menginisiasi *Order Transaction Request* ke API Midtrans Snap untuk menghasilkan *Snap Token* unik.
3. *Customer* melakukan pembayaran melalui *UI Payment Popup* (QRIS, GoPay, ShopeePay, Virtual Account Bank).
4. Server Midtrans mengirimkan sinyal notifikasi *HTTP POST (Webhook)* ke *endpoint* sistem `PaymentCallbackController`.
5. Sistem memvalidasi keaslian data menggunakan enkripsi *SHA-512 Signature Hash*:
   $$\text{Signature} = \text{SHA512}(\text{order\_id} + \text{status\_code} + \text{gross\_amount} + \text{ServerKey})$$
6. Jika *signature* valid dan status transaksi berstatus `capture` / `settlement`, status pembayaran booking diperbarui menjadi `paid` dan sistem menahan (*holds*) dana dalam skema *escrow platform*.

#### 2.2.6 Arsitektur Split Payment dan Automated Disbursement
Model *Split Payment* pada platform *marketplace* bertujuan untuk mendistribusikan nominal pembayaran bruto (*gross amount*) dari satu transaksi tunggal pelanggan ke dua pihak penerima yang berbeda:
1. **Platform Fee (Komisi Pengelola):** Sejumlah nominal tetap (misal Rp2.000,-) atau persentase komisi (misal 5-10%) yang menjadi pendapatan sah platform *FindServices*.
2. **Provider Net Share (Hak Penyedia Jasa):** Nilai sisa transaksi ($\text{Gross Amount} - \text{Platform Fee}$) yang menjadi hak mutlak penyedia jasa.

**Skema Implementasi (Midtrans Snap + Midtrans Iris API):**
Dalam ekosistem regulasi perbankan Indonesia, skema paling ideal bagi platform jasa adalah model *Escrow-to-Disbursement*:
- Pembayaran konsumen diterima secara utuh oleh akun induk platform melalui *Midtrans Snap*.
- Sistem mencatat pembagian hak di tabel basis data transaksi (`admin_fee` dan `provider_earnings`).
- Dana ditahan (*escrow hold*) hingga jasa selesai dikerjakan secara fisik dan dikonfirmasi tuntas oleh pelanggan (status pesanan berubah menjadi `completed`).
- Sistem mengeksekusi *API Call* ke **Midtrans Iris (Disbursement Engine)** secara *asynchronous* melalui *queue job Laravel* untuk mengirimkan dana hak penyedia jasa langsung ke rekening bank atau akun e-wallet mitra yang telah tervalidasi.
- Mekanisme ini mencegah penipuan jasa (*fraud*), menjamin mitra hanya dibayar jika pekerjaan selesai, dan menyelesaikan proses *payout* tanpa keterlibatan manual operator manusia.

#### 2.2.7 Kerangka Kerja Perangkat Lunak dan Realtime WebSocket
- **Laravel 12:** Kerangka kerja PHP modern dengan arsitektur MVC, fitur keamanan bawaan (*CSRF protection, Eloquent ORM, Database Transactions, Job Queues, Hashids obfuscation*), dan kinerja *routing* yang tinggi.
- **Inertia.js & Vue.js 3:** Pola arsitektur *Modern Monolith* yang memungkinkan pembangunan antarmuka dinamis reaktif menggunakan komponen Vue 3 (Composition API) tanpa perlu merancang arsitektur API RESTful terpisah yang kompleks.
- **Laravel Reverb:** Server WebSocket murni berbasis PHP berperforma tinggi yang menangani komunikasi *real-time* seperti *push notification* status pesanan dan pesan obrolan instan secara efisien.

---

## BAB III: METODOLOGI PENELITIAN DAN PENGEMBANGAN

### 3.1 Model Pengembangan Sistem
Pengembangan Proyek 3 ini menerapkan metodologi **Agile Development (Scrum Framework)** yang adaptif dan iteratif. Siklus pengembangan terdiri dari 5 tahapan berkesinambungan:

```
[1. Requirement & Audit] 
       │
       ▼
[2. System & Algorithm Design]
       │
       ▼
[3. Iterative Implementation (Sprint 1: Algoritma, Sprint 2: Split Payment)]
       │
       ▼
[4. Comprehensive Testing & Benchmarking]
       │
       ▼
[5. Evaluation, Deployment & Reporting]
```

1. **Tahap 1: Analisis Kebutuhan & Audit Sistem Eksisting (Requirement Analysis)**
   - Mengaudit kode eksisting pada `SearchController`, `MarketplaceController`, `BookingController`, dan `PaymentCallbackController`.
   - Mengukur *baseline latency* (waktu respons kueri pencarian lama dan beban komputasi Haversine).
   - Mengidentifikasi skema data rekening mitra dan kebutuhan integrasi kredensial Midtrans Iris API.

2. **Tahap 2: Perancangan Sistem & Algoritma (System & Algorithmic Design)**
   - Merancang rumus matematis perankingan *Multi-Criteria Weighted Ranking*.
   - Merancang migrasi skema basis data baru: indeks *Full-Text* pada tabel `services`, kolom nomor rekening/bank pada tabel `users`, dan tabel log *disbursement/split payment*.
   - Merancang diagram alir (*flowchart*), *Sequence Diagram*, dan *State Transition Machine* untuk transaksi *split payment*.

3. **Tahap 3: Implementasi Teknis (Implementation & Coding)**
   - **Sprint 1 (Optimasi Algoritma):**
     * Mengimplementasikan indeks *Full-Text* pada kolom `title` dan `description`.
     * Mengimplementasikan fungsi *Bounding Box Pre-Filtering* pada kueri geospasial *Haversine*.
     * Membangun fungsi kalkulasi skor hibrida pada *Search & Marketplace Query*.
   - **Sprint 2 (Split Payment & Midtrans Iris):**
     * Memperbarui antarmuka profil mitra untuk verifikasi rekening bank tujuan penarikan.
     * Mengonfigurasi integrasi API Midtrans Iris ke dalam sistem Laravel (menggunakan *GuzzleHttp / Midtrans SDK*).
     * Membangun *Queue Worker / Job Listener* otomatis yang mengeksekusi *payout request* saat pesanan berstatus `completed`.
     * Memperkuat keamanan *webhook callback* dengan verifikasi tanda tangan digital dan *idempotency check*.

4. **Tahap 4: Pengujian Sistem (System Testing & Benchmarking)**
   - **Black-Box Testing:** Menguji validitas fungsional alur booking, pembayaran Midtrans Snap, perubahan status pesanan, hingga eksekusi pencairan otomatis.
   - **Performance Benchmarking:** Menguji kecepatan respon sistem (*Response Time & Query Execution Latency*) menggunakan alat uji benchmarking (seperti Laravel Telescope, Apache Benchmark, atau k6) dengan dataset simulasi ribuan data jasa.
   - **Security & Concurrency Testing:** Menguji ketahanan *webhook* terhadap manipulasi parameter (*signature tampering*) dan mitigasi *double payout* (kondisi *race condition*).

5. **Tahap 5: Evaluasi dan Dokumentasi Akhir (Evaluation & Final Report)**
   - Menyusun dokumentasi teknis, buku panduan implementasi, dan laporan akhir Proyek 3.

---

### 3.2 Desain Alur Sistem dan Arsitektur Transaksi

#### 3.2.1 Diagram Alur Transaksi Split Payment (Escrow-to-Disbursement)
Alur transaksi *split payment* yang diimplementasikan dirancang mengikuti tahapan berikut:

```
[Customer]             [FindServices Web App]              [Midtrans Gateway / Iris]           [Service Provider]
    │                             │                                   │                                │
    │── 1. Buat Booking Jasa ────>│                                   │                                │
    │                             │── 2. Notifikasi Pesanan Masuk ────────────────────────────────────>│
    │                             │                                   │                                │
    │                             │<── 3. Konfirmasi Harga Deal ───────────────────────────────────────│
    │                             │                                   │                                │
    │── 4. Checkout Pembayaran ──>│                                   │                                │
    │                             │── 5. Request Snap Token ─────────>│                                │
    │                             │<── 6. Return Snap Token ──────────│                                │
    │                             │                                   │                                │
    │── 7. Bayar (QRIS/VA/EWallet)───────────────────────────────────>│                                │
    │                             │                                   │                                │
    │                             │<── 8. Webhook Notif (Settlement) ─│                                │
    │                             │   (Verifikasi SHA-512 Hash)       │                                │
    │                             │   (Ubah Status: 'paid' & ESCROW)  │                                │
    │                             │── 9. Notifikasi Pembayaran Lunas ─────────────────────────────────>│
    │                             │                                   │                                │
    │                             │                 [Pekerjaan Jasa Dilaksanakan]                      │
    │                             │                                   │                                │
    │── 10. Konfirmasi Selesai ──>│                                   │                                │
    │    (Status: 'completed')    │                                   │                                │
    │                             │── 11. Trigger Auto-Disbursement ─>│                                │
    │                             │    (Nominal = Total - Admin Fee)  │                                │
    │                             │                                   │── 12. Transfer Dana Bersih ───>│
    │                             │<── 13. Payout Status (Success) ───│                                │
    │                             │                                   │                                │
    │                             │── 14. Kirim Notifikasi Pencairan ─────────────────────────────────>│
```

---

### 3.3 Jadwal Rencana Kerja (Work Breakdown Schedule)
Pengerjaan Proyek 3 ini ditargetkan selesai dalam rentang waktu pelaksanaan (misalnya 4 hingga 5 bulan atau 1 semester akademik), dengan rincian jadwal sebagai berikut:

| No | Tahapan Kegiatan | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 |
|:--:|:-----------------|:-------:|:-------:|:-------:|:-------:|
| 1  | Pengumpulan data, audit sistem eksisting & perancangan proposal | ██████ |         |         |         |
| 2  | Perancangan skema basis data, algoritma perankingan & arsitektur API |         | ██████  |         |         |
| 3  | Implementasi Sprint 1: Optimasi Full-Text Search & Bounding Box Haversine |         | ██████  |         |         |
| 4  | Implementasi Sprint 2: Integrasi Midtrans Split Payment & Iris Disbursement |         |         | ██████  |         |
| 5  | Pengujian Fungsional, Benchmarking Latensi & Keamanan Webhook |         |         |         | ██████  |
| 6  | Analisis hasil pengujian, penyusunan laporan akhir & persiapan sidang |         |         |         | ██████  |

---

## BAB IV: KESIMPULAN PROPOSAL

Pengajuan Proyek 3 dengan judul **"OPTIMALISASI ALGORITMA DAN IMPLEMENTASI SPLIT PAYMENT MIDTRANS PADA WEBSITE FINDSERVICES"** ini merupakan langkah strategis dalam mentransformasikan platform *FindServices* dari fase purwarupa dasar menjadi platform *marketplace* jasa yang andal, berskala tinggi (*scalable*), dan mandiri secara operasional. 

Dengan memadukan optimalisasi algoritma pencarian hibrida (*Full-Text Search*), reduksi beban spasial *Haversine* menggunakan *Bounding Box*, serta pembobotan multi-kriteria berbasis rating dan kedekatan lokasi, sistem akan memberikan pengalaman pencarian yang jauh lebih responsif dan relevan bagi pengguna. Sementara itu, implementasi sistem *split payment* dan pencairan dana otomatis (*automated disbursement*) melalui integrasi API Midtrans menjadi solusi tuntas terhadap permasalahan beban rekonsiliasi manual dan risiko finansial platform, sekaligus memperkuat kepercayaan mitra penyedia jasa terhadap ekosistem *FindServices*.

Melalui metodologi pengembangan yang terstruktur serta instrumen pengujian performa yang komprehensif, proyek ini memiliki nilai akademis dan implementatif yang tinggi untuk diajukan sebagai karya Proyek 3 bagi mahasiswa Program Studi Teknik Informatika / Sistem Informasi.
