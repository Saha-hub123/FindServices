TUGAS MANDIRI

Topik: Eksplorasi dan Pemahaman Common Vulnerability Scoring System (CVSS) Version 4.0 Calculator



Tujuan Pembelajaran



Mahasiswa diharapkan mampu memahami prinsip penilaian tingkat keparahan kerentanan keamanan, mengenali fungsi setiap komponen CVSS v4.0, menginterpretasikan nilai metrik, membaca vector string, serta menganalisis perubahan skor melalui simulasi menggunakan kalkulator resmi FIRST.



Instruksi Tugas

Pelajari secara mandiri Common Vulnerability Scoring System Version 4.0 Calculator melalui situs resmi:



https://www.first.org/cvss/calculator/4.0



Lakukan eksplorasi secara menyeluruh terhadap fitur dan komponen kalkulator. Pemahaman tidak hanya berfokus pada cara memperoleh skor, tetapi juga pada alasan setiap metrik memiliki nilai tertentu dan bagaimana perubahan nilai tersebut memengaruhi hasil penilaian kerentanan.



Bagian A. Memahami Konsep CVSS v4.0

Pelajari dan jelaskan:

1. Pengertian, tujuan, dan manfaat CVSS dalam vulnerability assessment.
2. Perbedaan antara vulnerability, threat, risk, dan severity.
3. Fungsi empat kelompok metrik CVSS: Base, Threat, Environmental, dan Supplemental.
4. Perbedaan label skor CVSS-B, CVSS-BT, CVSS-BE, dan CVSS-BTE.
5. Kategori severity: None, Low, Medium, High, dan Critical.
6. Hubungan antara nilai metrik, vector string, skor numerik, dan severity.



Bagian B. Eksplorasi Base Metrics

Pelajari seluruh 11 Base Metrics CVSS v4.0 yang terdiri atas:

* Exploitability: AV, AC, AT, PR, UI.
* Impact pada Vulnerable System: VC, VI, VA.
* Impact pada Subsequent System: SC, SI, SA.



Untuk setiap metrik, jelaskan nama lengkap, tujuan penilaian, seluruh pilihan nilainya, arti setiap pilihan, dan minimal satu contoh situasi nyata atau hipotetis.



Berikan perhatian khusus pada perbedaan Attack Complexity dan Attack Requirements, Privileges Required dan User Interaction, serta Vulnerable System dan Subsequent System.



Bagian C. Memahami Threat, Environmental, dan Supplemental Metrics

Eksplorasi bagian-bagian berikut pada kalkulator:

1. Threat Metrics: pahami fungsi Exploit Maturity (E) serta hubungannya dengan bukti eksploitasi kerentanan.
2. Environmental Metrics: pelajari Confidentiality Requirement, Integrity Requirement, Availability Requirement, dan Modified Base Metrics.
3. Supplemental Metrics: pahami fungsi Safety, Automatable, Recovery, Value Density, Vulnerability Response Effort, dan Provider Urgency.



Jelaskan mengapa Supplemental Metrics menyediakan informasi tambahan tetapi tidak secara langsung mengubah skor numerik CVSS.



Bagian D. Memahami Vector String

Pelajari struktur dan cara membaca CVSS v4.0 Vector String.



Jelaskan:

1. Fungsi awalan CVSS:4.0.
2. Fungsi tanda / dan :.
3. Hubungan singkatan metrik dengan nilai pilihannya.
4. Cara membentuk vector string dari pilihan metrik.
5. Cara menggunakan vector string untuk mereproduksi hasil penilaian.

Buat satu contoh vector string Base CVSS v4.0 dan jelaskan makna setiap komponennya.



Bagian E. Simulasi Penggunaan Kalkulator

Gunakan kalkulator resmi FIRST untuk menjalankan simulasi berikut.



Simulasi 1 : Kebocoran Data Pasien



Sebuah endpoint aplikasi klinik memungkinkan pengguna internet tanpa akun mengakses seluruh data pasien, termasuk identitas dan riwayat kunjungan. Eksploitasi tidak memerlukan kondisi khusus maupun interaksi pengguna lain. Tidak ditemukan bukti perubahan data atau gangguan ketersediaan layanan.



Tentukan seluruh Base Metrics, skor CVSS, severity, dan vector string.



Simulasi 2:Manipulasi Data Pasien



Gunakan kondisi Simulasi 1, tetapi ubah skenario sehingga penyerang juga dapat mengubah seluruh data pasien secara tidak sah.



Tentukan metrik yang berubah, hitung kembali skor, lalu jelaskan perbedaannya.



Simulasi 3 : Pengaruh Autentikasi



Gunakan kembali kondisi Simulasi 1. Kali ini, eksploitasi hanya dapat dilakukan oleh pengguna yang telah login menggunakan akun biasa.



Tentukan metrik yang berubah dan bandingkan skor terhadap Simulasi 1.



Simulasi 4 : Dampak pada Sistem Lain



Sebuah kerentanan pada aplikasi klinik memungkinkan penyerang melakukan perubahan data secara signifikan pada aplikasi tersebut serta pada sistem laboratorium independen yang terhubung.



Identifikasi dampak terhadap Vulnerable System dan Subsequent System, tentukan seluruh Base Metrics, dan jelaskan hasilnya.



Bagian F. Analisis Hasil Simulasi

Susun tabel perbandingan berikut berdasarkan hasil kalkulator:



SimulasiMetrik yang berubahSkor CVSSSeverity Penjelasan perubahan1 Kondisi awal.........2............3............4............



Jawab pula pertanyaan berikut:

1. Mengapa perubahan satu metrik dapat memengaruhi skor akhir?
2. Apakah dua vector string berbeda selalu menghasilkan skor berbeda? Jelaskan berdasarkan hasil eksplorasi.
3. Mengapa severity tidak boleh ditentukan hanya berdasarkan nama kerentanan?
4. Mengapa hasil CVSS tidak dapat langsung dianggap sebagai ukuran keseluruhan risiko organisasi?
5. Mengapa penilaian metrik harus didasarkan pada bukti teknis?



Petunjuk Pengerjaan

* Gunakan kalkulator FIRST sebagai alat utama pengujian.
* Pelajari keterangan dan definisi setiap metrik sebelum menentukan nilainya.
* Gunakan dokumentasi resmi FIRST untuk memperjelas istilah yang belum dipahami.
* Lakukan simulasi secara terpisah dengan mengembalikan konfigurasi awal sebelum mengubah skenario.
* Dokumentasikan tangkapan layar yang memperlihatkan pilihan metrik, skor, severity, dan vector string.
* Setiap hasil penilaian harus disertai argumentasi teknis, bukan hanya angka.
* Mahasiswa tidak diminta menyerang sistem nyata; seluruh simulasi dilakukan menggunakan skenario yang disediakan.



Hasil yang Dikumpulkan

Susun laporan pembelajaran singkat dalam format PDF yang memuat penjelasan konsep CVSS, rangkuman seluruh kelompok metrik beserta nilai dan contohnya, penjelasan struktur vector string, hasil empat simulasi, tabel perbandingan skor, tangkapan layar kalkulator, dan kesimpulan.



Kriteria Penilaian: Ketepatan pemahaman konsep (25%), kelengkapan penjelasan metrik (25%), ketepatan pelaksanaan simulasi (30%), dan kualitas analisis serta dokumentasi (20%).



Penekanan: Tujuan tugas ini bukan sekadar memperoleh skor CVSS yang benar, tetapi memahami dan mampu mempertanggungjawabkan mengapa suatu kerentanan menghasilkan skor tersebut berdasarkan karakteristik teknis dan dampaknya.

