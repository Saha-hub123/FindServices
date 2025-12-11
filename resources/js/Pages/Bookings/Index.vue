<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { onMounted, onUnmounted, computed, ref } from 'vue'; // Tambah onUnmounted
import { Head, Link, useForm, router, usePage } from '@inertiajs/vue3';

const props = defineProps({
    myBookings: Array,
    incomingOrders: Array,
    history: Array // Data baru
});

// State untuk Tab Aktif (Default: Booking Saya)
const activeTab = ref('my_bookings'); 

// Helper Format Rupiah
const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value);
};

// Helper Format Tanggal: "Senin, 01 Jan 2025"
const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('id-ID', {
        weekday: 'long',  // Senin
        day: '2-digit',   // 01
        month: 'short',   // Jan
        year: 'numeric'   // 2025
    });
};

// Helper Format Waktu: Hapus detik (14:30:00 -> 14:30)
const formatTime = (timeString) => {
    if (!timeString) return '-';
    // Ambil 5 karakter pertama saja (HH:mm)
    return timeString.substring(0, 5);
};

// Contoh implementasi di Index.vue

onMounted(() => {
    // Gabungkan array booking saya & pesanan masuk
    const allBookings = [...props.myBookings, ...props.incomingOrders];

    allBookings.forEach(booking => {
        window.Echo.private(`booking.${booking.id}`)
            .listen('BookingStatusUpdated', (e) => {
                // Reload halaman index (partial) untuk update status
                router.reload({ only: ['myBookings', 'incomingOrders'] });
            });
    });
});

onUnmounted(() => {
    // Loop lagi untuk leave channel (cleanup)
    const allBookings = [...props.myBookings, ...props.incomingOrders];
    allBookings.forEach(booking => {
        window.Echo.leave(`booking.${booking.id}`);
    });
});

const getStatusClass = (status) => {
    switch(status) {
        case 'unpaid': return 'bg-gray-200 text-gray-800'; // Abu-abu
        case 'pending': return 'bg-yellow-100 text-yellow-800'; // Kuning
        case 'paid': return 'bg-green-100 text-green-600'; // Hijau Muda (Sudah bayar, tunggu konfirmasi)
        case 'confirmed': return 'bg-blue-100 text-blue-800'; // Biru
        case 'waiting_completion': return 'bg-orange-100 text-orange-800';
        case 'in_progress': return 'bg-purple-100 text-purple-800'; // Ungu (Sedang kerja)
        case 'completed': return 'bg-green-600 text-white'; // Hijau Tua
        case 'cancelled': return 'bg-red-100 text-red-800'; // Merah
        case 'rejected': return 'bg-red-200 text-red-900 line-through'; // Merah Coret
        default: return 'bg-gray-100 text-gray-800';
    }
};

const getStatusLabel = (status) => {
    switch(status) {
        case 'unpaid': return 'Belum Bayar';
        case 'pending': return 'Menunggu Konfirmasi';
        case 'paid': return 'Sudah Dibayar';
        case 'waiting_completion': return 'menunggu Penyelesaian';
        case 'confirmed': return 'Diterima';
        case 'in_progress': return 'Sedang Dikerjakan';
        case 'completed': return 'Selesai';
        case 'cancelled': return 'Dibatalkan';
        case 'rejected': return 'Ditolak';
        default: return status;
    }
};

// 1. STATE FILTER HISTORY
const historyFilter = ref('all'); // Opsi: 'all', 'buy', 'sell'

// 2. COMPUTED PROPERTY
// Memfilter data props.history berdasarkan tombol yang dipilih
const filteredHistory = computed(() => {
    const userId = usePage().props.auth.user.id;
    
    if (historyFilter.value === 'buy') {
        // Tampilkan hanya jika saya sebagai customer
        return props.history.filter(b => b.customer_id === userId);
    } 
    else if (historyFilter.value === 'sell') {
        // Tampilkan hanya jika saya sebagai provider
        return props.history.filter(b => b.provider_id === userId);
    }
    
    // Default: Tampilkan semua
    return props.history;
});
</script>

