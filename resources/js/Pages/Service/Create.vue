<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, useForm, Link } from '@inertiajs/vue3';
import { ref, onMounted } from 'vue';

const props = defineProps({
    categories: Array
});

// State untuk Preview Gambar
const imagePreviews = ref([]);

const form = useForm({
    title: '',
    category_id: '',
    description: '',
    price_min: '',
    price_max: '',
    location: '', // Alamat Teks
    latitude: '', // Koordinat
    longitude: '', // Koordinat
    images: []    // File Asli
});

// --- LOGIC GAMBAR ---
const handleImageUpload = (event) => {
    const files = Array.from(event.target.files);
    
    // Reset jika mau replace, atau push jika mau append (disini replace logic)
    imagePreviews.value = [];
    form.images = files;

    files.forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreviews.value.push(e.target.result);
        };
        reader.readAsDataURL(file);
    });
};

const removeImage = (index) => {
    // Hapus dari preview dan form
    imagePreviews.value.splice(index, 1);
    // Note: Menghapus FileList dari input file itu tricky, 
    // jadi simplenya kita reset form.images menjadi array baru (namun input file asli tidak berubah visualnya)
    // Untuk production yang proper, gunakan library file upload seperti FilePond
    const newImages = Array.from(form.images);
    newImages.splice(index, 1);
    form.images = newImages;
};

// --- LOGIC MAP (LEAFLET) ---
let map = null;
let marker = null;

onMounted(() => {
    // 1. Inisialisasi Map (Default: Monas Jakarta)
    // Jika nanti browser minta izin lokasi, bisa pakai navigator.geolocation
    const defaultLat = -6.175392;
    const defaultLng = 106.827153;

    map = L.map('map').setView([defaultLat, defaultLng], 13);

    // 2. Tambahkan Tile Layer (OSM)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // 3. Ikon Marker Default Leaflet (Fix bug icon hilang di webpack)
    const icon = L.icon({
        iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
    });

    // 4. Buat Marker Awal
    marker = L.marker([defaultLat, defaultLng], { draggable: true, icon: icon }).addTo(map);
    
    // Update Form saat awal
    updateCoordinates(defaultLat, defaultLng);

    // 5. Event: Saat Marker Digeser
    marker.on('dragend', function (e) {
        const position = marker.getLatLng();
        updateCoordinates(position.lat, position.lng);
        fetchAddress(position.lat, position.lng);
    });

    // 6. Event: Saat Peta Diklik
    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        updateCoordinates(e.latlng.lat, e.latlng.lng);
        fetchAddress(e.latlng.lat, e.latlng.lng);
    });
    
    // Coba ambil lokasi user saat ini
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            map.setView([lat, lng], 15);
            marker.setLatLng([lat, lng]);
            updateCoordinates(lat, lng);
            fetchAddress(lat, lng);
        });
    }
});

const updateCoordinates = (lat, lng) => {
    form.latitude = lat;
    form.longitude = lng;
};

// Reverse Geocoding (Gratis pakai Nominatim OSM)
// Mengubah Lat/Lng menjadi Nama Jalan
const fetchAddress = async (lat, lng) => {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
        const data = await response.json();
        if (data && data.display_name) {
            // Kita ambil bagian depannya saja biar tidak kepanjangan
            form.location = data.display_name; 
        }
    } catch (error) {
        console.error("Gagal mengambil alamat:", error);
    }
};

const submit = () => {
    form.post(route('services.store'));
};

// --- TAMBAHAN UNTUK SEARCH LOCATION ---
const searchResults = ref([]);
const isSearching = ref(false);
let debounceTimeout = null;

