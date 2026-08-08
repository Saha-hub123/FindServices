<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, useForm, Link } from '@inertiajs/vue3';
import { ref, onMounted, computed, nextTick } from 'vue';

// Props menerima data Booking yang sudah ada (termasuk relasi service didalamnya)
const props = defineProps({
    booking: Object,
    bookedDates: Object,
    adminFee: Number, // <--- Ini data kiriman dari Controller (misal: 4000)
});

// Shortcut untuk akses data service
const service = props.booking.service;

// Helper untuk hitung harga jasa saat ini (sebelum diedit di form ini)
// Jika final_price ada, berarti Revised Price = Final - Admin.
// Jika belum ada final_price, berarti masih pakai Initial.
const currentServicePrice = props.booking.final_price 
    ? (parseFloat(props.booking.final_price) - parseFloat(props.booking.admin_fee || 0))
    : parseFloat(props.booking.initial_price);

// Inisialisasi Form dengan Data Existing
const form = useForm({
    booking_date: props.booking.booking_date ? props.booking.booking_date.split('T')[0] : '', // Pastikan format YYYY-MM-DD
    booking_time: props.booking.booking_time ? props.booking.booking_time.substring(0, 5) : '',
    location: props.booking.location,
    latitude: parseFloat(props.booking.latitude),
    longitude: parseFloat(props.booking.longitude),
    notes: props.booking.notes,
    // UBAH DISINI: revised_price
    revised_price: currentServicePrice,
    payment_method: props.booking.payment_method || 'manual',
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
    } catch (e) { console.error(e); }
};

onMounted(() => {
    // Gunakan Koordinat dari Booking yang sedang diedit
    const lat = form.latitude;
    const lng = form.longitude;

    map = L.map('map-booking').setView([lat, lng], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OSM contributors'
    }).addTo(map);

    const icon = L.icon({
        iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
        iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34],
    });

    marker = L.marker([lat, lng], { draggable: true, icon: icon }).addTo(map);

    // Event Listeners
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

    // Scroll ke jam
    if (form.booking_time) {
        scrollToSelectedTime();
    }
});

// --- 2. LOGIC TIME & VALIDATION ---
const timeError = ref('');

// Generate Slot Waktu (00:00 - 23:30)
const availableTimeSlots = computed(() => {
    const slots = [];
    for (let h = 0; h < 24; h++) {
        slots.push(`${String(h).padStart(2, '0')}:00`);
        slots.push(`${String(h).padStart(2, '0')}:30`);
    }
    return slots;
});

// Cek apakah slot waktu harus didisable
const isSlotDisabled = (timeStr) => {
    if (!form.booking_date) return true;

    // 1. Setup Tanggal yang dipilih (Reset jam ke 00:00)
    const selectedDate = new Date(form.booking_date);
    selectedDate.setHours(0, 0, 0, 0);

    // 2. Setup Hari Ini (Reset jam ke 00:00)
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // KONDISI A: Jika tanggal yang dipilih adalah MASA LALU -> Disable Semua
    if (selectedDate < today) return true;

    // KONDISI B: Jika tanggal adalah HARI INI -> Cek Jam
    if (selectedDate.getTime() === today.getTime()) {
        
        // Pengecualian UX: 
        // Jika tanggal & jam sama persis dengan DATA ASLI (Existing Booking), 
        // JANGAN disable (biarkan user tetap di jam itu kecuali dia mau ubah).
        const originalDate = props.booking.booking_date.split('T')[0];
        const originalTime = props.booking.booking_time.substring(0, 5); // Ambil HH:mm
        
        if (form.booking_date === originalDate && timeStr === originalTime) {
            return false; // Biarkan aktif
        }

        // Logic normal: Minimal 15 menit dari sekarang
        const [h, m] = timeStr.split(':').map(Number);
        const slotTime = new Date();
        slotTime.setHours(h, m, 0, 0);

        const nowPlus15 = new Date();
        nowPlus15.setMinutes(nowPlus15.getMinutes() + 15);

        return slotTime < nowPlus15;
    }

    // KONDISI C: Tanggal masa depan -> Enable Semua
    return false;
};

