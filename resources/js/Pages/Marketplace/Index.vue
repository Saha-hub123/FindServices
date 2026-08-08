<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import MarketplaceCard from '@/Components/MarketplaceCard.vue';
import { Head, useForm } from '@inertiajs/vue3';
import { ref, watch, computed } from 'vue'; // Tambah watch
import axios from 'axios'; // Tambah axios

const props = defineProps({
    services: Object,
    categories: Array,
    filters: Object
});

const searchForm = useForm({
    search: props.filters.search || '',
    category: props.filters.category || '',
    price_min: props.filters.price_min || '',
    price_max: props.filters.price_max || '',
    rating_avg: props.filters.rating_avg || '',
    // Pastikan ini sesuai dengan nama kolom database
    latitude: props.filters.latitude || '', 
    longitude: props.filters.longitude || '',
    radius: props.filters.radius || 10,
    location_name: props.filters.location_name || '',
});

const submitSearch = () => {
    searchForm.get(route('marketplace.index'), { 
        preserveState: true,  // Agar input tidak hilang/reset
        preserveScroll: true, // <--- TAMBAHKAN INI (Agar tidak scroll ke atas)
        replace: true,        // Opsional: Agar history browser tidak penuh (user bisa back dengan nyaman)
    });
};

const locationResults = ref([]);
const isSearchingLocation = ref(false);
let debounceTimer = null;

// --- TAMBAHAN BARU: LOGIC LOKASI SAYA ---
const isLoadingMyLocation = ref(false);

const useMyLocation = () => {
    if (!navigator.geolocation) {
        alert("Browser Anda tidak mendukung fitur Geolocation.");
        return;
    }

    isLoadingMyLocation.value = true;

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            // 1. Simpan Koordinat ke Form
            searchForm.latitude = lat;
            searchForm.longitude = lon;

            // 2. Reverse Geocoding (Koordinat -> Nama Jalan) agar UX bagus
            try {
                const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
                const data = await res.json();
                
                // Ambil bagian alamat yang relevan (Kecamatan/Kota)
                // Nominatim kadang mengembalikan alamat sangat panjang, kita ambil display_name atau address parts
                searchForm.location_name = data.display_name; 
            } catch (e) {
                console.error("Gagal reverse geocode:", e);
                // Jika gagal dapat nama, isi koordinat saja sebagai fallback
                searchForm.location_name = `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
            } finally {
                isLoadingMyLocation.value = false;
                submitSearch(); // Langsung trigger pencarian
            }
        },
        (error) => {
            console.error(error);
            let msg = "Gagal mengambil lokasi.";
            if (error.code === 1) msg = "Izin lokasi ditolak. Mohon aktifkan izin lokasi di browser Anda.";
            else if (error.code === 2) msg = "Lokasi tidak tersedia / sinyal GPS lemah.";
            else if (error.code === 3) msg = "Waktu permintaan lokasi habis.";
            
            alert(msg);
            isLoadingMyLocation.value = false;
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
};

const searchLocation = () => {
    if (searchForm.location_name.length < 3) return;
    
    isSearchingLocation.value = true;
    clearTimeout(debounceTimer);
    
    debounceTimer = setTimeout(async () => {
        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchForm.location_name)}&limit=5`);
            locationResults.value = await res.json();
        } catch (e) { console.error(e); } 
        finally { isSearchingLocation.value = false; }
    }, 500);
};

// --- PERBAIKAN UTAMA ADA DISINI ---
const selectLocation = (loc) => {
    // API Nominatim mengembalikan 'lat' dan 'lon'
    // Kita simpan ke form sebagai 'latitude' dan 'longitude'
    searchForm.latitude = loc.lat; 
    searchForm.longitude = loc.lon;
    
    searchForm.location_name = loc.display_name;
    locationResults.value = []; 
    submitSearch(); 
};

const resetFilter = () => {
    searchForm.search = '';
    searchForm.category = '';
    searchForm.price_min = '';
    searchForm.price_max = '';
    searchForm.rating_avg = '';
    searchForm.latitude = '';
    searchForm.longitude = '';
    searchForm.location_name = '';
    searchForm.radius = 10;
    
    // Menggunakan router.get ke URL dasar adalah cara paling ampuh
    searchForm.get(route('marketplace.index'), {
        preserveState: false, // Jangan simpan state lama
        preserveScroll: true, // Agar tidak lompat ke atas
        data: {}, // Kosongkan data kiriman
        onFinish: () => showMobileFilter.value = false // Tutup modal saat reset
    });
};

