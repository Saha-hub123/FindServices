<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, useForm, router } from '@inertiajs/vue3';
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'; // Pastikan nextTick & watch diimport

const props = defineProps({
    booking: Object,
    isProvider: Boolean,
    isCustomer: Boolean,
    user_id: Number
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
        window.Echo.private(`booking.${props.booking.id}`)
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
        window.Echo.leave(`booking.${props.booking.id}`);
    }
});


// --- LOGIC STATUS UPDATE ---
const updateStatus = (newStatus) => {
    if (confirm(`Apakah Anda yakin ingin mengubah status menjadi '${newStatus}'?`)) {
        router.patch(route('bookings.update-status', props.booking.id), {
            status: newStatus
        });
    }
};

// --- LOGIC REVIEW ---
const reviewForm = useForm({
    rating: 0,
    comment: ''
});

const submitReview = () => {
    reviewForm.post(route('bookings.review', props.booking.id), {
        onSuccess: () => reviewForm.reset()
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
</script>

<template>
    <Head :title="`Booking #${booking.id}`" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

                <div class="flex flex-col lg:flex-row gap-6">
                    
                    <div class="w-full lg:w-3/4 space-y-6">
                        <div>
                            <div class="text-sm text-gray-500 mb-1">
                                <Link :href="route('bookings.index')" class="hover:text-blue-600">&larr; Kembali ke Daftar Booking</Link>
                            </div>
                            <h1 class="text-2xl font-bold text-gray-900">Detail Pesanan #{{ booking.id }}</h1>
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
                            <div class="md:w-48 h-48 bg-gray-200">
                                <img v-if="booking.service.galleries.length > 0" 
                                     :src="'/storage/' + booking.service.galleries[0].image" 
                                     class="w-full h-full object-cover">
                            </div>
                            <div class="p-6 flex-1 flex flex-col justify-center">
                                <h3 class="text-lg font-bold text-gray-900 mb-2">{{ booking.service.title }}</h3>
                                <p class="text-sm text-gray-500 mb-4">{{ booking.service.description }}</p>
                                <div class="flex items-center gap-2">
                                    <span class="text-sm text-gray-500">Harga Awal:</span>
                                    <span class="font-bold text-blue-600">{{ formatCurrency(booking.initial_price) }}</span>
                                </div>
                            </div>
                        </div>

                        <div ref="reviewSection" v-if="booking.status === 'completed'" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-fade-in scroll-mt-24">
                            <h3 class="font-bold text-gray-800 mb-4 flex items-center">
                                <i class="fas fa-star text-yellow-400 mr-2"></i> Ulasan Pekerjaan
                            </h3>

                            <div v-if="booking.review" class="bg-gray-50 p-4 rounded-lg border border-gray-100">
                                <div class="flex items-center mb-2">
                                    <div class="flex mr-2">
                                        <i v-for="n in 5" :key="n" class="fas fa-star" :class="n <= booking.review.rating ? 'text-yellow-400' : 'text-gray-300'"></i>
                                    </div>
                                    <span class="text-sm font-bold text-gray-700">{{ booking.review.rating }}.0</span>
                                </div>
                                <p class="text-gray-600 italic">"{{ booking.review.review }}"</p>
                            </div>

                            <div v-else-if="isCustomer && !booking.review">
                                <p class="text-sm text-gray-600 mb-4">Bagaimana hasil pekerjaan ini? Berikan rating dan ulasan Anda.</p>
                                <form @submit.prevent="submitReview">
                                    <div class="flex gap-2 mb-4">
                                        <button type="button" v-for="n in 5" :key="n" @click="reviewForm.rating = n" class="text-2xl transition hover:scale-110" :class="n <= reviewForm.rating ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'">
                                            <i class="fas fa-star"></i>
                                        </button>
                                    </div>
                                    <textarea v-model="reviewForm.comment" rows="3" placeholder="Tulis pengalaman Anda..." class="w-full rounded-lg border-gray-300 mb-3"></textarea>
                                    <button type="submit" :disabled="reviewForm.processing || reviewForm.rating === 0" class="px-4 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 disabled:opacity-50">
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
                                <div class="p-4 border-b border-gray-50 bg-gray-50">
                                    <h4 class="font-bold text-gray-800 text-sm">Rincian Biaya</h4>
                                </div>
                                <div class="p-5 text-center">
                                    <div v-if="booking.final_price && booking.final_price != booking.initial_price">
                                        <p class="text-xs text-gray-500 mb-1">Harga Awal</p>
                                        <p class="text-sm font-semibold text-gray-400 line-through mb-3">
                                            {{ formatCurrency(booking.initial_price) }}
                                        </p>
                                        <p class="text-xs text-green-600 font-bold uppercase tracking-wider mb-1">
                                            Harga Deal (Revisi)
                                        </p>
                                    </div>
                                    
                                    <div v-else>
                                        <p class="text-xs text-blue-600 font-bold uppercase tracking-wider mb-1">
                                            Harga Pesanan
                                        </p>
                                    </div>

                                    <div class="text-3xl font-extrabold text-gray-900 mb-4">
                                        {{ formatCurrency(booking.final_price || booking.initial_price) }}
                                    </div>

                                    <div v-if="isCustomer && (booking.status === 'pending' || booking.status === 'rejected')">
                                        <Link :href="route('bookings.edit', booking.id)" class="w-full py-2 px-4 bg-yellow-100 border border-yellow-100 text-yellow-700 font-bold rounded-lg hover:bg-yellow-200 transition flex items-center justify-center text-sm shadow-sm">
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

                                    <div v-else-if="booking.status === 'pending'" class="p-2 bg-yellow-50 text-yellow-700 rounded text-xs font-medium border border-yellow-100 flex items-center justify-center text-center">
                                        <i class="fas fa-unlock-alt mr-1.5"></i>
                                        <span>Harga masih estimasi & belum dikunci</span>
                                    </div>

                                    <div v-else-if="booking.status !== 'cancelled' && booking.status !== 'rejected'" class="p-2 bg-green-50 text-green-700 rounded text-xs font-medium border border-green-100">
                                        <i class="fas fa-lock mr-1"></i> Harga & Pesanan Terkunci
                                    </div>
                                </div>
                            </div>
                            
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
                                <p class="text-xs text-gray-500 font-bold uppercase mb-2">Status Pesanan</p>
                                <span class="inline-block px-3 py-1 rounded-full text-sm font-bold uppercase mb-4" :class="getStatusBadge(booking.status)">
                                    {{ booking.status.replace('_', ' ') }}
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
                                        <button @click="updateStatus('pending')" class="w-full py-2 bg-white border border-red-200 text-red-600 hover:bg-red-50 rounded-lg font-bold text-sm">
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
                                        <button @click="updateStatus('confirmed')" class="w-full py-2 bg-blue-100 text-blue-600 rounded-lg font-bold text-sm hover:bg-blue-200 mb-2">
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
                                        <p class="text-xs text-gray-500 mb-2">Silakan menuju lokasi.</p>
                                        <button @click="updateStatus('in_progress')" class="w-full py-2 bg-purple-100 text-purple-600 rounded-lg font-bold text-sm hover:bg-purple-200">
                                            Mulai Pekerjaan
                                        </button>
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

                            <Link :href="route('chats.index', { user_id: isProvider ? booking.customer_id : booking.provider_id, booking_id: booking.id })" 
                                class="w-full py-3 px-4 bg-white border border-blue-600 text-blue-600 hover:bg-blue-50 font-bold rounded-lg transition flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                                </svg>
                                Chat {{ isProvider ? 'Pelanggan' : 'Penyedia' }}
                            </Link>

                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 flex items-center gap-3">
                                <img :src="'https://ui-avatars.com/api/?name=' + (isProvider ? booking.customer.name : booking.provider.name)" class="h-10 w-10 rounded-full border border-gray-100">
                                <div class="overflow-hidden">
                                    <p class="text-xs text-gray-500">{{ isProvider ? 'Pelanggan' : 'Penyedia Jasa' }}</p>
                                    <p class="font-bold text-sm text-gray-800 truncate">
                                        {{ isProvider ? booking.customer.name : booking.provider.name }}
                                    </p>
                                </div>
                            </div>

                        </div>
                    </div>

                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<style scoped>
#map-detail { z-index: 0; }
.animate-fade-in { animation: fadeIn 0.5s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>