<template>
    <Head title="Booking Saya" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                

                <div class="flex flex-col md:flex-row gap-6">
                    
                    <div class="w-full md:w-1/4">
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden sticky top-24">
                            <div class="p-4 border-b border-gray-100">
                                <h2 class="font-bold text-lg text-gray-800">Menu Booking</h2>
                            </div>
                            <nav class="flex flex-col p-2 space-y-1">
                                <button 
                                    @click="activeTab = 'my_bookings'"
                                    class="flex items-center w-full px-4 py-3 text-left rounded-lg transition-colors duration-200"
                                    :class="activeTab === 'my_bookings' ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-gray-600 hover:bg-gray-50'"
                                >
                                    <div class="p-2 rounded-full mr-3" :class="activeTab === 'my_bookings' ? 'bg-blue-200' : 'bg-gray-200'">
                                        <i class="fas fa-shopping-bag text-sm" :class="activeTab === 'my_bookings' ? 'text-blue-700' : 'text-gray-600'"></i>
                                    </div>
                                    <div>
                                        <span class="block">Jasa yang Dipesan</span>
                                        <span class="text-xs text-gray-500">Pesanan Saya ({{ myBookings.length }})</span>
                                    </div>
                                </button>

                                <button 
                                    @click="activeTab = 'incoming_orders'"
                                    class="flex items-center w-full px-4 py-3 text-left rounded-lg transition-colors duration-200"
                                    :class="activeTab === 'incoming_orders' ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-gray-600 hover:bg-gray-50'"
                                >
                                    <div class="p-2 rounded-full mr-3" :class="activeTab === 'incoming_orders' ? 'bg-blue-200' : 'bg-gray-200'">
                                        <i class="fas fa-store text-sm" :class="activeTab === 'incoming_orders' ? 'text-blue-700' : 'text-gray-600'"></i>
                                    </div>
                                    <div>
                                        <span class="block">Pesanan Masuk</span>
                                        <span class="text-xs text-gray-500">Orderan Saya ({{ incomingOrders.length }})</span>
                                    </div>
                                </button>

                                <button 
                                    @click="activeTab = 'history'"
                                    class="flex items-center w-full px-4 py-3 text-left rounded-lg transition-colors duration-200"
                                    :class="activeTab === 'history' ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-gray-600 hover:bg-gray-50'"
                                >
                                    <div class="p-2 rounded-full mr-3" :class="activeTab === 'history' ? 'bg-blue-200' : 'bg-gray-200'">
                                        <i class="fas fa-history text-sm" :class="activeTab === 'history' ? 'text-blue-700' : 'text-gray-600'"></i>
                                    </div>
                                    <div>
                                        <span class="block">Riwayat Transaksi</span>
                                        <span class="text-xs text-gray-500">Selesai & Dibatalkan</span>
                                    </div>
                                </button>
                            </nav>
                        </div>
                    </div>

                    <div class="w-full md:w-3/4">
                        <h1 class="text-2xl font-bold text-gray-900 mb-6">Aktivitas Booking</h1>
                        <div v-if="activeTab === 'my_bookings'">
                            <div v-if="myBookings.length === 0" class="bg-white rounded-xl p-8 text-center shadow-sm">
                                <i class="fas fa-shopping-basket text-4xl text-gray-300 mb-4"></i>
                                <p class="text-gray-500">Anda belum membooking jasa apapun.</p>
                                <Link :href="route('marketplace.index')" class="text-blue-600 font-semibold mt-2 inline-block hover:underline">Cari Jasa Sekarang</Link>
                            </div>

                            <div v-else class="space-y-4">
                                <div v-for="booking in myBookings" :key="booking.id" class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-5 flex flex-col md:flex-row md:items-center gap-4 transition hover:shadow-md">
                                    
                                    <div class="shrink-0">
                                        <img v-if="booking.service.galleries && booking.service.galleries.length > 0" 
                                             :src="'/storage/' + booking.service.galleries[0].image" 
                                             class="h-24 w-24 object-cover rounded-lg border border-gray-200" alt="Service">
                                        <div v-else class="h-24 w-24 bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">
                                            <i class="fas fa-image text-2xl"></i>
                                        </div>
                                    </div>

                                    <div class="flex-1">
                                        <div class="flex justify-between items-start">
                                            <div>
                                                <div class="flex items-center gap-2 mb-1">
                                                    <span class="text-xs font-bold text-gray-400 font-mono">#CD{{ booking.id }}</span>
                                                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide" :class="getStatusClass(booking.status)">
                                                        {{ getStatusLabel(booking.status) }}
                                                    </span>
                                                </div>

                                                <h3 class="font-bold text-lg text-gray-900 leading-tight">{{ booking.service.title }}</h3>
                                                
                                                <div class="mt-2 space-y-0.5">
                                                    <p class="text-sm text-gray-500">
                                                        <i class="far fa-calendar-alt mr-1 w-4 text-center"></i> 
                                                        <span class="font-medium text-gray-700">{{ formatDate(booking.booking_date) }}</span>
                                                        
                                                        <span class="mx-1 text-gray-300">•</span>
                                                        
                                                        <i class="far fa-clock mr-1"></i>
                                                        <span class="font-medium text-gray-700">{{ formatTime(booking.booking_time) }}</span>
                                                    </p>
                                                    
                                                    <div class="flex items-center mt-1.5">
                                                        <p class="text-sm text-gray-600 mr-1">Provider:</p>
                                                        
                                                        <Link :href="route('profile.show', booking.provider.id)" class="flex items-center group">
                                                            <img :src="booking.provider.avatar ? '/storage/' + booking.provider.avatar : 'https://ui-avatars.com/api/?name=' + booking.provider.name + '&background=random'" 
                                                                class="h-6 w-6 rounded-full object-cover border border-gray-200 mr-1 group-hover:opacity-80 transition group-hover:ring-2 group-hover:ring-blue-100" 
                                                                alt="Provider">
                                                            
                                                            <span class="text-sm font-medium text-gray-700 truncate group-hover:underline transition">
                                                                {{ booking.provider.name }}
                                                            </span>
                                                        </Link>
                                                    </div>
                                                </div>
                                            </div>

                                            <div class="text-right hidden md:block min-w-[120px]">
                                                
                                                <div v-if="booking.final_price">
                                                    <span class="block text-xs text-gray-400 line-through decoration-red-300 decoration-2 mb-0.5">
                                                        {{ formatCurrency(booking.initial_price) }}
                                                    </span>
                                                    <div class="font-bold text-xl text-blue-600">
                                                        {{ formatCurrency(booking.final_price) }}
                                                    </div>
                                                    <span class="text-[10px] text-green-600 font-bold bg-green-50 px-1.5 py-0.5 rounded">
                                                        Fixed Price
                                                    </span>
                                                </div>

                                                <div v-else>
                                                    <span class="block text-xs text-gray-400 mb-0.5">Estimasi Awal</span>
                                                    <div class="font-bold text-lg text-gray-800">
                                                        {{ formatCurrency(booking.initial_price) }}
                                                    </div>
                                                </div>

                                            </div>
                                        </div>
                                    </div>

                                    <div class="flex md:flex-col gap-2 shrink-0 border-t md:border-t-0 md:border-l border-gray-100 pt-3 md:pt-0 md:pl-4 mt-2 md:mt-0">
                                        
                                        <Link :href="route('bookings.show', booking.id)" class="flex-1 md:w-32 inline-flex justify-center items-center px-4 py-2 bg-gray-100 border border-transparent rounded-md font-semibold text-xs text-gray-700 uppercase tracking-widest hover:bg-gray-200 focus:outline-none transition">
                                            <i class="fas fa-eye mr-2"></i> Detail
                                        </Link>

                                        <Link :href="route('chats.index', { user_id: booking.provider_id, booking_id: booking.id })" class="flex-1 md:w-32 inline-flex justify-center items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-blue-700 focus:outline-none transition">
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-white" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                                            </svg> Chat
                                        </Link>
                                    </div>

                                </div>
                            </div>
                        </div>

                        <div v-if="activeTab === 'incoming_orders'">
                            <div v-if="incomingOrders.length === 0" class="bg-white rounded-xl p-8 text-center shadow-sm">
                                <i class="fas fa-inbox text-4xl text-gray-300 mb-4"></i>
                                <p class="text-gray-500">Belum ada pesanan masuk untuk jasa Anda.</p>
                            </div>

                            <div v-else class="space-y-4">
                                <div v-for="booking in incomingOrders" :key="booking.id" class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-5 flex flex-col md:flex-row md:items-center gap-4 transition hover:shadow-md">
                                    
                                    <div class="shrink-0">
                                        <img v-if="booking.service.galleries && booking.service.galleries.length > 0" 
                                             :src="'/storage/' + booking.service.galleries[0].image" 
                                             class="h-24 w-24 object-cover rounded-lg border border-gray-200" alt="Service">
                                        <div v-else class="h-24 w-24 bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">
                                            <i class="fas fa-image text-2xl"></i>
                                        </div>
                                    </div>

                                    <div class="flex-1">
                                        <div class="flex justify-between items-start">
                                            <div>
                                                <div class="flex items-center gap-2 mb-1">
                                                    <span class="text-xs font-bold text-gray-400 font-mono">#CD{{ booking.id }}</span>
                                                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide" :class="getStatusClass(booking.status)">
                                                        {{ getStatusLabel(booking.status) }}
                                                    </span>
                                                </div>

                                                <h3 class="font-bold text-lg text-gray-900 leading-tight">{{ booking.service.title }}</h3>
                                                
                                                <div class="mt-2 space-y-0.5">
                                                    <p class="text-sm text-gray-500">
                                                        <i class="far fa-calendar-alt mr-1 w-4 text-center"></i> 
                                                        <span class="font-medium text-gray-700">{{ formatDate(booking.booking_date) }}</span>
                                                        
                                                        <span class="mx-1 text-gray-300">•</span>
                                                        
                                                        <i class="far fa-clock mr-1"></i>
                                                        <span class="font-medium text-gray-700">{{ formatTime(booking.booking_time) }}</span>
                                                    </p>
                                                    
                                                    <div class="flex items-center mt-1.5">
                                                        <p class="text-sm text-gray-600 mr-1">Customer:</p>
                                                        
                                                        <Link :href="route('profile.show', booking.customer.id)" class="flex items-center group">
                                                            <img :src="booking.customer.avatar ? '/storage/' + booking.customer.avatar : 'https://ui-avatars.com/api/?name=' + booking.customer.name + '&background=random'" 
                                                                class="h-6 w-6 rounded-full object-cover border border-gray-200 mr-1 group-hover:opacity-80 transition group-hover:ring-2 group-hover:ring-blue-100" 
                                                                alt="customer">
                                                            
                                                            <span class="text-sm font-medium text-gray-700 truncate group-hover:underline transition">
                                                                {{ booking.customer.name }}
                                                            </span>
                                                        </Link>
                                                    </div>
                                                </div>
                                            </div>

                                            <div class="text-right hidden md:block min-w-[120px]">
                                                
                                                <div v-if="booking.final_price">
                                                    <span class="block text-xs text-gray-400 line-through decoration-red-300 decoration-2 mb-0.5">
                                                        {{ formatCurrency(booking.initial_price) }}
                                                    </span>
                                                    <div class="font-bold text-xl text-blue-600">
                                                        {{ formatCurrency(booking.final_price) }}
                                                    </div>
                                                    <span class="text-[10px] text-green-600 font-bold bg-green-50 px-1.5 py-0.5 rounded">
                                                        Fixed Price
                                                    </span>
                                                </div>

                                                <div v-else>
                                                    <span class="block text-xs text-gray-400 mb-0.5">Estimasi Awal</span>
                                                    <div class="font-bold text-lg text-gray-800">
                                                        {{ formatCurrency(booking.initial_price) }}
                                                    </div>
                                                </div>

                                            </div>
                                        </div>
                                    </div>

                                    <div class="flex md:flex-col gap-2 shrink-0 mt-3 md:mt-0 md:border-l border-gray-100 md:pl-4 pt-3 md:pt-0">
                                        <Link :href="route('bookings.show', booking.id)" class="flex-1 md:w-32 inline-flex justify-center items-center px-4 py-2 bg-gray-100 rounded-md font-semibold text-xs text-gray-700 uppercase tracking-widest hover:bg-gray-200">
                                            <i class="fas fa-tasks mr-2"></i> Kelola
                                        </Link>
                                        
                                        <Link :href="route('chats.index', { user_id: booking.customer_id, booking_id: booking.id })" class="flex-1 md:w-32 inline-flex justify-center items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-blue-700">
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-white" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                                            </svg> Chat
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div v-if="activeTab === 'history'">
    
                            <div class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
                                <h2 class="text-lg font-bold text-gray-800">Arsip Transaksi</h2>
                                
                                <div class="bg-white p-1 rounded-lg border border-gray-200 flex shadow-sm">
                                    <button 
                                        @click="historyFilter = 'all'"
                                        class="px-4 py-1.5 text-xs font-bold rounded-md transition-all"
                                        :class="historyFilter === 'all' ? 'bg-gray-800 text-white shadow' : 'text-gray-500 hover:bg-gray-50'"
                                    >
                                        Semua
                                    </button>
                                    <button 
                                        @click="historyFilter = 'buy'"
                                        class="px-4 py-1.5 text-xs font-bold rounded-md transition-all flex items-center"
                                        :class="historyFilter === 'buy' ? 'bg-blue-600 text-white shadow' : 'text-gray-500 hover:bg-gray-50'"
                                    >
                                        <i class="fas fa-shopping-bag mr-1.5"></i> Pembelian
                                    </button>
                                    <button 
                                        @click="historyFilter = 'sell'"
                                        class="px-4 py-1.5 text-xs font-bold rounded-md transition-all flex items-center"
                                        :class="historyFilter === 'sell' ? 'bg-green-600 text-white shadow' : 'text-gray-500 hover:bg-gray-50'"
                                    >
                                        <i class="fas fa-store mr-1.5"></i> Penjualan
                                    </button>
                                </div>
                            </div>

                            <div v-if="filteredHistory.length === 0" class="bg-white rounded-xl p-12 text-center shadow-sm border border-dashed border-gray-300">
                                <div class="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <i class="fas fa-history text-3xl text-gray-400"></i>
                                </div>
                                <p class="text-gray-500 font-medium">Tidak ada riwayat untuk filter ini.</p>
                                <button v-if="historyFilter !== 'all'" @click="historyFilter = 'all'" class="text-sm text-blue-600 hover:underline mt-2">
                                    Lihat Semua Riwayat
                                </button>
                            </div>

                            <div v-else class="space-y-4">
                                <div v-for="booking in filteredHistory" :key="booking.id" class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-5 flex flex-col gap-3 transition hover:shadow-md opacity-80 hover:opacity-100 group">
                                    <div class="flex justify-between items-center pb-2 border-b border-gray-50">
                                        <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded"
                                            :class="booking.customer_id === $page.props.auth.user.id ? 'bg-blue-50 text-blue-600' : 'bg-green-50 text-green-600'">
                                            {{ booking.customer_id === $page.props.auth.user.id ? 'PEMBELIAN' : 'PENJUALAN' }}
                                        </span>
                                        <span class="text-xs text-gray-400 italic">Arsip</span>
                                    </div>

                                    <div class="flex flex-col md:flex-row md:items-center gap-4">
                                        
                                        <div class="shrink-0">
                                            <img v-if="booking.service.galleries && booking.service.galleries.length > 0" 
                                                :src="'/storage/' + booking.service.galleries[0].image" 
                                                class="h-24 w-24 object-cover rounded-lg border border-gray-200 grayscale group-hover:grayscale-0 transition duration-300" alt="Service">
                                            <div v-else class="h-24 w-24 bg-gray-100 rounded-lg flex items-center justify-center text-gray-400 group-hover:text-gray-600 transition duration-300">
                                                <i class="fas fa-image text-2xl"></i>
                                            </div>
                                        </div>

                                        <div class="flex-1">
                                            <div class="flex justify-between items-start">
                                                <div>
                                                    <div class="flex items-center gap-2 mb-1">
                                                        <span class="text-xs font-bold text-gray-400 font-mono">#CD{{ booking.id }}</span>
                                                        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide" :class="getStatusClass(booking.status)">
                                                            {{ getStatusLabel(booking.status) }}
                                                        </span>
                                                    </div>

                                                    <h3 class="font-bold text-lg text-gray-900 leading-tight">{{ booking.service.title }}</h3>
                                                    
                                                    <div class="mt-2 space-y-0.5">
                                                        <p class="text-sm text-gray-500">
                                                            <i class="far fa-calendar-alt mr-1 w-4 text-center"></i> 
                                                            <span class="font-medium text-gray-700">{{ formatDate(booking.booking_date) }}</span>
                                                            <span class="mx-1 text-gray-300">•</span>
                                                            <i class="far fa-clock mr-1"></i>
                                                            <span class="font-medium text-gray-700">{{ formatTime(booking.booking_time) }}</span>
                                                        </p>
                                                        
                                                        <div class="flex items-center mt-1.5">
    
                                                            <template v-if="booking.customer_id === $page.props.auth.user.id">
                                                                <p class="text-sm text-gray-600 mr-1">Provider:</p>
                                                                
                                                                <Link :href="route('profile.show', booking.provider.id)" class="flex items-center group/profile relative z-20">
                                                                    
                                                                    <img :src="booking.provider.avatar ? '/storage/' + booking.provider.avatar : 'https://ui-avatars.com/api/?name=' + booking.provider.name + '&background=random&color=fff'" 
                                                                        class="h-6 w-6 rounded-full object-cover border border-gray-200 mr-2 transition 
                                                                                group-hover/profile:opacity-80 
                                                                                group-hover/profile:ring-2 group-hover/profile:ring-blue-100"
                                                                        alt="Provider">
                                                                    
                                                                    <span class="text-sm font-medium text-gray-700 truncate transition 
                                                                                group-hover/profile:text-gray-600 
                                                                                group-hover/profile:underline">
                                                                        {{ booking.provider.name }}
                                                                    </span>
                                                                </Link>
                                                            </template>
                                                            
                                                            <template v-else>
                                                                <p class="text-sm text-gray-600 mr-1">Customer:</p>
                                                                
                                                                <Link :href="route('profile.show', booking.customer.id)" class="flex items-center group/profile relative z-20">
                                                                    
                                                                    <img :src="booking.customer.avatar ? '/storage/' + booking.customer.avatar : 'https://ui-avatars.com/api/?name=' + booking.customer.name + '&background=random&color=fff'" 
                                                                        class="h-6 w-6 rounded-full object-cover border border-gray-200 mr-2 transition 
                                                                                group-hover/profile:opacity-80 
                                                                                group-hover/profile:ring-2 group-hover/profile:ring-blue-100"
                                                                        alt="Customer">
                                                                    
                                                                    <span class="text-sm font-medium text-gray-700 truncate transition 
                                                                                group-hover/profile:text-gray-600 
                                                                                group-hover/profile:underline">
                                                                        {{ booking.customer.name }}
                                                                    </span>
                                                                </Link>
                                                            </template>

                                                        </div>
                                                    </div>
                                                </div>

                                                <div class="text-right hidden md:block min-w-[120px]">
                                                    <div v-if="booking.final_price">
                                                        <span class="block text-xs text-gray-400 line-through decoration-red-300 decoration-2 mb-0.5">
                                                            {{ formatCurrency(booking.initial_price) }}
                                                        </span>
                                                        <div class="font-bold text-xl text-gray-700">
                                                            {{ formatCurrency(booking.final_price) }}
                                                        </div>
                                                        <span class="text-[10px] text-gray-500 font-bold bg-gray-100 px-1.5 py-0.5 rounded">
                                                            Final
                                                        </span>
                                                    </div>
                                                    <div v-else>
                                                        <span class="block text-xs text-gray-400 mb-0.5">Estimasi</span>
                                                        <div class="font-bold text-lg text-gray-700">
                                                            {{ formatCurrency(booking.initial_price) }}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="flex md:flex-col gap-2 shrink-0 mt-3 md:mt-0 md:border-l border-gray-100 md:pl-4 pt-3 md:pt-0 justify-center">
                                            <Link :href="route('bookings.show', booking.id)" class="flex-1 md:w-32 inline-flex justify-center items-center px-4 py-2 bg-white border border-gray-300 rounded-md font-semibold text-xs text-gray-700 uppercase tracking-widest hover:bg-gray-50 transition">
                                                Lihat Detail
                                            </Link>
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>