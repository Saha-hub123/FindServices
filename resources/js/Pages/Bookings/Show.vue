<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, useForm, router, usePage } from '@inertiajs/vue3';
import { onMounted, onUnmounted, ref, watch, nextTick, computed } from 'vue'; // Pastikan nextTick & watch diimport
import axios from 'axios'; // Kita butuh axios untuk request token on-demand

const props = defineProps({
    booking: Object,
    service: Object,
    bookedDates: Object, // Ubah jadi Object karena format dari backend sekarang {'2023-12-01': 5}
    isProvider: Boolean,
    isCustomer: Boolean,
    user_id: Number
});

// --- LOGIC DESKRIPSI ---
const showFullDescription = ref(false);
const descriptionLimit = 150; // Batas karakter sebelum dipotong (standar UX yang nyaman)

// Menghitung apakah deskripsi perlu dipotong
const hasLongDescription = computed(() => {
    return (props.booking.service.description || '').length > descriptionLimit;
});
// Mengatur teks yang akan ditampilkan
const displayedDescription = computed(() => {
    const text = props.booking.service.description || '';
    
    if (showFullDescription.value || !hasLongDescription.value) {
        return text;
    }
    
    // Potong teks dan tambahkan '...'
    return text.slice(0, descriptionLimit) + '...';
});
// --- LOGIC MAP (View Only) ---
onMounted(() => {
    if (props.booking.latitude && props.booking.longitude) {
        const lat = parseFloat(props.booking.latitude);
        const lng = parseFloat(props.booking.longitude);
        
        const map = L.map('map-detail').setView([lat, lng], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OSM' }).addTo(map);
        
        const icon = L.icon({
            iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
            shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
            iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34],
        });
        
        L.marker([lat, lng], { icon: icon }).addTo(map)
         .bindPopup(props.booking.location).openPopup();
    }

    // --- LISTENER REALTIME STATUS ---
    if (window.Echo) {
        window.Echo.private(`booking.${props.booking.hash_id}`)
            .listen('BookingStatusUpdated', (e) => {
                console.log('Status berubah:', e.booking.status);

                // Cara paling aman & mudah di Inertia:
                // Reload data booking dari server (partial reload)
                // Ini otomatis memperbarui props.booking tanpa refresh halaman penuh
                router.reload({ only: ['booking'] });

                // Opsional: Kasih notifikasi kecil (Toast)
                // alert(`Status pesanan diperbarui menjadi: ${e.booking.status}`);
            })
            .listen('ReviewSubmitted', (e) => {
                console.log('Review diterima:', e);
                
                // Reload data booking agar relasi 'review' terisi
                router.reload({ 
                    only: ['booking'],
                    onSuccess: () => {
                        // Opsional: Scroll ke review jika provider sedang melihat halaman
                        nextTick(() => {
                            if (reviewSection.value) {
                                reviewSection.value.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }
                        });
                    }
                });
            });
    }
});

// Bersihkan listener saat keluar halaman
onUnmounted(() => {
    if (window.Echo) {
        window.Echo.leave(`booking.${props.booking.hash_id}`);
    }
});


// --- 2. ACTION HANDLERS ---

// A. Update Status Biasa (Cancel, Reject, Start, Complete)
const updateStatus = (newStatus) => {
    let msg = "Apakah Anda yakin?";
    if (newStatus === 'cancelled') msg = "Yakin ingin membatalkan pesanan ini?";
    if (newStatus === 'rejected') msg = "Tolak pesanan ini?";
    
    // Kirim status saja (tanpa harga)
    if (confirm(msg)) {
        router.patch(route('bookings.update-status', props.booking.hash_id), { 
            status: newStatus 
        });
    }
};

// B. KHUSUS PROVIDER: TERIMA PESANAN
// Fungsi ini sekarang menembak 'update-status' tapi membawa data harga
const approveBooking = () => {
    if (confirm("Terima pesanan ini dengan harga yang tertera?")) {
        
        // PENTING: Gunakan router.patch ke 'bookings.update-status'
        router.patch(route('bookings.update-status', props.booking.hash_id), {
            status: 'confirmed', // Set status jadi confirmed
            agreed_price: props.booking.initial_price // Kirim harga untuk validasi & hitung fee
        });
    }
};

// --- LOGIC REVIEW ---
const reviewForm = useForm({
    // _method: 'PATCH', // Penting untuk update file via Inertia
    rating: 0,
    comment: '',
    images: [],      // File baru yang akan diupload
    deleted_images: [] // Path file lama yang akan dihapus
});

const isEditingReview = ref(false);
const reviewImagePreviews = ref([]); // Untuk file baru
const existingReviewImages = ref([]); // Untuk menampilkan file lama saat edit

// 4. Update Handle Images (Sama seperti create, tapi arahkan ke field images)
const handleReviewImages = (event) => {
    const files = Array.from(event.target.files);
    
    // Validasi Total (Sisa Lama + Baru <= 3)
    const currentTotal = existingReviewImages.value.length;
    if (files.length + reviewForm.images.length + currentTotal > 3) {
        alert("Total maksimal 3 foto.");
        return;
    }

    files.forEach(file => {
        reviewForm.images.push(file); // Masuk ke reviewForm.images (di controller jadi new_images)
        reviewImagePreviews.value.push(URL.createObjectURL(file));
    });
};

// Fungsi Reset (Clear form & preview)
const resetReviewForm = () => {
    reviewForm.reset();
    reviewImagePreviews.value = [];
};

const submitReview = () => {
    reviewForm.post(route('bookings.review', props.booking.hash_id), {
        onSuccess: () => resetReviewForm(),
        forceFormData: true // [PENTING] Agar file terkirim sebagai Multipart
    });
};

// Fungsi Hapus Review (CRUD)
const deleteReview = (reviewId) => {
    if (confirm("Hapus ulasan ini?")) {
        router.delete(route('reviews.destroy', reviewId));
    }
};