// 1. State Lokal (Menampung data gabungan)
// Inisialisasi dengan data halaman pertama dari props
const allServices = ref([...props.services.data]);
const nextPageUrl = ref(props.services.next_page_url);
const isLoadingMore = ref(false);

// 2. Watcher (PENTING!)
// Saat user melakukan Filter (Search/Harga/Lokasi), props.services akan berubah.
// Kita harus me-reset allServices agar sesuai dengan hasil filter baru.
watch(() => props.services, (newVal) => {
    allServices.value = [...newVal.data];
    nextPageUrl.value = newVal.next_page_url;
});

// 3. Function Load More (Axios)
const loadMore = async () => {
    if (!nextPageUrl.value || isLoadingMore.value) return;

    isLoadingMore.value = true;

    try {
        const response = await axios.get(nextPageUrl.value);
        
        // Gabungkan data lama + data baru
        const newServices = response.data.data;
        allServices.value = [...allServices.value, ...newServices];

        // Update link next page
        nextPageUrl.value = response.data.next_page_url;
    } catch (error) {
        console.error("Gagal memuat data:", error);
    } finally {
        isLoadingMore.value = false;
    }
};
// -----------------------
// Fungsi untuk memformat angka jadi format Rupiah (contoh: 1.000.000)
const formatNumber = (value) => {
    if (!value) return '';
    // Hapus karakter non-digit dulu
    const number = value.replace(/\D/g, '');
    // Format jadi ada titiknya
    return new Intl.NumberFormat('id-ID').format(number);
};

// Handler khusus input harga
// key: bisa 'price_min' atau 'price_max'
const handlePriceInput = (event, key) => {
    // Ambil nilai mentah (hanya angka)
    let rawValue = event.target.value.replace(/\D/g, '');
    
    // Simpan ke form (data asli untuk dikirim ke backend)
    searchForm[key] = rawValue;

    // Update tampilan input agar ada titiknya
    event.target.value = formatNumber(rawValue);

    // Trigger pencarian jika diperlukan (karena @change di input teks kadang butuh enter/blur)
    // Jika Anda ingin search saat enter/blur, biarkan @change="submitSearch" di template
};

// Buat Computed Property untuk mengurutkan
const sortedCategories = computed(() => {
    if (!props.categories) return [];

    // 1. Cari kategori 'Lain-lain' (Sesuaikan dengan slug di database kamu)
    // Misal slug-nya 'lain-lain' atau 'others'
    const otherCategory = props.categories.find(c => c.slug === 'lain-lain' || c.slug === 'others');

    // 2. Ambil semua kategori KECUALI 'Lain-lain'
    const mainCategories = props.categories.filter(c => c.slug !== 'lain-lain' && c.slug !== 'others');

    // 3. Jika 'Lain-lain' ketemu, taruh di paling belakang. Jika tidak, kembalikan list biasa.
    if (otherCategory) {
        return [...mainCategories, otherCategory];
    }
    
    return mainCategories;
});

// State untuk Mobile Filter Bottom Sheet
const showMobileFilter = ref(false);

</script>