// Validasi saat submit/pilih
const validateTime = () => {
    if (!form.booking_date || !form.booking_time) {
        timeError.value = '';
        return;
    }
    // Jika user memilih waktu yang disabled (misal lewat inspect element)
    if (isSlotDisabled(form.booking_time)) {
        timeError.value = 'Waktu tidak valid atau sudah terlewat.';
        // Opsional: Reset form.booking_time = '' jika ingin strict
    } else {
        timeError.value = '';
    }
};

const selectTimeSlot = (time) => {
    if (isSlotDisabled(time)) return;
    form.booking_time = time;
    validateTime();
};

// AUTO SCROLL KE JAM TERPILIH SAAT LOAD
const scrollToSelectedTime = () => {
    nextTick(() => {
        const activeBtn = document.querySelector('.time-slot-active');
        if (activeBtn) {
            activeBtn.scrollIntoView({ block: 'center', behavior: 'smooth' });
        }
    });
};

// --- 3. LOGIC CALENDAR (Start from Booking Date) ---
const currentDate = new Date(form.booking_date); // Mulai dari tanggal booking, bukan hari ini
const currentMonth = ref(currentDate.getMonth());
const currentYear = ref(currentDate.getFullYear());
const monthNames = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"];
const startFromDate = form.booking_date ? new Date(form.booking_date) : new Date();

const daysInMonth = computed(() => {
    const days = [];
    const date = new Date(currentYear.value, currentMonth.value, 1);
    
    // SETUP TANGGAL HARI INI (LOKAL)
    const now = new Date();
    const todayStr = [
        now.getFullYear(),
        String(now.getMonth() + 1).padStart(2, '0'),
        String(now.getDate()).padStart(2, '0')
    ].join('-');

    // Padding kosong awal bulan
    for (let i = 0; i < date.getDay(); i++) days.push({ day: '', fullDate: null });

    // Loop tanggal
    while (date.getMonth() === currentMonth.value) {
        
        // FORMAT MANUAL YYYY-MM-DD (Supaya tidak kena bug Timezone)
        const y = date.getFullYear();
        const m = String(date.getMonth() + 1).padStart(2, '0');
        const d = String(date.getDate()).padStart(2, '0');
        const dateString = `${y}-${m}-${d}`;

        // Ambil data booking dari props (booking ini sendiri sudah di-exclude dari controller)
        const count = props.bookedDates[dateString] || 0;

        days.push({
            day: date.getDate(),
            fullDate: dateString,
            count: count,
            isFull: count >= 5, // Batas 5 Slot
            isBusy: count > 0 && count < 5,
            
            // Logika Past: Tanggal kalender < Hari ini
            isPast: dateString < todayStr, 
            
            // Logika Selected: Tanggal kalender === Tanggal di Form
            isSelected: form.booking_date === dateString
        });
        
        date.setDate(date.getDate() + 1);
    }
    return days;
});

const selectDate = (day) => {
    if (!day.fullDate) return;
    if (day.isPast) return; 
    
    if (day.isFull) {
        alert("Maaf, jadwal penuh pada tanggal ini.");
        return;
    }

    form.booking_date = day.fullDate;
    // validateTime(); // Panggil validasi waktu jika ada functionnya
};

const changeMonth = (step) => {
    let newMonth = currentMonth.value + step;
    let newYear = currentYear.value;

    if (newMonth > 11) {
        newMonth = 0;
        newYear++;
    } else if (newMonth < 0) {
        newMonth = 11;
        newYear--;
    }

    currentMonth.value = newMonth;
    currentYear.value = newYear;
};

// --- 4. SUBMIT (PUT) ---
const submit = () => {
    validateTime();
    if (timeError.value || !form.booking_date || !form.booking_time || !form.location) {
        alert("Mohon lengkapi data dengan benar.");
        return;
    }
    // Gunakan PUT untuk update
    form.put(route('bookings.update', props.booking.hash_id));
};