// 1. Fungsi Masuk Mode Edit
const startEditReview = () => {
    const review = props.booking.review;
    
    // Isi form dengan data lama
    reviewForm.rating = review.rating;
    reviewForm.comment = review.review;
    reviewForm.images = [];
    reviewForm.deleted_images = [];
    
    // Siapkan tampilan gambar lama
    existingReviewImages.value = review.images ? [...review.images] : [];
    reviewImagePreviews.value = []; // Reset preview upload baru

    isEditingReview.value = true;
};

// 2. Fungsi Batal Edit
const cancelEditReview = () => {
    isEditingReview.value = false;
    reviewForm.reset();
    reviewForm.clearErrors();
};

// 3. Fungsi Tandai Gambar Lama untuk Dihapus
const removeExistingImage = (imagePath) => {
    // Masukkan ke daftar hapus
    reviewForm.deleted_images.push(imagePath);
    // Hilangkan dari tampilan sementara
    existingReviewImages.value = existingReviewImages.value.filter(img => img !== imagePath);
};

// 5. Submit Update
const updateReview = () => {
    // Kita post ke route update, tapi key file-nya sesuaikan dengan controller
    reviewForm.transform((data) => ({
        ...data,
        new_images: data.images // Rename key agar sesuai controller
    })).post(route('reviews.update', props.booking.review.id), {
        onSuccess: () => {
            isEditingReview.value = false;
            reviewForm.reset();
            reviewImagePreviews.value = [];
        },
        forceFormData: true
    });
};

// Helper
const formatCurrency = (val) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(val);
const formatDate = (date) => new Date(date).toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });

// Status Color Helper
const getStatusBadge = (status) => {
    switch(status) {
        case 'pending': return 'bg-yellow-100 text-yellow-800';
        case 'confirmed': return 'bg-blue-100 text-blue-800';
        case 'in_progress': return 'bg-purple-100 text-purple-800';
        case 'waiting_completion': return 'bg-orange-100 text-orange-800';
        case 'completed': return 'bg-green-100 text-green-800';
        case 'cancelled': return 'bg-red-100 text-red-800';
        case 'rejected': return 'bg-red-200 text-red-900';
        default: return 'bg-gray-100 text-gray-800';
    }
};

// 1. BUAT REF UNTUK ELEMEN REVIEW
const reviewSection = ref(null);
// 2. WATCHER: PANTAU STATUS BOOKING
watch(() => props.booking.status, (newStatus) => {
    // Jika status berubah menjadi 'completed'
    if (newStatus === 'completed') {
        // Tunggu sebentar sampai Vue selesai merender elemen Review (karena ada v-if)
        nextTick(() => {
            // Lakukan Scroll Halus (Slide Down)
            if (reviewSection.value) {
                reviewSection.value.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' // Posisikan di tengah layar
                });
            }
        });
    }
});

// FUNGSI BAYAR
const payNow = async () => {
    try {
        // 1. Minta Token
        console.log("Sedang meminta token..."); // Debug 1
        const response = await axios.post(route('bookings.pay', props.booking.hash_id));
        
        // 2. Cek Apa isi Responnya
        console.log("Respon Server:", response.data); // Debug 2

        const token = response.data.snap_token;

        // 3. Validasi Token Sebelum Lanjut
        if (!token) {
            alert("Gagal mendapatkan Token Pembayaran dari server.");
            console.error("Token kosong/null");
            return;
        }

        // 4. Buka Popup Midtrans
        window.snap.pay(token, {
            onSuccess: function(result){
                alert("Pembayaran Berhasil!");
                location.reload();
            },
            // [MODIFIKASI DISINI]
            onPending: function(result){
                console.log("Pending Result:", result); // Debug
                alert("Menunggu Pembayaran... Silakan cek instruksi.");
                
                // Opsional: Kita bisa paksa reload, tapi kalau webhook belum masuk,
                // status tetap unpaid.
                // Triknya: Beri jeda 2-3 detik agar webhook sempat diproses server
                setTimeout(() => {
                    location.reload();
                }, 3000); 
            },
            onError: function(result){
                alert("Pembayaran Gagal!");
                location.reload();
            },
            onClose: function(){
                console.log('Popup ditutup');
            }
        });
        
    } catch (error) {
        console.error("Payment Error Full:", error);
        // Cek jika error datang dari backend (misal validasi 403/500)
        if (error.response && error.response.data) {
             alert("Eror Server: " + JSON.stringify(error.response.data));
        } else {
             alert("Terjadi kesalahan sistem.");
        }
    }
};

// --- LOGIKA HITUNGAN 4 HARGA (Card Rincian) ---
const pricingDetails = computed(() => {
    // 1. Ambil data mentah (handle null dengan 0)
    const initial = parseFloat(props.booking.initial_price || 0);
    const fee = parseFloat(props.booking.admin_fee || 0);
    const final = parseFloat(props.booking.final_price || 0);

    // 2. Cek apakah harga sudah fix (ada final_price)
    const isFixed = !!props.booking.final_price;

    // 3. Hitung Harga Revisi (Harga Jasa Murni)
    // Jika Fixed: Total Final dikurangi Fee
    // Jika Belum: Masih pakai Harga Awal
    const revised = isFixed ? (final - fee) : initial;

    // 4. Hitung Total Tampilan
    // Jika Fixed: Pakai Final Price
    // Jika Belum: Initial + Fee (Estimasi)
    const total = isFixed ? final : (initial + fee);

    return {
        initial: initial,
        revised: revised,
        fee: fee,
        total: total,
        isFixed: isFixed,
        // Cek apakah harga jasa berubah dari awal
        hasChanged: isFixed && (revised !== initial)
    };
});

// Tambahkan fungsi ini di script setup
const confirmManualPayment = () => {
    if (confirm("Nyatakan pembayaran manual telah diterima LUNAS?")) {
        router.post(route('bookings.confirm-payment', props.booking.hash_id));
    }
};