<template>
    <Head title="Marketplace Jasa" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="flex flex-col lg:flex-row gap-8">

                    <div class="hidden lg:block w-full lg:w-72 shrink-0">
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden top-24">

                            <div class="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                                <h2 class="font-bold text-gray-800 flex items-center gap-2">
                                    <i class="fas fa-sliders-h text-blue-600 text-sm"></i> Filter
                                </h2>

                                <button @click="resetFilter"
                                    class="text-xs font-semibold text-red-500 hover:text-red-700 hover:underline transition flex items-center gap-1"
                                    v-if="searchForm.search || searchForm.category || searchForm.price_min || searchForm.price_max || searchForm.rating_avg || searchForm.latitude">
                                    <i class="fas fa-undo"></i> Reset
                                </button>
                            </div>

                            <div class="p-5 space-y-6">

                                <div>
                                    <label
                                        class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-2 block">Kata
                                        Kunci</label>
                                    <div class="relative group">
                                        <i class="fas fa-search absolute left-3 top-3 text-gray-400 group-focus-within:text-blue-500 transition"></i>
                                        <input v-model="searchForm.search" @keyup.enter="submitSearch" type="text"
                                            placeholder="Cari nama jasa..."
                                            class="w-full bg-white border border-gray-200 rounded-lg py-2.5 pl-10 pr-4 text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition shadow-sm">
                                    </div>
                                </div>

                                <hr class="border-gray-100">

                                <div>
                                    <label
                                        class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-2 block">Rentang
                                        Harga</label>
                                    <div class="space-y-2">
                                        <div class="relative">
                                            <span
                                                class="absolute left-3 top-2.5 text-xs text-gray-500 font-bold">Rp</span>
                                            <input :value="formatNumber(searchForm.price_min?.toString() || '')"
                                                @input="(e) => handlePriceInput(e, 'price_min')" @change="submitSearch"
                                                type="text" placeholder="Min"
                                                class="w-full bg-white border border-gray-200 rounded-lg py-2 pl-9 pr-2 text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition">
                                        </div>

                                        <div class="relative">
                                            <span
                                                class="absolute left-3 top-2.5 text-xs text-gray-500 font-bold">Rp</span>
                                            <input :value="formatNumber(searchForm.price_max?.toString() || '')"
                                                @input="(e) => handlePriceInput(e, 'price_max')" @change="submitSearch"
                                                type="text" placeholder="Max"
                                                class="w-full bg-white border border-gray-200 rounded-lg py-2 pl-9 pr-2 text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition">
                                        </div>
                                    </div>
                                </div>

                                <hr class="border-gray-100">

                                <div>
                                    <label
                                        class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-2 block">Rating
                                        Service</label>
                                    <div class="space-y-1">
                                        <button v-for="star in [4, 3, 2, 1]" :key="star"
                                            @click="searchForm.rating_avg == star ? searchForm.rating_avg = '' : searchForm.rating_avg = star; submitSearch()"
                                            class="w-full flex items-center px-2 py-1.5 rounded-lg hover:bg-gray-50 transition group">
                                            <div class="w-4 h-4 rounded-full border flex items-center justify-center mr-3 transition-colors"
                                                :class="searchForm.rating_avg == star ? 'border-blue-600 bg-blue-600' : 'border-gray-300 bg-white group-hover:border-blue-400'">
                                                <div class="w-1.5 h-1.5 bg-white rounded-full"
                                                    v-if="searchForm.rating_avg == star"></div>
                                            </div>

                                            <div class="flex items-center text-yellow-400 text-xs mr-2">
                                                <i v-for="n in 5" :key="n" class="fas fa-star"
                                                    :class="n <= star ? '' : 'text-gray-200'"></i>
                                            </div>
                                            <span class="text-sm text-gray-600">& Up</span>
                                        </button>
                                    </div>
                                </div>

                                <hr class="border-gray-100">

                                <div>
                                    <div class="flex justify-between items-end mb-2">
                                        <label
                                            class="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">Lokasi
                                            & Jarak</label>

                                        <button @click="useMyLocation" :disabled="isLoadingMyLocation"
                                            class="text-[10px] font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 transition disabled:opacity-50 disabled:cursor-not-allowed">
                                            <i class="fas"
                                                :class="isLoadingMyLocation ? 'fa-spinner fa-spin' : 'fa-crosshairs'"></i>
                                            <span>{{ isLoadingMyLocation ? 'Mencari...' : 'Gunakan Lokasi Saya'
                                                }}</span>
                                        </button>
                                    </div>

                                    <div class="relative mb-3">
                                        <i class="fas fa-map-marker-alt absolute left-3 top-3 text-red-500 z-10"></i>

                                        <input v-model="searchForm.location_name" @input="searchLocation" type="text"
                                            placeholder="Ketik kecamatan/kota..."
                                            class="w-full bg-white border border-gray-200 rounded-lg py-2.5 pl-9 pr-8 text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition shadow-sm truncate">

                                        <button v-if="searchForm.location_name"
                                            @click="searchForm.location_name = ''; searchForm.latitude = ''; searchForm.longitude = ''; submitSearch()"
                                            class="absolute right-2 top-2 text-gray-400 hover:text-red-500 p-1 rounded-full hover:bg-gray-100 transition z-10"
                                            title="Hapus Lokasi">
                                            <i class="fas fa-times-circle"></i>
                                        </button>

                                        <div v-if="isSearchingLocation"
                                            class="absolute right-8 top-2.5 text-blue-500 animate-spin">
                                            <i class="fas fa-spinner"></i>
                                        </div>

                                        <div v-if="locationResults.length > 0"
                                            class="absolute z-50 w-full bg-white border border-gray-200 rounded-lg shadow-xl mt-1 max-h-48 overflow-y-auto">
                                            <ul>
                                                <li v-for="(loc, idx) in locationResults" :key="idx"
                                                    @click="selectLocation(loc)"
                                                    class="px-3 py-2 hover:bg-blue-50 cursor-pointer text-xs text-gray-700 border-b border-gray-50 last:border-0 flex gap-2 items-start text-left">
                                                    <i class="fas fa-map-pin text-gray-400 mt-0.5 shrink-0"></i>
                                                    <span class="line-clamp-2 leading-snug">{{ loc.display_name
                                                        }}</span>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>

                                    <div v-if="searchForm.latitude"
                                        class="bg-blue-50 p-3 rounded-lg border border-blue-100 animate-fade-in transition-all duration-300">
                                        <div class="flex justify-between items-center mb-2">
                                            <span class="text-xs font-bold text-blue-800">Radius Cari:</span>
                                            <span
                                                class="text-xs font-bold text-blue-600 bg-white px-2 py-0.5 rounded shadow-sm border border-blue-100">
                                                {{ searchForm.radius }} KM
                                            </span>
                                        </div>
                                        <input type="range" v-model="searchForm.radius" @change="submitSearch" min="1"
                                            max="50" step="1"
                                            class="w-full h-1.5 bg-blue-200 rounded-lg appearance-none cursor-pointer accent-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300">
                                        <div class="flex justify-between text-[10px] text-blue-400 mt-1 font-medium">
                                            <span>1km</span>
                                            <span>50km</span>
                                        </div>
                                    </div>
                                </div>

                                <hr class="border-gray-100">

                                <div>
                                    <div class="flex justify-between items-end mb-2">
                                        <label
                                            class="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">Kategori</label>
                                        <span v-if="searchForm.category"
                                            class="text-[10px] text-blue-600 font-bold bg-blue-50 px-1.5 py-0.5 rounded">Terpilih</span>
                                    </div>

                                    <div class="space-y-1 max-h-[250px] overflow-y-auto custom-scrollbar pr-1">

                                        <button @click="searchForm.category = ''; submitSearch()"
                                            class="w-full text-left px-3 py-2 rounded-lg flex items-center transition-colors group"
                                            :class="searchForm.category === '' ? 'bg-blue-50 text-blue-700 font-semibold ring-1 ring-blue-100' : 'hover:bg-gray-50 text-gray-600'">
                                            <div class="w-5 h-5 flex items-center justify-center mr-3">
                                                <i class="fas fa-th-large text-xs"
                                                    :class="searchForm.category === '' ? 'text-blue-600' : 'text-gray-400'"></i>
                                            </div>
                                            <span class="text-sm">Semua Jasa</span>
                                        </button>

                                        <button v-for="cat in sortedCategories" :key="cat.id"
                                            @click="searchForm.category = cat.slug; submitSearch()"
                                            class="w-full text-left px-3 py-2 rounded-lg flex items-center transition-colors group"
                                            :class="searchForm.category === cat.slug ? 'bg-blue-50 text-blue-700 font-semibold ring-1 ring-blue-100' : 'hover:bg-gray-50 text-gray-600'">

                                            <div class="w-5 h-5 flex items-center justify-center mr-3">
                                                <i :class="[
                                                    cat.icon_class || 'fas fa-tag',
                                                    'text-xs',
                                                    searchForm.category === cat.slug ? 'text-blue-600' : 'text-gray-400'
                                                ]"></i>
                                            </div>
                                            <span class="text-sm truncate">{{ cat.name }}</span>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div class="p-4 bg-gray-50 border-t border-gray-100">
                                <button @click="submitSearch"
                                    class="w-full py-2.5 bg-gray-900 hover:bg-black text-white rounded-lg font-bold text-sm shadow-lg shadow-gray-200 transition transform active:scale-95">
                                    Terapkan Filter
                                </button>
                            </div>

                        </div>
                    </div>

                    <div class="flex-1 min-w-0  lg:mb-0 mb-12">

                        <div class="flex flex-row items-center justify-between mb-4 lg:mb-6">
                            <div>
                                <h1 class="text-xl lg:text-2xl font-bold text-gray-900">Marketplace Jasa</h1>
                                <p class="text-xs lg:text-sm text-gray-500 mt-1">Temukan jasa profesional terbaik.</p>
                            </div>

                            <button @click="showMobileFilter = true"
                                class="lg:hidden flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-full shadow-sm text-sm font-semibold text-gray-700 hover:bg-gray-50 active:bg-gray-100 transition">
                                <i class="fas fa-sliders-h text-blue-600"></i>
                                <span>Filter</span>
                                <span v-if="searchForm.category || searchForm.price_min"
                                    class="w-2 h-2 bg-red-500 rounded-full"></span>
                            </button>
                        </div>

                        <div v-if="allServices.length > 0">

                            <div class="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6">
                                <MarketplaceCard v-for="service in allServices" :key="service.id" :service="service" />
                            </div>

                            <div v-if="nextPageUrl" class="mt-10 flex justify-center">
                                <button @click="loadMore" :disabled="isLoadingMore"
                                    class="px-8 py-3 bg-white border border-gray-300 text-gray-700 rounded-full font-bold shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-70 transition-all flex items-center gap-2 group">
                                    <span v-if="isLoadingMore">
                                        <i class="fas fa-spinner fa-spin text-blue-600"></i> Memuat...
                                    </span>
                                    <span v-else class="flex items-center gap-2">
                                        Muat Lebih Banyak
                                        <i
                                            class="fas fa-chevron-down text-xs transition-transform duration-300 group-hover:translate-y-0.5"></i>
                                    </span>
                                </button>
                            </div>

                            <div v-else-if="allServices.length > 12"
                                class="mt-10 text-center text-xs text-gray-400 italic">
                                - Semua jasa telah ditampilkan -
                            </div>

                        </div>

                        <div v-else class="bg-white rounded-xl border border-gray-200 p-12 text-center shadow-sm">
                            <div
                                class="h-20 w-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <i class="fas fa-search text-3xl text-gray-400"></i>
                            </div>
                            <h3 class="text-lg font-bold text-gray-900 mb-1">Tidak ada hasil ditemukan</h3>
                            <p class="text-gray-500">Coba ubah kata kunci atau filter pencarian Anda.</p>
                            <button @click="resetFilter" class="mt-4 text-blue-600 font-semibold hover:underline">
                                Reset Pencarian
                            </button>
                        </div>
                    </div>

                </div>
            </div>
        </div>
        <Teleport to="body">
        <div v-if="showMobileFilter" class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm transition-opacity"
            @click="showMobileFilter = false"></div>

        <div class="fixed inset-x-0 bottom-0 z-50 bg-white rounded-t-2xl shadow-2xl transform transition-transform duration-300 ease-out flex flex-col max-h-[90vh]"
            :class="showMobileFilter ? 'translate-y-0' : 'translate-y-full'">
            
            <div class="px-4 py-3 border-b border-gray-100 flex justify-between items-center bg-gray-50 rounded-t-2xl">
                <h3 class="font-bold text-lg text-gray-800 flex items-center gap-2">
                    <i class="fas fa-sliders-h text-blue-600"></i> Filter Pencarian
                </h3>
                <button @click="showMobileFilter = false" class="p-2 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>

            <div class="p-5 overflow-y-auto custom-scrollbar space-y-6">

                <div>
                    <label class="text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
                        <i class="fas fa-search text-blue-500"></i> Kata Kunci
                    </label>
                    <input v-model="searchForm.search" type="text" placeholder="Cari jasa..."
                        class="w-full bg-gray-50 border-gray-200 rounded-lg text-sm py-3 focus:ring-blue-500 focus:border-blue-500">
                </div>

                <hr class="border-gray-100">

                <div>
                    <div class="flex justify-between items-center mb-2">
                        <label class="text-xs font-bold text-gray-500 uppercase flex items-center gap-2">
                            <i class="fas fa-map-marker-alt text-red-500"></i> Lokasi
                        </label>
                        <button @click="useMyLocation"
                            class="text-xs text-blue-600 font-bold flex items-center gap-1 px-2 py-1">
                            <i class="fas fa-crosshairs"></i> Lokasi Saya
                        </button>
                    </div>
                    
                    <input v-model="searchForm.location_name" @input="searchLocation" type="text"
                        placeholder="Kecamatan/Kota..."
                        class="w-full bg-gray-50 border-gray-200 rounded-lg text-sm py-3 mb-2 focus:ring-blue-500 focus:border-blue-500">

                    <div v-if="searchForm.latitude" class="mt-2 bg-blue-50 p-3 rounded-lg border border-blue-100">
                        <div class="flex justify-between text-xs font-bold text-blue-800 mb-2">
                            <span>Radius Area</span>
                            <span class="bg-white px-2 py-0.5 rounded shadow-sm">{{ searchForm.radius }} KM</span>
                        </div>
                        <input type="range" v-model="searchForm.radius" min="1" max="50"
                            class="w-full h-1.5 bg-blue-200 rounded-lg appearance-none cursor-pointer accent-blue-600">
                        <div class="flex justify-between text-[10px] text-blue-400 mt-1">
                            <span>1 km</span>
                            <span>50 km</span>
                        </div>
                    </div>
                </div>

                <hr class="border-gray-100">

                <div>
                    <label class="text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
                        <i class="fas fa-tag text-green-500"></i> Rentang Harga
                    </label>
                    <div class="flex gap-3">
                        <div class="relative w-1/2">
                            <span class="absolute left-3 top-3 text-gray-400 text-xs font-bold">Rp</span>
                            <input :value="formatNumber(searchForm.price_min?.toString())"
                                @input="(e) => handlePriceInput(e, 'price_min')" type="text" placeholder="Min"
                                class="w-full bg-gray-50 border-gray-200 rounded-lg text-sm py-3 pl-8">
                        </div>
                        <div class="relative w-1/2">
                            <span class="absolute left-3 top-3 text-gray-400 text-xs font-bold">Rp</span>
                            <input :value="formatNumber(searchForm.price_max?.toString())"
                                @input="(e) => handlePriceInput(e, 'price_max')" type="text" placeholder="Max"
                                class="w-full bg-gray-50 border-gray-200 rounded-lg text-sm py-3 pl-8">
                        </div>
                    </div>
                </div>

                <hr class="border-gray-100">

                <div>
                    <label class="text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
                        <i class="fas fa-star text-yellow-500"></i> Rating Minimal
                    </label>
                    <div class="grid grid-cols-2 gap-3">
                        <button v-for="star in [4, 3, 2, 1]" :key="star"
                            @click="searchForm.rating_avg == star ? searchForm.rating_avg = '' : searchForm.rating_avg = star"
                            class="flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border transition text-sm font-medium"
                            :class="searchForm.rating_avg == star 
                                ? 'border-yellow-400 bg-yellow-50 text-yellow-700 ring-1 ring-yellow-400' 
                                : 'border-gray-200 bg-gray-50 text-gray-600 hover:bg-gray-100'">
                            
                            <div class="flex text-yellow-400 text-xs">
                                <i v-for="n in 5" :key="n" class="fas fa-star" :class="n <= star ? '' : 'text-gray-300'"></i>
                            </div>
                            <span class="text-xs">& Up</span>
                        </button>
                    </div>
                </div>

                <hr class="border-gray-100">

                <div>
                    <label class="text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
                        <i class="fas fa-th-large text-purple-500"></i> Kategori
                    </label>
                    <div class="grid grid-cols-2 gap-2">
                        <button @click="searchForm.category = ''"
                            class="px-3 py-2.5 rounded-lg text-xs font-medium border text-center transition flex items-center justify-center gap-2"
                            :class="searchForm.category === '' ? 'border-blue-500 bg-blue-50 text-blue-700 ring-1 ring-blue-500' : 'border-gray-200 bg-gray-50 text-gray-600'">
                            <span><i class="fas fa-th-large mr-2 opacity-70"></i>Semua</span>
                        </button>
                        <button v-for="cat in sortedCategories" :key="cat.id"
                            @click="searchForm.category = cat.slug"
                            class="px-3 py-2.5 rounded-lg text-xs font-medium border text-center truncate transition flex items-center justify-center gap-2"
                            :class="searchForm.category === cat.slug ? 'border-blue-500 bg-blue-50 text-blue-700 ring-1 ring-blue-500' : 'border-gray-200 bg-gray-50 text-gray-600'">
                            <i v-if="cat.icon_class" :class="cat.icon_class" class="text-[10px] opacity-70"></i>
                            <span>{{ cat.name }}</span>
                        </button>
                    </div>
                </div>
            </div>

            <div class="p-4 border-t border-gray-100 bg-white pb-safe rounded-t-none">
                <div class="flex gap-3">
                    <button @click="resetFilter"
                        class="w-1/3 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-bold text-sm transition">
                        Reset
                    </button>
                    <button @click="submitSearch(); showMobileFilter = false;"
                        class="w-2/3 py-3 bg-gray-900 hover:bg-black text-white rounded-xl font-bold text-sm shadow-lg shadow-gray-200 transition transform active:scale-95">
                        Tampilkan Hasil
                    </button>
                </div>
            </div>
        </div>
    </Teleport>
    </AuthenticatedLayout>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: #cbd5e1;
    border-radius: 20px;
}
</style>