// Fungsi Mencari Lokasi (Dipanggil saat mengetik)
const searchLocation = () => {
    // 1. Reset hasil jika input kosong
    if (!form.location || form.location.length < 3) {
        searchResults.value = [];
        return;
    }

    isSearching.value = true;

    // 2. Debounce (Tunggu user berhenti ngetik 500ms agar tidak spam API)
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(async () => {
        try {
            // Gunakan API Nominatim
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

// Fungsi Saat Hasil Dipilih
const selectSearchResult = (result) => {
    // 1. Ambil koordinat dari hasil
    const lat = parseFloat(result.lat);
    const lon = parseFloat(result.lon);

    // 2. Update Form
    form.location = result.display_name; // Nama lokasi lengkap
    form.latitude = lat;
    form.longitude = lon;

    // 3. Pindahkan Map & Marker
    if (map && marker) {
        map.setView([lat, lon], 16); // Zoom ke lokasi
        marker.setLatLng([lat, lon]); // Pindah pin
    }

    // 4. Bersihkan pencarian
    searchResults.value = [];
};

// Fungsi menutup dropdown jika klik di luar (Opsional tapi bagus untuk UX)
const closeSearch = () => {
    // Beri delay sedikit agar event click pada list sempat berjalan
    setTimeout(() => {
        searchResults.value = [];
    }, 200);
};
</script>

<template>
    <Head title="Buat Jasa Baru" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="mb-6 flex items-center justify-between">
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900">Buat Jasa Baru</h1>
                        <p class="text-sm text-gray-500">Isi detail lengkap untuk mulai menawarkan jasa.</p>
                    </div>
                    <Link :href="route('profile.index')" class="text-sm text-gray-600 hover:text-gray-900">
                        &larr; Batal
                    </Link>
                </div>

                <div class="bg-white rounded-xl shadow-sm border border-gray-200">
                    <form @submit.prevent="submit" class="p-6 md:p-8 space-y-6">

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="md:col-span-2">
                                <label class="block text-sm font-medium text-gray-700 mb-1">Judul Jasa</label>
                                <input v-model="form.title" type="text" placeholder="Contoh: Service AC Panggilan 24 Jam" 
                                       class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                <div v-if="form.errors.title" class="text-red-500 text-xs mt-1">{{ form.errors.title }}</div>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Kategori</label>
                                <select v-model="form.category_id" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                    <option value="" disabled>Pilih Kategori</option>
                                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                                </select>
                                <div v-if="form.errors.category_id" class="text-red-500 text-xs mt-1">{{ form.errors.category_id }}</div>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Harga Minimum (Rp)</label>
                                <input v-model="form.price_min" type="number" placeholder="50000" 
                                       class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                <div v-if="form.errors.price_min" class="text-red-500 text-xs mt-1">{{ form.errors.price_min }}</div>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Harga Maksimum (Rp)</label>
                                <input v-model="form.price_max" type="number" placeholder="150000" 
                                       class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                <div v-if="form.errors.price_max" class="text-red-500 text-xs mt-1">{{ form.errors.price_max }}</div>
                            </div>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Deskripsi Lengkap</label>
                            <textarea v-model="form.description" rows="5" placeholder="Jelaskan detail layanan, keahlian, dan garansi..." 
                                      class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"></textarea>
                            <div v-if="form.errors.description" class="text-red-500 text-xs mt-1">{{ form.errors.description }}</div>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Foto Jasa (Minimal 1)</label>
                            
                            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 transition cursor-pointer relative">
                                <input type="file" multiple @change="handleImageUpload" class="absolute inset-0 opacity-0 cursor-pointer w-full h-full">
                                <i class="fas fa-cloud-upload-alt text-3xl text-gray-400 mb-2"></i>
                                <p class="text-sm text-gray-500">Klik atau geser foto ke sini (max.size 2mb)</p>
                            </div>

                            <div v-if="imagePreviews.length > 0" class="grid grid-cols-3 md:grid-cols-5 gap-4 mt-4">
                                <div v-for="(img, index) in imagePreviews" :key="index" class="relative group aspect-square bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                                    <img :src="img" class="w-full h-full object-cover">
                                    <button type="button" @click="removeImage(index)" class="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1 h-6 w-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition shadow-sm">
                                        <i class="fas fa-times text-xs"></i>
                                    </button>
                                </div>
                            </div>
                            <div v-if="form.errors.images" class="text-red-500 text-xs mt-1">{{ form.errors.images }}</div>
                        </div>

                        <div class="relative z-10"> <label class="block text-sm font-medium text-gray-700 mb-2">Lokasi / Titik Jemput</label>
                            <p class="text-xs text-gray-500 mb-2">Klik peta atau geser pin untuk menentukan lokasi akurat.</p>
                            
                            <div id="map" class="w-full h-[300px] rounded-lg border border-gray-300 z-0 relative mb-3"></div>
                            
                            <div class="relative">
                                <i class="fas fa-map-marker-alt absolute left-3 top-3 text-red-500 z-10"></i>
                                <input 
                                    v-model="form.location" 
                                    @input="searchLocation"
                                    @blur="closeSearch"
                                    type="text" 
                                    placeholder="Ketik nama jalan/gedung..." 
                                    class="w-full rounded-lg border-gray-300 pl-10 focus:border-blue-500 focus:ring-blue-500 bg-white"
                                    autocomplete="off"
                                >

                                <div v-if="searchResults.length > 0" class="absolute z-50 w-full bg-white border border-gray-200 rounded-lg shadow-xl mt-1 max-h-60 overflow-y-auto">
                                    <ul>
                                        <li v-for="(result, index) in searchResults" :key="index" 
                                            @click="selectSearchResult(result)"
                                            class="px-4 py-3 hover:bg-blue-50 cursor-pointer text-sm text-gray-700 border-b border-gray-100 last:border-0 transition flex items-start gap-2">
                                            <i class="fas fa-map-pin text-gray-400 mt-1"></i>
                                            <span>{{ result.display_name }}</span>
                                        </li>
                                    </ul>
                                </div>

                                <div v-if="isSearching" class="absolute right-3 top-3">
                                    <i class="fas fa-spinner fa-spin text-gray-400"></i>
                                </div>
                            </div>
                            
                            <input type="hidden" v-model="form.latitude">
                            <input type="hidden" v-model="form.longitude">
                            
                            <div v-if="form.errors.location" class="text-red-500 text-xs mt-1">{{ form.errors.location }}</div>
                        </div>

                        <div class="pt-4 border-t border-gray-100 flex justify-end gap-3">
                            <Link :href="route('dashboard')" class="px-6 py-2.5 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition">
                                Batal
                            </Link>
                            <button type="submit" :disabled="form.processing" class="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition flex items-center disabled:opacity-50">
                                <i v-if="form.processing" class="fas fa-spinner fa-spin mr-2"></i>
                                Terbitkan Jasa
                            </button>
                        </div>

                    </form>
                </div>

            </div>
        </div>
    </AuthenticatedLayout>
</template>

<style>
/* Fix Leaflet z-index agar tidak menutupi modal/dropdown jika ada */
.leaflet-pane {
    z-index: 1 !important; 
}
.leaflet-top, .leaflet-bottom {
    z-index: 2 !important;
}
</style>