// 2. LOGIKA PERHITUNGAN 4 HARGA (SINKRON DENGAN KONSEP BARU)
const pricingSummary = computed(() => {
    // 1. Harga Awal (Tetap/History)
    const initialPrice = parseFloat(props.booking.initial_price) || 0;
    
    // 2. Harga Revisi (Dari Input Slider/Form)
    const revisedPrice = parseFloat(form.revised_price) || 0;
    
    // 3. Admin Fee
    let fee = 0;
    if (form.payment_method === 'gateway') {
        if (props.booking.payment_method === 'gateway') {
            fee = parseFloat(props.booking.admin_fee);
        } else {
            fee = props.adminFee;
        }
    } else {
        fee = 0;
    }
    
    // 4. Total Akhir
    const total = revisedPrice + fee;

    return {
        initial: initialPrice,
        revised: revisedPrice,
        fee: fee,
        total: total,
        // Cek apakah ada kenaikan/penurunan
        diff: revisedPrice - initialPrice
    };
});

const formatCurrency = (val) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(val);

// Helper 1: Format angka ke tampilan (10000 -> 10.000)
// Menggunakan parseInt untuk membuang desimal (.00) dari database
const formatInputCurrency = (value) => {
    if (value === null || value === undefined || value === '') return '';
    const integerValue = parseInt(value);
    if (isNaN(integerValue)) return '';
    return integerValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
};

// Helper 2: Parse tampilan ke angka murni (10.000 -> 10000)
const parseInputCurrency = (event, field) => {
    let displayValue = event.target.value;
    let rawValue = displayValue.replace(/\./g, '').replace(/\D/g, '');
    
    // Simpan ke form sebagai angka
    form[field] = rawValue ? parseInt(rawValue) : '';
    
    // Update tampilan input agar user melihat titik saat mengetik
    event.target.value = formatInputCurrency(rawValue);
};
</script>

