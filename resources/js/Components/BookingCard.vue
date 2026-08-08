<script setup>
import { Link, usePage } from '@inertiajs/vue3';
import { computed } from 'vue';

const props = defineProps({
    booking: Object,
    type: {
        type: String,
        default: 'customer' // 'customer', 'provider', 'history'
    }
});

const page = usePage();
const authUserId = computed(() => page.props.auth.user.id);

// --- HELPER FORMAT ---
const formatCurrency = (value) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value);

const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('id-ID', { weekday: 'long', day: '2-digit', month: 'short', year: 'numeric' });
};

const formatTime = (timeString) => {
    if (!timeString) return '-';
    return timeString.substring(0, 5);
};

// --- HELPER STATUS CLASS ---
const getBookingClass = (status) => {
    switch(status) {
        case 'pending': return 'bg-yellow-50 text-yellow-700 border border-yellow-200';
        case 'confirmed': return 'bg-blue-50 text-blue-700 border border-blue-200';
        case 'in_progress': return 'bg-purple-50 text-purple-700 border border-purple-200 animate-pulse';
        case 'waiting_completion': return 'bg-indigo-50 text-indigo-700 border border-indigo-200';
        case 'completed': return 'bg-green-50 text-green-700 border border-green-200';
        case 'cancelled': return 'bg-red-50 text-red-700 border border-red-200';
        case 'rejected': return 'bg-red-50 text-red-700 border border-red-200 line-through decoration-red-700';
        default: return 'bg-gray-50 text-gray-500 border border-gray-200';
    }
};

const getBookingLabel = (status) => {
    switch(status) {
        case 'pending': return 'Menunggu Konfirmasi';
        case 'confirmed': return 'Pesanan Diterima';
        case 'in_progress': return 'Sedang Dikerjakan';
        case 'waiting_completion': return 'Menunggu Penyelesaian';
        case 'completed': return 'Selesai';
        case 'cancelled': return 'Dibatalkan';
        case 'rejected': return 'Ditolak Provider';
        default: return status;
    }
};

const getPaymentClass = (status) => {
    switch(status) {
        case 'unpaid': return 'bg-slate-100 text-slate-600 border border-slate-200';
        case 'pending': return 'bg-orange-50 text-orange-700 border border-orange-200';
        case 'paid': return 'bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold';
        case 'failed': return 'bg-rose-50 text-rose-700 border border-rose-200';
        case 'expired': return 'bg-gray-100 text-gray-600 border border-gray-200';
        default: return 'bg-gray-50 text-gray-500';
    }
};

const getPaymentLabel = (status) => {
    switch(status) {
        case 'unpaid': return 'Belum Bayar';
        case 'pending': return 'Menunggu Pembayaran';
        case 'paid': return 'Lunas';
        case 'failed': return 'Gagal';
        case 'expired': return 'Kadaluarsa';
        default: return status;
    }
};
</script>

