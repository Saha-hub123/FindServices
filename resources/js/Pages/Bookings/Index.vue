<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import BookingCard from '@/Components/BookingCard.vue'; // Import Component Baru
import { onMounted, onUnmounted, computed, ref, watch } from 'vue';
import { Head, Link, usePage, router } from '@inertiajs/vue3';
import axios from 'axios';

const props = defineProps({
    myBookings: Object,     // Ubah Array -> Object
    incomingOrders: Object, // Ubah Array -> Object
    history: Object         // Ubah Array -> Object
});

const activeTab = ref('my_bookings'); 

// --- 1. LOAD MORE: MY BOOKINGS ---
const allMyBookings = ref([...props.myBookings.data]);
const nextMyBookingsUrl = ref(props.myBookings.next_page_url);
const isLoadingMyBookings = ref(false);

const loadMoreMyBookings = async () => {
    if (!nextMyBookingsUrl.value || isLoadingMyBookings.value) return;
    isLoadingMyBookings.value = true;
    try {
        const res = await axios.get(nextMyBookingsUrl.value);
        const newData = res.data.myBookings.data;
        allMyBookings.value = [...allMyBookings.value, ...newData];
        nextMyBookingsUrl.value = res.data.myBookings.next_page_url;
    } catch (e) { console.error(e); } 
    finally { isLoadingMyBookings.value = false; }
};

// --- 2. LOAD MORE: INCOMING ORDERS ---
const allIncomingOrders = ref([...props.incomingOrders.data]);
const nextIncomingOrdersUrl = ref(props.incomingOrders.next_page_url);
const isLoadingIncomingOrders = ref(false);

const loadMoreIncomingOrders = async () => {
    if (!nextIncomingOrdersUrl.value || isLoadingIncomingOrders.value) return;
    isLoadingIncomingOrders.value = true;
    try {
        const res = await axios.get(nextIncomingOrdersUrl.value);
        const newData = res.data.incomingOrders.data;
        allIncomingOrders.value = [...allIncomingOrders.value, ...newData];
        nextIncomingOrdersUrl.value = res.data.incomingOrders.next_page_url;
    } catch (e) { console.error(e); } 
    finally { isLoadingIncomingOrders.value = false; }
};

// --- 3. LOAD MORE: HISTORY ---
const allHistory = ref([...props.history.data]);
const nextHistoryUrl = ref(props.history.next_page_url);
const isLoadingHistory = ref(false);

const loadMoreHistory = async () => {
    if (!nextHistoryUrl.value || isLoadingHistory.value) return;
    isLoadingHistory.value = true;
    try {
        const res = await axios.get(nextHistoryUrl.value);
        const newData = res.data.history.data;
        allHistory.value = [...allHistory.value, ...newData];
        nextHistoryUrl.value = res.data.history.next_page_url;
    } catch (e) { console.error(e); } 
    finally { isLoadingHistory.value = false; }
};

// --- FILTER HISTORY (CLIENT SIDE) ---
const historyFilter = ref('all'); // 'all', 'buy', 'sell'

const filteredHistory = computed(() => {
    const userId = usePage().props.auth.user.id;
    let data = allHistory.value; // Gunakan allHistory, bukan props

    if (historyFilter.value === 'buy') {
        return data.filter(b => b.customer_id === userId);
    } else if (historyFilter.value === 'sell') {
        return data.filter(b => b.provider_id === userId);
    }
    return data;
});

// --- WATCHERS UNTUK REALTIME ---
// Jika ada update dari Echo atau Inertia reload, sync data lokal
watch(() => props.myBookings, (newVal) => {
    allMyBookings.value = [...newVal.data];
    nextMyBookingsUrl.value = newVal.next_page_url;
});
watch(() => props.incomingOrders, (newVal) => {
    allIncomingOrders.value = [...newVal.data];
    nextIncomingOrdersUrl.value = newVal.next_page_url;
});
watch(() => props.history, (newVal) => {
    allHistory.value = [...newVal.data];
    nextHistoryUrl.value = newVal.next_page_url;
});

// --- REALTIME ECHO ---
onMounted(() => {
    const all = [...props.myBookings.data, ...props.incomingOrders.data];
    all.forEach(booking => {
        if(window.Echo) {
            window.Echo.private(`booking.${booking.hash_id}`)
                .listen('BookingStatusUpdated', (e) => {
                    router.reload({ only: ['myBookings', 'incomingOrders', 'history'] });
                });
        }
    });
});
</script>