<template>
    <Head title="Edit Pesanan" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 lg:mb-0 mb-12">
                
                <form @submit.prevent="submit" class="flex flex-col lg:flex-row gap-6">
                    
                    <div class="w-full lg:w-3/4 space-y-6">
                        
                        <div class="flex items-center justify-between">
                            <div>
                                <Link :href="route('bookings.show', booking.hash_id)" class="text-sm text-gray-500 hover:text-blue-600">&larr; Kembali ke Detail</Link>
                                <h1 class="text-2xl font-bold text-gray-900">Edit Pesanan #{{ booking.hash_id }}</h1>
                            </div>
                        </div>
                        
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                <span class="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">1</span>
                                Ubah Tanggal & Waktu
                            </h2>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <div class="flex justify-between items-center mb-4">
                                        <button type="button" @click="changeMonth(-1)" class="p-1 hover:bg-gray-100 rounded"><i class="fas fa-chevron-left"></i></button>
                                        <span class="font-bold text-gray-700">{{ monthNames[currentMonth] }} {{ currentYear }}</span>
                                        <button type="button" @click="changeMonth(1)" class="p-1 hover:bg-gray-100 rounded"><i class="fas fa-chevron-right"></i></button>
                                    </div>
                                    <div class="grid grid-cols-7 gap-1 text-center text-sm">
                                        <div v-for="h in ['Min','Sen','Sel','Rab','Kam','Jum','Sab']" :key="h" class="font-bold text-gray-500 text-xs py-2">
                                            {{ h }}
                                        </div>

                                        <div v-for="(day, index) in daysInMonth" :key="index" 
                                            class="h-10 flex items-center justify-center rounded cursor-pointer transition relative border"
                                            :class="{
                                                'border-transparent': !day.isSelected,

                                                // 1. TERPILIH (Biru Solid)
                                                'bg-blue-600 text-white shadow-md border-blue-600': day.isSelected,

                                                // 2. PENUH (Merah - Disable)
                                                'bg-red-50 text-red-300 cursor-not-allowed border-red-50': day.isFull && !day.isSelected,

                                                // 3. RAMAI (Oranye)
                                                'bg-orange-50 text-orange-600 border-orange-200 hover:bg-orange-100': day.isBusy && !day.isSelected && !day.isPast,

                                                // 4. AVAILABLE (Putih)
                                                'hover:bg-blue-50 text-gray-700 border-gray-100': !day.isFull && !day.isBusy && !day.isPast && !day.isSelected && day.day,

                                                // 5. MASA LALU (Abu)
                                                'text-gray-300 cursor-not-allowed bg-gray-50': day.isPast,
                                                
                                                'invisible': !day.day
                                            }"
                                            @click="day.day ? selectDate(day) : null"
                                        >
                                            <span v-if="day.day">{{ day.day }}</span>

                                            <span v-if="day.isFull && !day.isSelected" class="absolute bottom-1 w-1.5 h-1.5 bg-red-400 rounded-full"></span>
                                            <span v-if="day.isBusy && !day.isSelected" class="absolute bottom-1 w-1.5 h-1.5 bg-orange-400 rounded-full"></span>
                                        </div>
                                    </div>
                                    <div class="flex gap-4 mt-4 text-xs justify-center">
                                        <div class="flex items-center gap-1"><span class="w-3 h-3 bg-red-50 border border-red-200 rounded"></span> Penuh</div>
                                        <div class="flex items-center gap-1"><span class="w-3 h-3 bg-orange-50 border border-orange-200 rounded"></span> Terisi Sebagian</div>
                                        <div class="flex items-center gap-1"><span class="w-3 h-3 border border-gray-200 rounded"></span> Kosong</div>
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

                                        <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-2 p-2">
                                            <button 
                                                v-for="time in availableTimeSlots" 
                                                :key="time"
                                                type="button"
                                                @click="selectTimeSlot(time)"
                                                :disabled="isSlotDisabled(time)"
                                                class="py-2 px-1 rounded-lg text-sm font-medium transition-all duration-200 border relative"
                                                :class="{
                                                    // KONDISI TERPILIH (Tambahkan class 'time-slot-active' untuk scroll)
                                                    'bg-blue-600 text-white border-blue-600 shadow-md transform scale-105 time-slot-active': form.booking_time === time,
                                                    
                                                    // KONDISI AVAILABLE (Tidak dipilih & Tidak Disabled)
                                                    'bg-white text-gray-700 border-gray-200 hover:border-blue-400 hover:text-blue-600': form.booking_time !== time && !isSlotDisabled(time),
                                                    
                                                    // KONDISI DISABLED
                                                    'bg-gray-100 text-gray-300 border-transparent cursor-not-allowed opacity-60': isSlotDisabled(time)
                                                }"
                                            >
                                                {{ time }}
                                                
                                                <span v-if="form.booking_date === booking.booking_date.split('T')[0] && time === booking.booking_time.substring(0, 5)" 
                                                    class="absolute -top-1 -right-1 flex h-2 w-2" title="Jadwal Saat Ini">
                                                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                                                    <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                                                </span>
                                            </button>
                                        </div>
                                    </div>
                                    <div v-if="timeError" class="text-red-500 text-xs mt-1">{{ timeError }}</div>
                                    <div v-if="form.errors.booking_time" class="text-red-500 text-xs mt-1">{{ form.errors.booking_time }}</div>

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
                                Ubah Lokasi
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
                                Edit Catatan
                            </h2>
                            <textarea v-model="form.notes" rows="3" placeholder="Keluhan atau detail khusus..." class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"></textarea>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
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

                                <label class="relative flex items-center justify-between p-4 border rounded-xl cursor-pointer transition-all"
                                    :class="form.payment_method === 'gateway' ? 'border-blue-600 bg-blue-50 ring-1 ring-blue-600' : 'border-gray-200 hover:border-gray-300'">
                                    <div class="flex items-center">
                                        <input type="radio" v-model="form.payment_method" value="gateway" class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500">
                                        <div class="ml-3">
                                            <span class="block text-sm font-bold text-gray-900">Pembayaran Otomatis</span>
                                            <span class="block text-xs text-gray-500">QRIS, E-Wallet, Virtual Account</span>
                                        </div>
                                    </div>
                                    <div class="flex gap-2 text-xl">
                                        <i class="fas fa-wallet text-blue-500"></i>
                                        <i class="fas fa-university text-green-500"></i>
                                    </div>
                                </label>

                            </div>
                            <div v-if="form.errors.payment_method" class="text-red-500 text-xs mt-1">{{ form.errors.payment_method }}</div>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                                <span class="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">5</span>
                                Negosiasi Harga
                            </h2>
                            <p class="text-sm text-gray-500 mb-4">Anda dapat mengubah harga penawaran sesuai budget atau kesepakatan baru.</p>

                            <div class="bg-gray-50 p-6 rounded-xl border border-gray-200">
                                <div class="flex justify-between text-sm mb-4 font-medium text-gray-600">
                                    <span>Min: {{ formatCurrency(booking.service.price_min) }}</span>
                                    <span>Max: {{ formatCurrency(booking.service.price_max) }}</span>
                                </div>
                                
                                <input 
                                    type="range" 
                                    v-model.number="form.revised_price" 
                                    :min="booking.service.price_min" 
                                    :max="booking.service.price_max" 
                                    step="5000"
                                    class="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer accent-blue-600 mb-6"
                                >

                                <div class="flex items-center gap-4">
                                    <div class="flex-1">
                                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Harga Penawaran Baru</label>
                                        <div class="relative">
                                            <span class="absolute left-3 top-2.5 text-gray-500 font-bold">Rp</span>
                                            
                                            <input 
                                                type="text" 
                                                inputmode="numeric"
                                                :value="formatInputCurrency(form.revised_price)"
                                                @input="(e) => parseInputCurrency(e, 'revised_price')"
                                                class="w-full rounded-lg border-blue-300 pl-10 focus:border-blue-500 focus:ring-blue-500 font-bold text-gray-900 text-lg transition"
                                                placeholder="0"
                                            >
                                        </div>
                                    </div>
                                    
                                    <div class="text-xs text-gray-500 max-w-[50%] leading-tight">
                                        * Geser slider atau ketik harga manual. 
                                        <span v-if="form.revised_price < booking.service.price_min" class="text-red-500 block mt-1 font-bold">
                                            <i class="fas fa-exclamation-circle"></i> Di bawah harga minimum!
                                        </span>
                                    </div>
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
                                    <h4 class="font-bold text-gray-800 text-sm">Rincian Biaya Baru</h4>
                                </div>
                                <div class="p-4 space-y-3">
                                    
                                    <div class="flex justify-between items-center text-sm">
                                        <span class="text-gray-500 text-xs">Harga Awal</span>
                                        <span class="font-medium text-gray-400 line-through decoration-red-400">
                                            {{ formatCurrency(pricingSummary.initial) }}
                                        </span>
                                    </div>

                                    <div class="flex justify-between items-center text-sm">
                                        <span class="text-gray-600">Harga Revisi</span>
                                        <span class="font-bold text-gray-800">
                                            {{ formatCurrency(pricingSummary.revised) }}
                                        </span>
                                    </div>
                                    
                                    <div v-if="pricingSummary.diff !== 0" class="text-right text-[10px] italic mb-1" 
                                        :class="pricingSummary.diff > 0 ? 'text-red-500' : 'text-green-600'">
                                        ({{ pricingSummary.diff > 0 ? 'Naik' : 'Turun' }} {{ formatCurrency(Math.abs(pricingSummary.diff)) }})
                                    </div>

                                    <div class="flex justify-between items-center text-sm">
                                        <span class="text-gray-600">Biaya Layanan</span>
                                        <span v-if="pricingSummary.fee > 0" class="text-gray-800 font-medium">
                                            {{ formatCurrency(pricingSummary.fee) }}
                                        </span>
                                        <span v-else class="text-green-600 font-medium">Gratis</span>
                                    </div>

                                    <div class="flex justify-between items-center mt-4 pt-3 border-t border-dashed border-gray-300">
                                        <div><span class="block text-xs text-gray-500 font-medium">Total Akhir</span></div>
                                        <span class="font-bold text-xl text-blue-600">
                                            {{ formatCurrency(pricingSummary.total) }}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <button type="submit" 
                                    :disabled="form.processing || !form.booking_date || !form.booking_time || !form.location" 
                                    class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-lg transition flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed">
                                <i v-if="form.processing" class="fas fa-spinner fa-spin mr-2"></i>
                                <span v-if="form.processing">Menyimpan...</span>
                                <span v-else>Simpan Perubahan</span>
                            </button>
                            <Link :href="route('bookings.show', booking.hash_id)" class="block w-full text-center py-2 text-sm text-gray-500 hover:text-gray-800">
                                Batal
                            </Link>

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