<template>
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-5 flex flex-col md:flex-row md:items-center gap-4 transition hover:shadow-md group">
        
        <div v-if="type === 'history'" class="md:hidden flex justify-between items-center pb-2 border-b border-gray-50 mb-2 w-full">
            <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded"
                :class="booking.customer_id === authUserId ? 'bg-blue-50 text-blue-600' : 'bg-green-50 text-green-600'">
                {{ booking.customer_id === authUserId ? 'PEMBELIAN' : 'PENJUALAN' }}
            </span>
            <span class="text-xs text-gray-400 italic">Arsip</span>
        </div>

        <div class="shrink-0 relative w-full md:w-auto mb-3 md:mb-0">

            <img v-if="booking.service.galleries && booking.service.galleries.length > 0"
                :src="'/storage/' + booking.service.galleries[0].image" class="object-cover rounded-lg border border-gray-200 shadow-sm
                w-full h-48 md:h-24 md:w-24"
                :class="type === 'history' ? 'grayscale group-hover:grayscale-0 transition duration-300' : ''"
                alt="Service">

            <div v-else class="bg-gray-100 rounded-lg flex items-center justify-center text-gray-400
                w-full h-48 md:h-24 md:w-24">
                <i class="fas fa-image text-3xl md:text-2xl"></i>
            </div>

            <div v-if="type === 'history'" class="hidden md:block absolute -top-2 -left-2 z-10">
                <span
                    class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded shadow-sm border border-white"
                    :class="booking.customer_id === authUserId ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'">
                    {{ booking.customer_id === authUserId ? 'BELI' : 'JUAL' }}
                </span>
            </div>

        </div>

        <div class="flex-1 min-w-0">
            <div class="flex justify-between items-start">
                <div>
                    <div class="flex flex-wrap items-center gap-2 mb-1">
                        <span class="text-xs font-bold text-gray-400 font-mono">#CD{{ booking.hash_id }}</span>
                        <span class="w-fit px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider" 
                            :class="getBookingClass(booking.status)">
                            {{ getBookingLabel(booking.status) }}
                        </span>
                        
                        <span class="w-fit px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider flex items-center gap-1" 
                            :class="getPaymentClass(booking.payment_status)">
                            <i v-if="booking.payment_status === 'paid'" class="fas fa-check-circle text-[9px]"></i>
                            <i v-if="booking.payment_status === 'pending'" class="fas fa-clock text-[9px]"></i>
                            <i v-if="booking.payment_status === 'failed'" class="fas fa-times-circle text-[9px]"></i>
                            {{ getPaymentLabel(booking.payment_status) }}
                        </span>
                    </div>

                    <h3 class="font-bold text-lg text-gray-900 leading-tight truncate pr-2">{{ booking.service.title }}</h3>
                    
                    <div class="mt-2 space-y-0.5">
                        <p class="text-sm text-gray-500">
                            <i class="far fa-calendar-alt mr-1 w-4 text-center"></i> 
                            <span class="font-medium text-gray-700">{{ formatDate(booking.booking_date) }}</span>
                            <span class="mx-1 text-gray-300">•</span>
                            <i class="far fa-clock mr-1"></i>
                            <span class="font-medium text-gray-700">{{ formatTime(booking.booking_time) }}</span>
                        </p>
                        
                        <div class="flex items-center mt-1.5">
                            <template v-if="type === 'customer' || (type === 'history' && booking.customer_id === authUserId)">
                                <p class="text-sm text-gray-600 mr-1">Provider:</p>
                                <Link :href="route('profile.show', booking.provider.hash_id)" class="flex items-center group/profile">
                                    <img :src="booking.provider.avatar ? '/storage/' + booking.provider.avatar : 'https://ui-avatars.com/api/?name=' + booking.provider.name + '&background=random'" 
                                         class="h-6 w-6 rounded-full object-cover border border-gray-200 mr-1 transition group-hover/profile:opacity-80" alt="Prov">
                                    <span class="text-sm font-medium text-gray-700 truncate group-hover/profile:text-blue-600 group-hover/profile:underline transition">
                                        {{ booking.provider.name }}
                                    </span>
                                </Link>
                            </template>
                            
                            <template v-else>
                                <p class="text-sm text-gray-600 mr-1">Customer:</p>
                                <Link :href="route('profile.show', booking.customer.hash_id)" class="flex items-center group/profile">
                                    <img :src="booking.customer.avatar ? '/storage/' + booking.customer.avatar : 'https://ui-avatars.com/api/?name=' + booking.customer.name + '&background=random'" 
                                         class="h-6 w-6 rounded-full object-cover border border-gray-200 mr-1 transition group-hover/profile:opacity-80" alt="Cust">
                                    <span class="text-sm font-medium text-gray-700 truncate group-hover/profile:text-blue-600 group-hover/profile:underline transition">
                                        {{ booking.customer.name }}
                                    </span>
                                </Link>
                            </template>
                        </div>
                    </div>
                </div>

                <div class="text-right hidden md:block min-w-[140px]">
                    <div v-if="booking.status === 'cancelled' || booking.status === 'rejected'">
                        <span class="block text-xs text-gray-400 mb-0.5">
                            {{ booking.status === 'cancelled' ? 'Dibatalkan' : 'Ditolak' }}
                        </span>
                        <div class="font-bold text-lg text-gray-300 line-through decoration-gray-300">
                            {{ formatCurrency(booking.final_price || booking.initial_price) }}
                        </div>
                        <div class="mt-1">
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded uppercase border bg-gray-50 text-gray-400 border-gray-100">
                                {{ booking.status === 'cancelled' ? 'VOID' : 'REJECT' }}
                            </span>
                        </div>
                    </div>

                    <div v-else-if="booking.final_price">
                        <div class="text-xs text-gray-400 mb-0.5 flex justify-end gap-1">
                            <span>Awal:</span>
                            <span :class="(parseFloat(booking.final_price) - parseFloat(booking.admin_fee || 0)) !== parseFloat(booking.initial_price) ? 'line-through decoration-red-300' : ''">
                                {{ formatCurrency(booking.initial_price) }}
                            </span>
                        </div>
                        <div class="text-sm font-bold text-gray-700 mb-0.5">
                            Jasa: {{ formatCurrency(parseFloat(booking.final_price) - parseFloat(booking.admin_fee || 0)) }}
                        </div>
                        <div class="text-xs text-gray-500 mb-1">
                            <span v-if="parseFloat(booking.admin_fee) > 0">+ Fee: {{ formatCurrency(booking.admin_fee) }}</span>
                            <span v-else class="text-green-600 font-bold bg-green-50 px-1 rounded">Fee Gratis</span>
                        </div>
                        <div class="border-t border-dashed border-gray-300 pt-1 mt-1">
                            <div class="font-extrabold text-lg text-blue-600">
                                {{ formatCurrency(booking.final_price) }}
                            </div>
                            <span class="text-[10px] text-white bg-blue-600 px-1.5 py-0.5 rounded font-bold">TOTAL FIX</span>
                        </div>
                    </div>

                    <div v-else>
                        <span class="block text-xs text-gray-500 mb-1 bg-yellow-50 px-2 py-0.5 rounded border border-yellow-100">Estimasi Awal</span>
                        <div class="font-bold text-xl text-gray-400">{{ formatCurrency(booking.initial_price) }}</div>
                        <div class="text-[10px] text-gray-400 mt-1 italic">(Belum final)</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex md:flex-col gap-2 shrink-0 border-t md:border-t-0 md:border-l border-gray-100 pt-3 md:pt-0 md:pl-4 mt-2 md:mt-0 justify-center">
            
            <Link :href="route('bookings.show', booking.hash_id)" 
                class="flex-1 md:w-32 inline-flex justify-center items-center px-4 py-2 bg-gray-100 border border-transparent rounded-md font-semibold text-xs text-gray-700 uppercase tracking-widest hover:bg-gray-200 focus:outline-none transition">
                <i class="fas fa-eye mr-2"></i> Detail
            </Link>

            <Link :href="route('chats.index', { 
    user_id: (type === 'customer' || (type === 'history' && booking.customer_id === authUserId)) 
        ? booking.provider?.hash_id   // GANTI: provider_id -> provider?.hash_id
        : booking.customer?.hash_id,  // GANTI: customer_id -> customer?.hash_id
    
    booking_id: booking.hash_id 
})"
                class="flex-1 md:w-32 inline-flex justify-center items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-blue-700 focus:outline-none transition">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                </svg> Chat
            </Link>
        </div>

    </div>
</template>