<template>
    <Head title="Booking Saya" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

                <div class="flex flex-col md:flex-row gap-6">
                    
                    <div class="w-full md:w-1/4 hidden lg:block">
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden sticky top-24">
                            <div class="p-4 border-b border-gray-100">
                                <h2 class="font-bold text-lg text-gray-800">Menu Booking</h2>
                            </div>
                            <nav class="flex flex-col p-2 space-y-1">
                                <button @click="activeTab = 'my_bookings'" class="flex items-center w-full px-4 py-3 text-left rounded-lg transition-colors duration-200" :class="activeTab === 'my_bookings' ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-gray-600 hover:bg-gray-50'">
                                    <div class="p-2 rounded-full mr-3" :class="activeTab === 'my_bookings' ? 'bg-blue-200' : 'bg-gray-200'">
                                        <i class="fas fa-shopping-bag text-sm" :class="activeTab === 'my_bookings' ? 'text-blue-700' : 'text-gray-600'"></i>
                                    </div>
                                    <div>
                                        <span class="block">Jasa yang Dipesan</span>
                                        <span class="text-xs text-gray-500">Pesanan Saya ({{ myBookings.total }})</span>
                                    </div>
                                </button>

                                <button @click="activeTab = 'incoming_orders'" class="flex items-center w-full px-4 py-3 text-left rounded-lg transition-colors duration-200" :class="activeTab === 'incoming_orders' ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-gray-600 hover:bg-gray-50'">
                                    <div class="p-2 rounded-full mr-3" :class="activeTab === 'incoming_orders' ? 'bg-blue-200' : 'bg-gray-200'">
                                        <i class="fas fa-store text-sm" :class="activeTab === 'incoming_orders' ? 'text-blue-700' : 'text-gray-600'"></i>
                                    </div>
                                    <div>
                                        <span class="block">Pesanan Masuk</span>
                                        <span class="text-xs text-gray-500">Orderan Saya ({{ incomingOrders.total }})</span>
                                    </div>
                                </button>

                                <button @click="activeTab = 'history'" class="flex items-center w-full px-4 py-3 text-left rounded-lg transition-colors duration-200" :class="activeTab === 'history' ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-gray-600 hover:bg-gray-50'">
                                    <div class="p-2 rounded-full mr-3" :class="activeTab === 'history' ? 'bg-blue-200' : 'bg-gray-200'">
                                        <i class="fas fa-history text-sm" :class="activeTab === 'history' ? 'text-blue-700' : 'text-gray-600'"></i>
                                    </div>
                                    <div>
                                        <span class="block">Riwayat Transaksi</span>
                                        <span class="text-xs text-gray-500">Arsip ({{ history.total }})</span>
                                    </div>
                                </button>
                            </nav>
                        </div>
                    </div>

                    <div class="w-full md:w-3/4 lg:mb-0 mb-12">
                        <h1 class="text-2xl font-bold text-gray-900 mb-6">Aktivitas Booking</h1>
                        
                        <div class="lg:hidden mb-4 sticky top-16 z-20 bg-gray-100/95 backdrop-blur-sm py-2 -mx-4 px-4 md:mx-0 md:px-0 overflow-hidden">

                            <div class="flex overflow-x-auto gap-3 pb-2 hide-scrollbar">

                                <button @click="activeTab = 'my_bookings'"
                                    class="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-full border text-sm font-medium transition-all shadow-sm"
                                    :class="activeTab === 'my_bookings'
                                        ? 'bg-blue-600 text-white border-blue-600'
                                        : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'">

                                    <i class="fas fa-shopping-bag text-xs"></i>
                                    <span>Dipesan</span>
                                    <span class="ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                                        :class="activeTab === 'my_bookings' ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-600'">
                                        {{ myBookings.total }}
                                    </span>
                                </button>

                                <button @click="activeTab = 'incoming_orders'"
                                    class="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-full border text-sm font-medium transition-all shadow-sm"
                                    :class="activeTab === 'incoming_orders'
                                        ? 'bg-blue-600 text-white border-blue-600'
                                        : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'">

                                    <i class="fas fa-store text-xs"></i>
                                    <span>Masuk</span>
                                    <span class="ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                                        :class="activeTab === 'incoming_orders' ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-600'">
                                        {{ incomingOrders.total }}
                                    </span>
                                </button>

                                <button @click="activeTab = 'history'"
                                    class="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-full border text-sm font-medium transition-all shadow-sm"
                                    :class="activeTab === 'history'
                                        ? 'bg-blue-600 text-white border-blue-600'
                                        : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'">

                                    <i class="fas fa-history text-xs"></i>
                                    <span>Riwayat</span>
                                    <span class="ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                                        :class="activeTab === 'history' ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-600'">
                                        {{ history.total }}
                                    </span>
                                </button>

                            </div>
                        </div>
                        <div v-if="activeTab === 'my_bookings'">
                            <div v-if="allMyBookings.length === 0" class="bg-white rounded-xl p-8 text-center shadow-sm">
                                <i class="fas fa-shopping-basket text-4xl text-gray-300 mb-4"></i>
                                <p class="text-gray-500">Anda belum membooking jasa apapun.</p>
                                <Link :href="route('marketplace.index')" class="text-blue-600 font-semibold mt-2 inline-block hover:underline">Cari Jasa Sekarang</Link>
                            </div>
                            <div v-else class="space-y-4">
                                <BookingCard v-for="booking in allMyBookings" :key="booking.id" :booking="booking" type="customer" />
                                
                                <div v-if="nextMyBookingsUrl" class="flex justify-center mt-6">
                                    <button @click="loadMoreMyBookings" :disabled="isLoadingMyBookings" class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-full font-bold shadow-sm hover:bg-gray-50 disabled:opacity-70 text-sm">
                                        {{ isLoadingMyBookings ? 'Memuat...' : 'Muat Lebih Banyak' }}
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div v-if="activeTab === 'incoming_orders'">
                            <div v-if="allIncomingOrders.length === 0" class="bg-white rounded-xl p-8 text-center shadow-sm">
                                <i class="fas fa-inbox text-4xl text-gray-300 mb-4"></i>
                                <p class="text-gray-500">Belum ada pesanan masuk untuk jasa Anda.</p>
                            </div>
                            <div v-else class="space-y-4">
                                <BookingCard v-for="booking in allIncomingOrders" :key="booking.id" :booking="booking" type="provider" />
                                
                                <div v-if="nextIncomingOrdersUrl" class="flex justify-center mt-6">
                                    <button @click="loadMoreIncomingOrders" :disabled="isLoadingIncomingOrders" class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-full font-bold shadow-sm hover:bg-gray-50 disabled:opacity-70 text-sm">
                                        {{ isLoadingIncomingOrders ? 'Memuat...' : 'Muat Lebih Banyak' }}
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div v-if="activeTab === 'history'">
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">

                                <h2 class="hidden sm:block text-lg font-bold text-gray-800">
                                    <i class="fas fa-history text-gray-400 mr-2"></i> Arsip Transaksi
                                </h2>

                                <div
                                    class="w-full sm:w-auto bg-white p-1 rounded-lg border border-gray-200 flex shadow-sm overflow-x-auto">

                                    <button @click="historyFilter = 'all'"
                                        class="flex-1 sm:flex-none px-4 py-2 text-[10px] sm:text-xs font-bold rounded-md transition-all whitespace-nowrap text-center"
                                        :class="historyFilter === 'all' ? 'bg-gray-800 text-white shadow-sm' : 'text-gray-500 hover:bg-gray-50'">
                                        Semua
                                    </button>

                                    <button @click="historyFilter = 'buy'"
                                        class="flex-1 sm:flex-none px-4 py-2 text-[10px] sm:text-xs font-bold rounded-md transition-all flex items-center justify-center whitespace-nowrap"
                                        :class="historyFilter === 'buy' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-500 hover:bg-gray-50'">
                                        <i class="fas fa-shopping-bag mr-1.5"
                                            :class="historyFilter === 'buy' ? 'text-white' : 'text-blue-500'"></i>
                                        Pembelian
                                    </button>

                                    <button @click="historyFilter = 'sell'"
                                        class="flex-1 sm:flex-none px-4 py-2 text-[10px] sm:text-xs font-bold rounded-md transition-all flex items-center justify-center whitespace-nowrap"
                                        :class="historyFilter === 'sell' ? 'bg-green-600 text-white shadow-sm' : 'text-gray-500 hover:bg-gray-50'">
                                        <i class="fas fa-store mr-1.5"
                                            :class="historyFilter === 'sell' ? 'text-white' : 'text-green-500'"></i>
                                        Penjualan
                                    </button>

                                </div>
                            </div>

                            <div v-if="filteredHistory.length === 0" class="bg-white rounded-xl p-12 text-center shadow-sm border border-dashed border-gray-300">
                                <i class="fas fa-history text-3xl text-gray-400 mb-4"></i>
                                <p class="text-gray-500 font-medium">Tidak ada riwayat untuk filter ini.</p>
                            </div>
                            <div v-else class="space-y-4">
                                <BookingCard v-for="booking in filteredHistory" :key="booking.id" :booking="booking" type="history" />

                                <div v-if="nextHistoryUrl" class="flex justify-center mt-6">
                                    <button @click="loadMoreHistory" :disabled="isLoadingHistory" class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-full font-bold shadow-sm hover:bg-gray-50 disabled:opacity-70 text-sm">
                                        {{ isLoadingHistory ? 'Memuat...' : 'Muat Lebih Banyak' }}
                                    </button>
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
/* Sembunyikan Scrollbar tapi tetap bisa di-scroll */
.hide-scrollbar::-webkit-scrollbar {
    display: none;
}
.hide-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
}
</style>