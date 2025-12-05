<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, useForm, Link } from '@inertiajs/vue3';
import { ref, onMounted, computed, nextTick } from 'vue';

const props = defineProps({
    service: Object,
    bookedDates: Object
});

const form = useForm({
    service_id: props.service.id,
    booking_date: '',
    booking_time: '',
    location: '',
    latitude: '',
    longitude: '',
    notes: '',
    initial_price: props.service.price_min,
    payment_method: 'manual', 
    status: 'pending'
});

// --- 1. LOGIC LOCATION SEARCH & MAP ---
const searchResults = ref([]);
const isSearching = ref(false);
let debounceTimeout = null;
let map = null;
let marker = null;

const searchLocation = () => {
    if (!form.location || form.location.length < 3) {
        searchResults.value = [];
        return;
    }
    isSearching.value = true;
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(form.location)}&limit=5`);
            const data = await response.json();
            searchResults.value = data;
        } catch (error) {
            console.error("Error searching location:", error);
        } finally {
            isSearching.value = false;
        }
    }, 500);
};

const selectSearchResult = (result) => {
    const lat = parseFloat(result.lat);
    const lon = parseFloat(result.lon);
    form.location = result.display_name;
    form.latitude = lat;
    form.longitude = lon;
    if (map && marker) {
        map.setView([lat, lon], 16);
        marker.setLatLng([lat, lon]);
    }
    searchResults.value = [];
};

const closeSearch = () => {
    setTimeout(() => { searchResults.value = []; }, 200);
};

const fetchAddress = async (lat, lng) => {
    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
        const data = await res.json();
        if (data.display_name) {
            form.location = data.display_name;
        }
    } catch (e) { 
        console.error(e); 
    }
};

onMounted(() => {
    const defaultLat = props.service.latitude ? parseFloat(props.service.latitude) : -6.175392;
    const defaultLng = props.service.longitude ? parseFloat(props.service.longitude) : 106.827153;

    if(!form.latitude) {
        form.latitude = defaultLat;
        form.longitude = defaultLng;
    }

    map = L.map('map-booking').setView([defaultLat, defaultLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OSM contributors'
    }).addTo(map);

    const icon = L.icon({
        iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34],
    });

    marker = L.marker([defaultLat, defaultLng], { draggable: true, icon: icon }).addTo(map);

    fetchAddress(defaultLat, defaultLng); // Auto fill awal

    marker.on('dragend', function (e) {
        const pos = marker.getLatLng();
        form.latitude = pos.lat;
        form.longitude = pos.lng;
        fetchAddress(pos.lat, pos.lng);
    });

    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        form.latitude = e.latlng.lat;
        form.longitude = e.latlng.lng;
        fetchAddress(e.latlng.lat, e.latlng.lng);
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            map.setView([lat, lng], 16);
            marker.setLatLng([lat, lng]);
            form.latitude = lat;
            form.longitude = lng;
            fetchAddress(lat, lng);
        });
    }
});

// --- 2. LOGIC TIME & VALIDATION (YANG TADI HILANG) ---
const timeError = ref(''); // <--- INI VARIABEL YANG TADI HILANG

const validateTime = () => {
    if (!form.booking_date || !form.booking_time) {
        timeError.value = '';
        return;
    }

    const selectedDate = new Date(form.booking_date);
    const today = new Date();
    
    // Cek apakah tanggal yang dipilih adalah HARI INI
    const isToday = selectedDate.toDateString() === today.toDateString();

    if (isToday) {
        const [hours, minutes] = form.booking_time.split(':').map(Number);
        const selectedTime = new Date();
        selectedTime.setHours(hours, minutes, 0, 0);

        const nowPlus15 = new Date();
        nowPlus15.setMinutes(nowPlus15.getMinutes() + 15);

        if (selectedTime < nowPlus15) {
            timeError.value = 'Waktu minimal 15 menit dari sekarang.';
            form.booking_time = ''; // Reset jika invalid
        } else {
            timeError.value = '';
        }
    } else {
        timeError.value = '';
    }
};

const availableTimeSlots = computed(() => {
    const slots = [];
    const startHour = 0; 
    const endHour = 23.5;  
    
    for (let h = startHour; h <= endHour; h++) {
        slots.push(`${h.toString().padStart(2, '0')}:00`);
        if (h !== endHour) slots.push(`${h.toString().padStart(2, '0')}:30`);
    }
    return slots;
});

const isSlotDisabled = (timeStr) => {
    if (!form.booking_date) return true;

    const selectedDate = new Date(form.booking_date);
    const today = new Date();
    
    if (selectedDate.toDateString() !== today.toDateString()) return false;

    const [hours, minutes] = timeStr.split(':').map(Number);
    const slotTime = new Date();
    slotTime.setHours(hours, minutes, 0, 0);

    const nowPlus15 = new Date();
    nowPlus15.setMinutes(nowPlus15.getMinutes() + 15);

    return slotTime < nowPlus15;
};

const selectTimeSlot = (time) => {
    if (isSlotDisabled(time)) return;
    form.booking_time = time;
    validateTime(); // Validasi ulang untuk memastikan aman
};

// --- 3. LOGIC CALENDAR ---
const currentDate = new Date();
const currentMonth = ref(currentDate.getMonth());
const currentYear = ref(currentDate.getFullYear());
const monthNames = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"];

const daysInMonth = computed(() => {
    const days = [];
    const date = new Date(currentYear.value, currentMonth.value, 1);
    for (let i = 0; i < date.getDay(); i++) days.push({ day: '', fullDate: null });

    while (date.getMonth() === currentMonth.value) {
        const dateObj = new Date(date); 
        dateObj.setHours(12,0,0,0);
        const dateString = dateObj.toISOString().split('T')[0];
        const todayStr = new Date().toISOString().split('T')[0];

        // Ambil jumlah booking dari props (0 jika tidak ada)
        const count = props.bookedDates[dateString] || 0;

        days.push({
            day: date.getDate(),
            fullDate: dateString,
            count: count, // Simpan jumlah booking
            isFull: count >= 5, // Status Penuh (Merah)
            isBusy: count > 0 && count < 5, // Status Ramai (Oranye)
            isPast: dateString < todayStr,
            isSelected: form.booking_date === dateString
        });
        date.setDate(date.getDate() + 1);
    }
    return days;
});

const selectDate = (day) => {
    // Cek isFull (bukan isBooked lagi)
    if (day.isFull || day.isPast || !day.fullDate) return;

    form.booking_date = day.fullDate;
    form.booking_time = ''; 
    validateTime();
};

const changeMonth = (step) => {
    let newMonth = currentMonth.value + step;
    if (newMonth > 11) { currentMonth.value = 0; currentYear.value++; }
    else if (newMonth < 0) { currentMonth.value = 11; currentYear.value--; }
    else { currentMonth.value = newMonth; }
};

// --- 4. SUBMIT ---
const submit = () => {
    validateTime();
    if (timeError.value || !form.booking_date || !form.booking_time || !form.location) {
        alert("Mohon lengkapi data dengan benar.");
        return;
    }
    form.post(route('bookings.store'));
};

const formatCurrency = (val) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(val);
</script>

<template>
    <Head title="Form Booking" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                
                
                <form @submit.prevent="submit" class="flex flex-col lg:flex-row gap-6">
                    
                    
                    <div class="w-full lg:w-3/4 space-y-6">
                        <div>
                           <Link :href="route('service.show',service.id)" class="text-sm text-gray-500 hover:text-blue-600">&larr; Kembali ke Detail Jasa</Link>
                            <h1 class="text-2xl font-bold text-gray-900">Form Pemesanan Jasa</h1>
                        </div>
                        
                        
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                <span class="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">1</span>
                                Pilih Tanggal & Waktu
                            </h2>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <div class="flex justify-between items-center mb-4">
                                        <button type="button" @click="changeMonth(-1)" class="p-1 hover:bg-gray-100 rounded"><i class="fas fa-chevron-left"></i></button>
                                        <span class="font-bold text-gray-700">{{ monthNames[currentMonth] }} {{ currentYear }}</span>
                                        <button type="button" @click="changeMonth(1)" class="p-1 hover:bg-gray-100 rounded"><i class="fas fa-chevron-right"></i></button>
                                    </div>
                                    <div class="grid grid-cols-7 gap-1 text-center text-sm mb-2 font-medium text-gray-500">
                                        <span>Min</span><span>Sen</span><span>Sel</span><span>Rab</span><span>Kam</span><span>Jum</span><span>Sab</span>
                                    </div>
                                    <div class="grid grid-cols-7 gap-1 text-center text-sm">
                                        <div v-for="(day, index) in daysInMonth" :key="index" 
                                            class="h-10 flex items-center justify-center rounded cursor-pointer transition relative border border-transparent"
                                            :class="{
                                                'bg-blue-600 text-white shadow-md border-blue-600': day.isSelected,

                                                // KONDISI PENUH (>= 5): Merah Mati
                                                'bg-red-50 text-red-300 cursor-not-allowed': day.isFull && !day.isSelected,

                                                // KONDISI RAMAI (1-4): Oranye
                                                'bg-orange-50 text-orange-600 border-orange-100 hover:bg-orange-100 hover:border-orange-300': day.isBusy && !day.isSelected && !day.isPast,

                                                // KONDISI KOSONG (0): Putih/Hover Biru
                                                'hover:bg-blue-50 text-gray-700': !day.isFull && !day.isBusy && !day.isPast && !day.isSelected,

                                                // KONDISI LEWAT: Abu
                                                'text-gray-300 cursor-not-allowed': day.isPast
                                            }"
                                            @click="selectDate(day)"
                                        >
                                            {{ day.day }}

                                            <span v-if="day.isFull" class="absolute bottom-1 w-1 h-1 bg-red-400 rounded-full"></span>
                                            <span v-if="day.isBusy" class="absolute bottom-1 w-1 h-1 bg-orange-400 rounded-full"></span>
                                        </div>
                                    </div>
                                    <div class="mt-4 flex flex-wrap gap-3 text-[10px] text-gray-500 justify-center">
                                        <span class="flex items-center">
                                            <span class="w-2.5 h-2.5 bg-blue-600 rounded-full mr-1.5"></span> Dipilih
                                        </span>
                                        <span class="flex items-center">
                                            <span class="w-2.5 h-2.5 bg-red-100 border border-red-200 rounded-full mr-1.5 relative"><span class="absolute inset-0 m-auto w-1 h-1 bg-red-400 rounded-full"></span></span> Penuh (5/5)
                                        </span>
                                        <span class="flex items-center">
                                            <span class="w-2.5 h-2.5 bg-orange-100 border border-orange-200 rounded-full mr-1.5 relative"><span class="absolute inset-0 m-auto w-1 h-1 bg-orange-400 rounded-full"></span></span> Terisi (1-4)
                                        </span>
                                        <span class="flex items-center">
                                            <span class="w-2.5 h-2.5 bg-white border border-gray-300 rounded-full mr-1.5"></span> Kosong
                                        </span>
                                    </div>
                                </div>

                                <div class="flex flex-col">
                                    <div class="mb-4 flex items-center justify-between">
                                        <label class="block text-sm font-bold text-gray-700">Jam Kedatangan</label>
                                        <span v-if="form.booking_time" class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                                            {{ form.booking_time }}
                                        </span>
                                    </div>

                                    <div class="border border-gray-200 rounded-xl p-1 bg-gray-50 h-[280px] overflow-y-auto custom-scrollbar">
                                        <div v-if="!form.booking_date" class="h-full flex flex-col items-center justify-center text-gray-400 text-sm p-4 text-center">
                                            <i class="far fa-calendar-times text-2xl mb-2"></i>
                                            <p>Pilih tanggal terlebih dahulu untuk melihat jam tersedia.</p>
                                        </div>

                                        <div v-else class="grid grid-cols-3 gap-2 p-2">
                                            <button 
                                                v-for="time in availableTimeSlots" 
                                                :key="time"
                                                type="button"
                                                @click="selectTimeSlot(time)"
                                                :disabled="isSlotDisabled(time)"
                                                class="py-2 px-1 rounded-lg text-sm font-medium transition-all duration-200 border"
                                                :class="{
                                                    'bg-blue-600 text-white border-blue-600 shadow-md transform scale-105': form.booking_time === time,
                                                    'bg-white text-gray-700 border-gray-200 hover:border-blue-400 hover:text-blue-600': form.booking_time !== time && !isSlotDisabled(time),
                                                    'bg-gray-100 text-gray-300 border-transparent cursor-not-allowed': isSlotDisabled(time)
                                                }"
                                            >
                                                {{ time }}
                                            </button>
                                        </div>
                                    </div>

                                    <div class="mt-3 text-center">
                                        <div v-if="form.booking_time" class="text-xs text-gray-600 animate-fade-in">
                                            Jadwal: <span class="font-bold text-gray-800">
                                                {{ new Date(form.booking_date).toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'short' }) }}
                                                pukul {{ form.booking_time }}
                                            </span>
                                        </div>
                                        <div v-if="timeError" class="text-xs text-red-500 font-bold mt-1 animate-pulse">
                                            {{ timeError }}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                <span class="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">2</span>
                                Lokasi Pengerjaan
                            </h2>
                            <p class="text-sm text-gray-500 mb-3">Cari alamat atau geser pin di peta untuk lokasi akurat.</p>
                            
                            <div id="map-booking" class="w-full h-[300px] rounded-lg border border-gray-300 z-0 relative mb-3"></div>
                            
                            <div class="relative">
                                <i class="fas fa-search absolute left-3 top-3 text-gray-400 z-10"></i>
                                <input 
                                    v-model="form.location" 
                                    @input="searchLocation"
                                    @blur="closeSearch"
                                    type="text" 
                                    placeholder="Cari nama jalan, gedung, atau perumahan..." 
                                    class="w-full rounded-lg border-gray-300 pl-10 focus:border-blue-500 focus:ring-blue-500 bg-white"
                                    autocomplete="off"
                                >
                                <div v-if="searchResults.length > 0" class="absolute z-50 w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 max-h-60 overflow-y-auto">
                                    <ul>
                                        <li v-for="(result, index) in searchResults" :key="index" 
                                            @click="selectSearchResult(result)"
                                            class="px-4 py-3 hover:bg-blue-50 cursor-pointer text-sm text-gray-700 border-b border-gray-100 last:border-0 transition flex items-start gap-2">
                                            <i class="fas fa-map-pin text-red-500 mt-1 shrink-0"></i>
                                            <span>{{ result.display_name }}</span>
                                        </li>
                                    </ul>
                                </div>
                                <div v-if="isSearching" class="absolute right-3 top-3"><i class="fas fa-spinner fa-spin text-gray-400"></i></div>
                            </div>
                            <div v-if="form.errors.location" class="text-red-500 text-sm mt-1">{{ form.errors.location }}</div>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                <span class="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">3</span>
                                Catatan
                            </h2>
                            <textarea v-model="form.notes" rows="3" placeholder="Keluhan atau detail khusus..." class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"></textarea>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                <span class="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">4</span>
                                Metode Pembayaran
                            </h2>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <label class="relative flex items-center justify-between p-4 border rounded-xl cursor-pointer transition-all"
                                    :class="form.payment_method === 'manual' ? 'border-blue-600 bg-blue-50 ring-1 ring-blue-600' : 'border-gray-200 hover:border-gray-300'">
                                    <div class="flex items-center">
                                        <input type="radio" v-model="form.payment_method" value="manual" class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500">
                                        <div class="ml-3">
                                            <span class="block text-sm font-bold text-gray-900">Bayar Langsung / Manual</span>
                                            <span class="block text-xs text-gray-500">Cash atau Transfer ke Rekening Penyedia</span>
                                        </div>
                                    </div>
                                    <i class="fas fa-hand-holding-usd text-2xl text-gray-400"></i>
                                </label>
                                <div class="relative flex items-center justify-between p-4 border border-gray-200 rounded-xl bg-gray-50 opacity-60 cursor-not-allowed" title="Segera Hadir">
                                    <div class="flex items-center">
                                        <input type="radio" disabled class="h-4 w-4 text-gray-400 border-gray-300">
                                        <div class="ml-3">
                                            <span class="block text-sm font-bold text-gray-500">Pembayaran Otomatis</span>
                                            <span class="block text-xs text-gray-400">E-Wallet, Virtual Account</span>
                                        </div>
                                    </div>
                                    <div class="flex gap-1"><i class="fas fa-wallet text-gray-400"></i><i class="fas fa-university text-gray-400"></i></div>
                                    <span class="absolute top-2 right-2 bg-yellow-100 text-yellow-800 text-[9px] font-bold px-1.5 py-0.5 rounded">SOON</span>
                                </div>
                            </div>
                        </div>

                    </div>

                    <div class="w-full lg:w-1/4">
                        <div class="sticky top-24 space-y-4">
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                
                                <div class="relative h-32 bg-gray-200">
                                    <img v-if="service.galleries.length > 0" :src="'/storage/' + service.galleries[0].image" class="w-full h-full object-cover">
                                    <div v-else class="w-full h-full flex items-center justify-center text-gray-400 bg-gray-100"><i class="fas fa-image"></i></div>
                                </div>
                                <div class="p-4">
                                    <span class="text-[10px] bg-blue-100 text-blue-600 px-2 py-0.5 rounded font-bold uppercase">{{ service.category.name }}</span>
                                    <h3 class="font-bold text-gray-800 mt-2 line-clamp-2 leading-snug">{{ service.title }}</h3>
                                    <div class="mt-4 space-y-3">
                                        <div class="text-xs text-gray-500 flex items-start">
                                            <i class="fas fa-map-marker-alt mr-2 mt-0.5 text-red-500 shrink-0"></i>
                                            <span class="line-clamp-2 leading-relaxed">{{ service.location || 'Lokasi Online' }}</span>
                                        </div>
                                        <div class="pt-3 border-t border-gray-100 flex items-center">
                                            <img :src="'https://ui-avatars.com/api/?name=' + service.user.name" class="h-8 w-8 rounded-full border border-gray-200 mr-3">
                                            <div class="overflow-hidden">
                                                <p class="text-[10px] text-gray-400 uppercase font-bold">Penyedia</p>
                                                <p class="text-sm font-bold text-gray-700 truncate">{{ service.user.name }}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                <div class="p-4 border-b border-gray-50">
                                    <h4 class="font-bold text-gray-800 text-sm">Rincian Pembayaran</h4>
                                </div>
                                <div class="p-4">
                                    <div class="space-y-2">
                                        <div class="flex justify-between items-center text-sm">
                                            <span class="text-gray-600">Estimasi Awal</span>
                                            <span class="font-bold text-gray-800">{{ formatCurrency(service.price_min) }}</span>
                                        </div>
                                        <div class="flex justify-between items-center text-sm">
                                            <span class="text-gray-600">Biaya Layanan</span>
                                            <span class="text-green-600 font-medium">Gratis</span>
                                        </div>
                                    </div>
                                    <div class="mt-3 p-3 bg-yellow-50 border border-yellow-100 text-[11px] text-yellow-800 rounded-lg leading-tight flex gap-2 items-start">
                                        <i class="fas fa-info-circle mt-0.5 shrink-0"></i> 
                                        <span>Harga final mungkin berubah setelah konfirmasi penyedia.</span>
                                    </div>
                                    <div class="flex justify-between items-center mt-4 pt-3 border-t border-dashed border-gray-200">
                                        <div><span class="block text-xs text-gray-500 font-medium">Total Estimasi</span></div>
                                        <span class="font-bold text-xl text-blue-600">{{ formatCurrency(service.price_min) }}</span>
                                    </div>
                                </div>
                            </div>

                            <button type="submit" 
                                    :disabled="form.processing || !form.booking_date || !form.booking_time || !form.location" 
                                    class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-lg transition flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed">
                                <i v-if="form.processing" class="fas fa-spinner fa-spin mr-2"></i>
                                <span v-if="form.processing">Memproses...</span>
                                <span v-else>Buat Pesanan</span>
                            </button>
                            <p class="text-[10px] text-gray-400 text-center mt-2">Dengan membuat pesanan, Anda setuju dengan Syarat & Ketentuan.</p>

                        </div>
                    </div>

                </form>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<style scoped>
#map-booking { z-index: 0; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #e2e8f0; border-radius: 20px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background-color: #cbd5e1; }
</style>