// State untuk Lightbox
const isLightboxOpen = ref(false);
const lightboxImage = ref(''); // Variable khusus untuk menampung gambar di popup

// Fungsi Helper (Dibuat menerima parameter 'url')
const openLightbox = (url) => {
    console.log("URL Gambar:", url); // Debugging
    
    if (url) {
        lightboxImage.value = url; // Simpan URL ke state lightbox
        isLightboxOpen.value = true; // Buka popup
    } else {
        console.error("URL Gambar kosong/undefined");
    }
};

const closeLightbox = () => {
    isLightboxOpen.value = false;
    // Optional: lightboxImage.value = ''; 
};
</script>

<template>
    <Head :title="`Booking #${booking.hash_id}`" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 lg:mb-0 mb-12">

                <div class="flex flex-col lg:flex-row gap-6">
                    
                    <div class="w-full lg:w-3/4 space-y-6">
                        <div>
                            <div class="text-sm text-gray-500 mb-1">
                                <Link :href="route('bookings.index')" class="hover:text-blue-600">&larr; Kembali ke Daftar Booking</Link>
                            </div>
                            <h1 class="text-2xl font-bold text-gray-900">Detail Pesanan #{{ booking.hash_id }}</h1>
                        </div>
                            
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h3 class="font-bold text-gray-800 mb-4 flex items-center">
                                <i class="fas fa-map-marked-alt text-blue-600 mr-2"></i> Lokasi Pengerjaan
                            </h3>
                            <div id="map-detail" class="w-full h-64 rounded-lg bg-gray-100 z-0 mb-3 border border-gray-200"></div>
                            <p class="text-sm text-gray-600">
                                <span class="font-semibold">Alamat:</span> {{ booking.location }}
                            </p>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h3 class="font-bold text-gray-800 mb-4 flex items-center">
                                <i class="fas fa-calendar-alt text-blue-600 mr-2"></i> Jadwal & Catatan
                            </h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <p class="text-xs text-gray-500 uppercase font-bold mb-1">Tanggal</p>
                                    <p class="text-gray-800">{{ formatDate(booking.booking_date) }}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 uppercase font-bold mb-1">Jam</p>
                                    <p class="text-gray-800">{{ booking.booking_time }}</p>
                                </div>
                                <div class="md:col-span-2">
                                    <p class="text-xs text-gray-500 uppercase font-bold mb-1">Catatan Pelanggan</p>
                                    <p class="text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-100 italic">
                                        "{{ booking.notes || 'Tidak ada catatan tambahan.' }}"
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col md:flex-row">
                            <div class="md:w-48 h-48 bg-gray-200 group relative">
                                <Link :href="route('service.show', booking.service.slug)" class="block h-full w-full">
                                    <img v-if="booking.service.galleries.length > 0" 
                                        :src="'/storage/' + booking.service.galleries[0].image" 
                                        class="w-full h-full object-cover transition duration-300 group-hover:opacity-90">
                                    
                                    <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition flex items-center justify-center"></div>
                                </Link>
                            </div>
                            <div class="p-6 flex-1 flex flex-col justify-center">
                                <h3 class="text-lg font-bold text-gray-900 mb-2">
                                    <Link :href="route('service.show', booking.service.slug)" class="hover:text-blue-600 hover:underline transition">
                                        {{ booking.service.title }}
                                    </Link>
                                </h3>
                                <div class="mb-4">
                                    <p class="text-sm text-gray-600 whitespace-pre-line leading-relaxed transition-all duration-300">
                                        {{ displayedDescription }}
                                    </p>
                                    
                                    <button 
                                        v-if="hasLongDescription" 
                                        @click="showFullDescription = !showFullDescription" 
                                        class="text-xs font-bold text-blue-600 hover:text-blue-800 mt-1 focus:outline-none flex items-center gap-1 hover:underline"
                                    >
                                        <span v-if="!showFullDescription">Baca Selengkapnya <i class="fas fa-chevron-down ml-0.5"></i></span>
                                        <span v-else>Sembunyikan <i class="fas fa-chevron-up ml-0.5"></i></span>
                                    </button>
                                </div>
                                <div class="flex items-center gap-2">
                                    <span class="text-sm text-gray-500">Harga Awal:</span>
                                    <span class="font-bold text-blue-600">{{ formatCurrency(booking.initial_price) }}</span>
                                </div>
                            </div>
                        </div>

                        <div ref="reviewSection" v-if="booking.status === 'completed'" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-fade-in scroll-mt-24">
    
                            <h3 class="font-bold text-gray-800 mb-4 flex items-center justify-between">
                                <span class="flex items-center"><i class="fas fa-star text-yellow-400 mr-2"></i> Ulasan Pekerjaan</span>
                                
                                <div v-if="booking.review && booking.review.user_id === $page.props.auth.user.id && !isEditingReview" class="flex gap-3">
                                    <button @click="startEditReview" class="text-xs text-blue-600 hover:text-blue-800 font-bold hover:underline">
                                        <i class="fas fa-edit mr-1"></i> Edit
                                    </button>
                                    <button @click="deleteReview(booking.review.id)" class="text-xs text-red-500 hover:text-red-700 font-bold hover:underline">
                                        <i class="fas fa-trash-alt mr-1"></i> Hapus
                                    </button>
                                </div>
                            </h3>

                            <div v-if="isEditingReview" class="bg-blue-50/50 p-4 rounded-lg border border-blue-100">
                                <form @submit.prevent="updateReview">
                                    <p class="text-xs font-bold text-blue-600 mb-2 uppercase">Edit Ulasan Anda</p>
                                    
                                    <div class="flex gap-2 mb-3">
                                        <button type="button" v-for="n in 5" :key="n" @click="reviewForm.rating = n" class="text-2xl transition hover:scale-110" :class="n <= reviewForm.rating ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'">
                                            <i class="fas fa-star"></i>
                                        </button>
                                    </div>

                                    <textarea v-model="reviewForm.comment" rows="3" class="w-full rounded-lg border-gray-300 mb-3 text-sm focus:ring-blue-500 focus:border-blue-500"></textarea>

                                    <div class="mb-4">
                                        <label class="block text-xs font-bold text-gray-500 mb-2">Foto Bukti (Max 3)</label>
                                        <div class="flex flex-wrap items-center gap-3">
                                            
                                            <div v-for="(img, idx) in existingReviewImages" :key="'old-'+idx" class="relative h-16 w-16 group">
                                                <img :src="'/storage/' + img" class="h-full w-full object-cover rounded-lg border border-gray-200">
                                                <button type="button" @click="removeExistingImage(img)" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600 shadow-sm" title="Hapus foto ini">
                                                    &times;
                                                </button>
                                                <span class="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-[8px] text-center rounded-b-lg">Lama</span>
                                            </div>

                                            <div v-for="(preview, idx) in reviewImagePreviews" :key="'new-'+idx" class="relative h-16 w-16">
                                                <img :src="preview" class="h-full w-full object-cover rounded-lg border border-green-300 ring-2 ring-green-100">
                                                <button type="button" @click="reviewForm.images.splice(idx, 1); reviewImagePreviews.splice(idx, 1)" class="absolute -top-2 -right-2 bg-gray-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-gray-800">
                                                    &times;
                                                </button>
                                                <span class="absolute bottom-0 left-0 right-0 bg-green-600/80 text-white text-[8px] text-center rounded-b-lg">Baru</span>
                                            </div>

                                            <label v-if="(existingReviewImages.length + reviewForm.images.length) < 3" class="h-16 w-16 flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition">
                                                <i class="fas fa-plus text-gray-400"></i>
                                                <input type="file" multiple accept="image/*" @change="handleReviewImages" class="hidden">
                                            </label>
                                        </div>
                                    </div>

                                    <div class="flex gap-2">
                                        <button type="submit" :disabled="reviewForm.processing" class="px-4 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 disabled:opacity-50 text-sm">
                                            Simpan Perubahan
                                        </button>
                                        <button type="button" @click="cancelEditReview" class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-bold hover:bg-gray-50 text-sm">
                                            Batal
                                        </button>
                                    </div>
                                </form>
                            </div>

                            <div v-else-if="booking.review" class="bg-gray-50 p-4 rounded-lg border border-gray-100">
                                <div class="flex items-center mb-2">
                                    <div class="flex mr-2">
                                        <i v-for="n in 5" :key="n" class="fas fa-star" :class="n <= booking.review.rating ? 'text-yellow-400' : 'text-gray-300'"></i>
                                    </div>
                                    <span class="text-sm font-bold text-gray-700">{{ booking.review.rating }}.0</span>
                                </div>
                                <p class="text-gray-600 italic mb-3">"{{ booking.review.review }}"</p>

                                <div v-if="booking.review.images && booking.review.images.length > 0" class="flex gap-2 mt-3">
                                    <div v-for="(img, idx) in booking.review.images" :key="idx" class="relative group">
                                        <img :src="'/storage/' + img" class="h-20 w-20 object-cover rounded-lg border border-gray-200 cursor-pointer hover:scale-105 transition" @click="openLightbox('/storage/' + img)">
                                    </div>
                                </div>
                            </div>

                            <div v-else-if="isCustomer && !booking.review">
                                <p class="text-sm text-gray-600 mb-4">Bagaimana hasil pekerjaan ini? Berikan rating dan foto bukti.</p>
                                <form @submit.prevent="submitReview">
                                    <div class="flex gap-2 mb-4">
                                        <button type="button" v-for="n in 5" :key="n" @click="reviewForm.rating = n" class="text-2xl transition hover:scale-110" :class="n <= reviewForm.rating ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'">
                                            <i class="fas fa-star"></i>
                                        </button>
                                    </div>

                                    <textarea v-model="reviewForm.comment" rows="3" placeholder="Tulis pengalaman Anda..." class="w-full rounded-lg border-gray-300 mb-3 text-sm focus:ring-blue-500 focus:border-blue-500"></textarea>

                                    <div class="mb-4">
                                        <label class="block text-xs font-bold text-gray-500 mb-2">Tambah Foto (Opsional, Max 3)</label>
                                        <div class="flex items-center gap-3">
                                            <label v-if="reviewForm.images.length < 3" class="h-16 w-16 flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition">
                                                <i class="fas fa-camera text-gray-400"></i>
                                                <input type="file" multiple accept="image/*" @change="handleReviewImages" class="hidden">
                                            </label>

                                            <div v-for="(preview, idx) in reviewImagePreviews" :key="idx" class="relative h-16 w-16">
                                                <img :src="preview" class="h-full w-full object-cover rounded-lg border border-gray-200">
                                                <button type="button" @click="reviewForm.images.splice(idx, 1); reviewImagePreviews.splice(idx, 1)" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-0.5 w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600">
                                                    &times;
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    <button type="submit" :disabled="reviewForm.processing || reviewForm.rating === 0" class="px-4 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 disabled:opacity-50 text-sm">
                                        Kirim Ulasan
                                    </button>
                                </form>
                            </div>

                            <div v-else class="text-center text-gray-500 text-sm py-4">
                                Menunggu ulasan dari pelanggan.
                            </div>
                        </div>

                    </div>

                    <div class="w-full lg:w-1/4">
                        <div class="sticky top-24 space-y-4">
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                <div class="p-4 border-b border-gray-50 bg-gray-50 flex justify-between items-center">
                                    <h4 class="font-bold text-gray-800 text-sm">Rincian Biaya</h4>
                                    <span v-if="pricingDetails.isFixed" class="text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded font-bold uppercase border border-green-200">
                                        Fixed
                                    </span>
                                    <span v-else class="text-[10px] bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded font-bold uppercase border border-yellow-200">
                                        Estimasi
                                    </span>
                                </div>
                                <div class="p-5 text-center">
                                    <div class="flex justify-between items-center text-sm">
                                        <span class="text-gray-500 text-xs">Harga Awal</span>
                                        <span class="font-medium" :class="pricingDetails.hasChanged ? 'text-gray-400 line-through decoration-red-400' : 'text-gray-800'">
                                            {{ formatCurrency(pricingDetails.initial) }}
                                        </span>
                                    </div>

                                    <div class="flex justify-between items-center text-sm">
                                        <span class="text-gray-600">Harga Kesepakatan (Jasa)</span>
                                        <span class="font-bold text-gray-900">
                                            {{ formatCurrency(pricingDetails.revised) }}
                                        </span>
                                    </div>

                                    <div class="flex justify-between items-center text-sm">
                                        <span class="text-gray-600 flex items-center gap-1">
                                            Biaya Layanan
                                            <i v-if="pricingDetails.fee > 0" class="fas fa-info-circle text-gray-300 text-xs" title="Biaya operasional aplikasi"></i>
                                        </span>
                                        <span v-if="pricingDetails.fee > 0" class="text-gray-800 font-medium">
                                            {{ formatCurrency(pricingDetails.fee) }}
                                        </span>
                                        <span v-else class="text-green-600 font-bold text-xs bg-green-50 px-2 py-0.5 rounded border border-green-100">
                                            GRATIS
                                        </span>
                                    </div>

                                    <div class="border-t border-dashed border-gray-300 pt-3 mt-2 flex justify-between items-center">
                                        <span class="font-bold text-gray-800">Total Akhir</span>
                                        <span class="font-extrabold text-xl text-blue-700">
                                            {{ formatCurrency(pricingDetails.total) }}
                                        </span>
                                    </div>

                                    <div class="flex justify-between items-center my-2 py-2 border-t border-gray-200">
                                            <span class="text-sm text-gray-600">Metode Bayar</span>
                                            <div class="flex items-center gap-2">
                                                <template v-if="booking.payment_method === 'manual'">
                                                    <span class="text-sm font-bold text-gray-800">Manual / Cash</span>
                                                    <i class="fas fa-hand-holding-usd text-gray-500"></i>
                                                </template>
                                                <template v-else>
                                                    <span class="text-sm font-bold text-gray-800">Midtrans Otomatis</span>
                                                    <i class="fas fa-university text-blue-600"></i>
                                                </template>
                                            </div>
                                        </div>

                                        <div v-if="booking.status === 'pending'" class="p-2 my-2 bg-yellow-50 text-yellow-700 rounded text-xs font-medium border border-yellow-100 flex items-center justify-center text-center">
                                            <i class="fas fa-unlock-alt mr-1.5"></i>
                                            <span>Harga masih estimasi & belum dikunci</span>
                                        </div>

                                        <div v-else-if="booking.status !== 'cancelled' && booking.status !== 'rejected'" class="p-2 my-2 bg-green-50 text-green-700 rounded text-xs font-medium border border-green-100">
                                            <i class="fas fa-lock mr-1"></i> Harga & Pesanan Terkunci
                                        </div>

                                    <div v-if="isCustomer && (booking.status === 'pending' || booking.status === 'rejected')">
                                        <Link :href="route('bookings.edit', booking.hash_id)" class="w-full py-2 px-4 bg-yellow-200 border border-yellow-100 text-yellow-700 font-bold rounded-lg hover:bg-yellow-300 transition flex items-center justify-center text-sm shadow-sm">
                                            <i class="fas fa-pencil-alt mr-2"></i> 
                                            {{ booking.status === 'rejected' ? 'Revisi & Ajukan Ulang' : 'Edit Pesanan' }}
                                        </Link>
                                        <p class="text-[10px] text-gray-400 mt-2 leading-tight text-center">
                                            <span v-if="booking.status === 'rejected'" class="text-red-400">
                                                Pesanan ditolak. Silakan ubah detail (Tanggal/Harga) lalu ajukan kembali.
                                            </span>
                                            <span v-else>
                                                Anda hanya bisa mengedit pesanan sebelum penyedia menyetujuinya.
                                            </span>
                                        </p>
                                    </div>

                                    

                                    <div class="mt-6">

                                        

                                        <div v-if="isCustomer" class="space-y-3">
    
                                            <div v-if="booking.status === 'pending'" class="bg-yellow-50 text-yellow-800 p-3 rounded-lg text-center text-sm font-medium border border-yellow-100">
                                                <i class="fas fa-clock mr-1.5"></i> Menunggu Konfirmasi Harga dari Penyedia
                                            </div>

                                            <div v-if="booking.status === 'confirmed' && booking.payment_status === 'unpaid' && booking.payment_method === 'gateway'" 
                                                class="space-y-4 p-1">
                                                
                                                <div class="flex items-start gap-3 p-3 bg-blue-50/80 border-l-4 border-blue-500 rounded-r-lg">
                                                    <div class="bg-blue-100 p-1.5 rounded-full shrink-0 text-blue-600 mt-0.5">
                                                        <i class="fas fa-info text-xs"></i>
                                                    </div>
                                                    <div class="text-xs text-blue-800 leading-relaxed">
                                                        <span class="font-bold block mb-0.5">Siap Diproses</span>
                                                        Silakan selesaikan pembayaran agar pesanan segera diteruskan ke penyedia.
                                                    </div>
                                                </div>

                                                <button @click="payNow" 
                                                        class="group relative w-full overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 to-blue-700 p-px shadow-lg shadow-blue-500/30 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-blue-500/50 active:scale-[0.98]">
                                                    
                                                    <div class="relative flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-3.5 text-white transition-all">
                                                        <i class="fas fa-credit-card text-lg transition-transform duration-300 group-hover:rotate-12"></i>
                                                        
                                                        <div class="flex flex-col items-start leading-none">
                                                            <span class="text-[10px] font-medium opacity-90 uppercase tracking-wide">Bayar Sekarang</span>
                                                            <span class="text-lg font-bold">{{ formatCurrency(booking.final_price) }}</span>
                                                        </div>
                                                        
                                                        <i class="fas fa-chevron-right absolute right-5 text-sm opacity-0 transition-all duration-300 group-hover:translate-x-1 group-hover:opacity-100"></i>
                                                    </div>
                                                </button>
                                            </div>


                                            <div v-else-if="booking.payment_status === 'pending'" class="space-y-4 p-1">
                                                
                                                <div class="flex items-start gap-3 p-3 bg-orange-50/80 border border-orange-100 rounded-xl shadow-sm">
                                                    <i class="fas fa-hourglass-half text-orange-500 mt-1 text-lg animate-pulse"></i>
                                                    <div class="text-xs text-orange-800 leading-relaxed">
                                                        <span class="font-bold text-orange-900 block mb-0.5">Menunggu Pembayaran</span>
                                                        Transaksi sebelumnya belum selesai. Lanjutkan pembayaran Anda.
                                                    </div>
                                                </div>

                                                <button @click="payNow" 
                                                        class="group w-full rounded-2xl bg-orange-500 hover:bg-orange-600 text-white font-bold py-3.5 px-4 shadow-lg shadow-orange-500/30 transition-all duration-300 hover:-translate-y-0.5 active:scale-[0.98] flex items-center justify-center gap-2">
                                                    
                                                    <i class="fas fa-history transition-transform duration-500 group-hover:-rotate-180"></i>
                                                    <span>Lanjutkan Pembayaran</span>
                                                </button>
                                            </div>

                                            <div v-else-if="booking.payment_status === 'failed'" class="space-y-3">
                                                <div class="bg-red-50 text-red-700 p-4 rounded-lg text-center border border-red-100">
                                                    <i class="fas fa-times-circle text-2xl mb-2 block"></i>
                                                    <span class="font-bold block">Pembayaran Gagal</span>
                                                    <span class="text-xs">Terjadi kesalahan pada metode pembayaran. Silakan hubungi penyedia jasa atau membuat pesanan ulang.</span>
                                                </div>
                                            </div>

                                            <div v-else-if="booking.payment_status === 'expired'" class="space-y-3">
                                                <div class="bg-red-50 text-red-700 p-4 rounded-lg text-center border border-red-100">
                                                    <i class="fas fa-clock text-2xl mb-2 block"></i>
                                                    <span class="font-bold block">Waktu Pembayaran Habis</span>
                                                    <span class="text-xs">Batas waktu pembayaran telah berakhir. Silakan buat pesanan ulang.</span>
                                                </div>
                                                <Link :href="route('service.show', booking.service.slug)" class="w-full block bg-red-600 text-white font-bold py-3 rounded-xl hover:bg-red-700 text-center text-sm shadow-md transition">
                                                    <i class="fas fa-redo mr-2"></i> Pesan Ulang Jasa Ini
                                                </Link>
                                            </div>

                                            <div v-else-if="booking.payment_status === 'paid'" class="bg-green-100 border border-green-200 text-green-800 p-3 rounded-lg text-center font-bold flex items-center justify-center">
                                                <i class="fas fa-check-circle mr-2 text-xl"></i> Pembayaran Lunas
                                            </div>

                                        </div>


                                        <div v-if="isProvider" class="space-y-3">

                                            <div v-if="booking.status === 'pending'" class="bg-blue-50 text-blue-800 p-3 rounded-lg text-center text-sm font-medium border border-blue-100">
                                                <i class="fas fa-exclamation-circle mr-1.5"></i> 
                                                Pesanan Baru Masuk! Silakan cek detail dan konfirmasi harga.
                                            </div>

                                            <div v-else-if="booking.status === 'confirmed' && booking.payment_status === 'unpaid'" class="bg-yellow-50 text-yellow-800 p-3 rounded-lg text-center text-sm font-medium border border-yellow-100">
                                                <i class="fas fa-hourglass-start mr-1.5"></i> 
                                                Anda telah menyetujui pesanan. Menunggu Customer melakukan pembayaran.
                                            </div>

                                            <div v-else-if="booking.payment_status === 'pending'" class="bg-orange-50 text-orange-800 p-3 rounded-lg text-center text-sm font-medium border border-orange-100 flex flex-col gap-1">
                                                <div><i class="fas fa-sync fa-spin mr-1.5"></i> Customer sedang memproses pembayaran...</div>
                                                <div class="text-xs opacity-75">Silahkan mulai pengerjaan atau menunggu status Lunas.</div>
                                            </div>

                                            <div v-else-if="booking.payment_status === 'failed'" class="bg-red-50 text-red-700 p-3 rounded-lg text-center text-sm font-medium border border-red-100">
                                                <i class="fas fa-times-circle text-2xl mb-2 block"></i>
                                                <span class="font-bold block">Pembayaran Gagal</span>
                                                <span class="text-xs">Terjadi kesalahan pada metode pembayaran pelanggan. Silakan hubungi pelanggan</span>
                                            </div>

                                            <div v-else-if="booking.payment_status === 'expired'" class="space-y-3">
                                                <div class="bg-red-50 text-red-700 p-4 rounded-lg text-center border border-red-100">
                                                    <i class="fas fa-clock text-2xl mb-2 block"></i>
                                                    <span class="font-bold block">Waktu Pembayaran Habis</span>
                                                    <span class="text-xs">Batas waktu pembayaran untuk pelanggan telah berakhir.</span>
                                                </div>
                                            </div>

                                            <div v-else-if="booking.payment_status === 'paid'" class="space-y-2">
                                                <div class="bg-green-100 border border-green-200 text-green-800 p-3 rounded-lg text-center font-bold flex items-center justify-center">
                                                    <i class="fas fa-check-circle mr-2 text-xl"></i> 
                                                    {{ booking.payment_method === 'gateway' ? 'Pembayaran Lunas' : 'Bayar Manual (COD)' }}
                                                </div>
                                            </div>

                                        </div>

                                    </div>
                                    
                                </div>
                            </div>

                            
                            
                            
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
                                <p class="text-xs text-gray-500 font-bold uppercase mb-2">Status Pesanan</p>
                                <span class="inline-block px-3 py-1 rounded-full text-sm font-bold uppercase mb-4" :class="getStatusBadge(booking.status || 'pending')">
                                    {{ booking.status?.replace('_', ' ') ?? '-' }}
                                </span>

                                <div v-if="isCustomer" class="space-y-2">
                                    <div v-if="booking.status === 'pending'">
                                        <p class="text-xs text-gray-500 mb-2 animate-pulse">Menunggu konfirmasi penyedia...</p>
                                        <button @click="updateStatus('cancelled')" class="w-full py-2 bg-white border border-red-200 text-red-600 hover:bg-red-50 rounded-lg font-bold text-sm">
                                            Batalkan Pesanan
                                        </button>
                                    </div>
                                    <div v-if="booking.status === 'rejected'">
                                        <p class="text-xs text-gray-500 mb-2">Pesanan anda ditolak, Silahkan tanya pada penyedia alasannya</p>
                                        <button @click="updateStatus('pending')" class="w-full py-2 bg-orange-100 text-orange-800 rounded-lg font-bold text-sm hover:bg-orange-200">
                                            Ajukan Ulang Pesanan
                                        </button>
                                        <button @click="updateStatus('cancelled')" class="w-full mt-2 py-2 bg-white border border-red-200 text-red-600 hover:bg-red-50 rounded-lg font-bold text-sm">
                                            Batalkan Pesanan
                                        </button>
                                    </div>
                                    <div v-if="booking.status === 'cancelled'">
                                        <p class="text-xs text-gray-500 mb-2">Anda membatalkan pesanan ini</p>
                                    </div>
                                    <div v-if="booking.status === 'confirmed'">
                                        <p class="text-xs text-gray-500 mb-2">Pesanan diterima, silahkan tunggu sampai waktu pengerjaan</p>
                                        <button @click="updateStatus('cancelled')" class="w-full py-2 bg-white border border-red-200 text-red-600 hover:bg-red-50 rounded-lg font-bold text-sm">
                                            Batalkan Pesanan
                                        </button>
                                    </div>
                                    <div v-if="booking.status === 'in_progress'">
                                        <p class="text-xs text-gray-500 mb-2">Pesanan sedang dalam proses pengerjaan</p>
                                        <button @click="updateStatus('cancelled')" class="w-full py-2 bg-white border border-red-200 text-red-600 hover:bg-red-50 rounded-lg font-bold text-sm">
                                            Batalkan Pesanan
                                        </button>
                                    </div>
                                    <div v-if="booking.status === 'completed'">
                                        <p class="text-xs text-gray-500 mb-2">Pesanan telah selesai dikerjakan, terima kasih.</p>
                                        
                                        <Link :href="route('service.show', booking.service)" 
                                            class="flex items-center justify-center w-full py-2 bg-blue-100 text-blue-700 rounded-lg font-bold text-sm hover:bg-blue-200 transition">
                                            Lihat Jasa Ini
                                        </Link>
                                    </div>

                                    <div v-if="booking.status === 'waiting_completion'" class="bg-orange-50 p-3 rounded-lg border border-orange-100">
                                        <p class="text-xs text-orange-800 mb-3 font-semibold">Penyedia menyatakan pekerjaan selesai. Konfirmasi?</p>
                                        <button @click="updateStatus('completed')" class="w-full py-2 bg-green-600 text-white rounded-lg font-bold text-sm hover:bg-green-700 mb-2">
                                            <i class="fas fa-check mr-1"></i> Ya, Selesai
                                        </button>
                                        <button @click="updateStatus('in_progress')" class="w-full py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-bold text-sm hover:bg-gray-50">
                                            Belum Selesai
                                        </button>
                                    </div>
                                </div>

                                <div v-if="isProvider" class="space-y-2">
                                    <div v-if="booking.status === 'pending'">
                                        <p class="text-xs text-gray-500 mb-2">konfirmasi Penyewaan</p>
                                        <button @click="approveBooking" class="w-full py-2 bg-blue-100 text-blue-600 rounded-lg font-bold text-sm hover:bg-blue-200 mb-2">
                                            Terima Pesanan
                                        </button>
                                        <button @click="updateStatus('rejected')" class="w-full py-2 bg-white border border-red-200 text-red-600 rounded-lg hover:bg-red-50 font-bold text-sm">
                                            Tolak Pesanan
                                        </button>
                                    </div>
                                    <div v-if="booking.status === 'cancelled'">
                                        <p class="text-xs text-gray-500 mb-2">Pesanan dibatalkan, silahkan tanya alasannya pada pelanggan</p>
                                    </div>
                                    <div v-if="booking.status === 'rejected'">
                                        <p class="text-xs text-orange-500 mb-2">Anda menolak pesanan ini, tolong beritahu alasannya pada pelanggan</p>
                                    </div>


                                    <div v-if="booking.status === 'confirmed'">
    
                                        <template v-if="booking.payment_method === 'gateway'">
                                            <div v-if="booking.payment_status !== 'paid'" class="space-y-2">
                                                <div class="bg-orange-50 border border-orange-100 text-orange-700 px-3 py-2 rounded-lg text-xs text-center flex items-center justify-center gap-2">
                                                    <i class="fas fa-spinner fa-spin"></i>
                                                    Menunggu pembayaran customer berhasil...
                                                </div>
                                                <button disabled class="w-full py-2 bg-gray-100 text-gray-400 rounded-lg font-bold text-sm cursor-not-allowed">
                                                    Mulai Pekerjaan
                                                </button>
                                            </div>

                                            <div v-else>
                                                <p class="text-xs text-center text-gray-500 mb-2">Pembayaran terverifikasi. Silakan menuju lokasi.</p>
                                                <button @click="updateStatus('in_progress')" class="w-full py-2 bg-purple-600 text-white rounded-lg font-bold text-sm hover:bg-purple-700 shadow-md">
                                                    <i class="fas fa-tools mr-2"></i> Mulai Pekerjaan
                                                </button>
                                            </div>
                                        </template>


                                        <template v-else>
                                            <div v-if="booking.payment_status !== 'paid'" class="space-y-3">
                                                <div class="bg-blue-50 border border-blue-100 text-blue-700 px-3 py-2 rounded-lg text-xs text-center">
                                                    <i class="fas fa-info-circle mr-1"></i>
                                                    Customer menggunakan pembayaran Manual. Pastikan Anda menerima uang sebelum memulai.
                                                </div>
                                                
                                                <div class="grid grid-cols-2 gap-2">
                                                    <button @click="confirmManualPayment" class="py-2 bg-green-600 text-white rounded-lg font-bold text-xs hover:bg-green-700 shadow-sm">
                                                        <i class="fas fa-check-circle mr-1"></i> Uang Diterima
                                                    </button>
                                                    
                                                    <button @click="updateStatus('rejected')" class="py-2 bg-white border border-red-200 text-red-600 rounded-lg font-bold text-xs hover:bg-red-50">
                                                        <i class="fas fa-times-circle mr-1"></i> Pembayaran Ditolak
                                                    </button>
                                                </div>
                                            </div>

                                            <div v-else>
                                                <div class="bg-green-50 border border-green-100 text-green-700 px-3 py-2 rounded-lg text-xs text-center mb-2">
                                                    <i class="fas fa-check mr-1"></i> Pembayaran Manual Diterima
                                                </div>
                                                <button @click="updateStatus('in_progress')" class="w-full py-2 bg-purple-600 text-white rounded-lg font-bold text-sm hover:bg-purple-700 shadow-md">
                                                    <i class="fas fa-tools mr-2"></i> Mulai Pekerjaan
                                                </button>
                                            </div>
                                        </template>

                                    </div>

                                    <div v-if="booking.status === 'in_progress'">
                                        <button @click="updateStatus('waiting_completion')" class="w-full py-2 bg-orange-100 text-orange-500 rounded-lg font-bold text-sm hover:bg-orange-200">
                                            Selesaikan Pekerjaan
                                        </button>
                                        <p class="text-[10px] text-gray-400 mt-2">Pelanggan harus mengkonfirmasi penyelesaian.</p>
                                    </div>

                                    <div v-if="booking.status === 'waiting_completion'">
                                        <p class="text-xs text-orange-600 font-semibold animate-pulse">Menunggu konfirmasi pelanggan...</p>
                                    </div>
                                    <div v-if="booking.status === 'completed'">
                                        <p class="text-xs text-gray-500 mb-2">Anda telah menyelesaikan pesanan ini</p>
                                    </div>
                                </div>

                            </div>

                            <Link :href="route('chats.index', { user_id: isProvider ? booking.customer?.hash_id : booking.provider?.hash_id, booking_id: booking.hash_id })" 
                                class="w-full py-3 px-4 bg-white border border-blue-600 text-blue-600 hover:bg-blue-50 font-bold rounded-lg transition flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                                </svg>
                                Chat {{ isProvider ? 'Pelanggan' : 'Penyedia' }}
                            </Link>
                            
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 flex items-center gap-3">

                                <Link
                                    :href="route('profile.show', isProvider ? booking.customer.hash_id : booking.provider.hash_id)">
                                    <img :src="(isProvider ? booking.customer.avatar : booking.provider.avatar)
                                        ? '/storage/' + (isProvider ? booking.customer.avatar : booking.provider.avatar)
                                        : 'https://ui-avatars.com/api/?name=' + (isProvider ? booking.customer.name : booking.provider.name) + '&background=random'"
                                        class="h-10 w-10 rounded-full border border-gray-200 object-cover hover:ring-4 hover:ring-blue-100 transition">
                                </Link>

                                <div class="overflow-hidden flex-1">
                                    <p class="text-xs text-gray-500">
                                        {{ isProvider ? 'Pelanggan' : 'Penyedia Jasa' }}
                                    </p>
                                    <Link
                                        :href="route('profile.show', isProvider ? booking.customer.hash_id : booking.provider.hash_id)"
                                        class="font-bold text-sm text-gray-800 truncate hover:text-blue-600 transition block">
                                        {{ isProvider ? booking.customer.name : booking.provider.name }}
                                    </Link>
                                </div>

                                <Link
                                    :href="route('profile.show', isProvider ? booking.customer.hash_id : booking.provider.hash_id)"
                                    class="items-center px-3 py-1 border bg-white border-blue-600 rounded-md text-xs font-semibold text-blue-600 hover:bg-blue-50 transition flex-shrink-0">
                                    <i class="fas fa-user mr-1.5"></i> Profil
                                </Link>

                            </div>

                        </div>
                    </div>

                </div>
            </div>
        </div>
        <Teleport to="body">
            <div v-if="isLightboxOpen"
                class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/90 backdrop-blur-sm transition-opacity duration-300 animate-fade-in"
                @click="closeLightbox">

                <button @click="closeLightbox"
                    class="absolute top-5 right-5 text-white/70 hover:text-white transition p-2 z-[10000]">
                    <i class="fas fa-times text-3xl"></i>
                </button>

                <img v-if="lightboxImage" :src="lightboxImage"
                    class="max-h-[90vh] max-w-[90vw] object-contain rounded-lg shadow-2xl animate-zoom-in select-none"
                    @click.stop>
            </div>
        </Teleport>
    </AuthenticatedLayout>
</template>

<style scoped>
#map-detail { z-index: 0; }
.animate-fade-in { animation: fadeIn 0.5s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>