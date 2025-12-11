<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, useForm, Link } from '@inertiajs/vue3';
import { ref, onMounted } from 'vue';

const props = defineProps({
    service: Object,
    categories: Array
});

// State untuk Preview Gambar BARU
const newImagePreviews = ref([]);

// State untuk gambar LAMA yang masih ada (belum dihapus)
const existingGalleries = ref([...props.service.galleries]);

const form = useForm({
    title: props.service.title,
    category_id: props.service.category_id,
    description: props.service.description,
    price_min: props.service.price_min,
    price_max: props.service.price_max,
    location: props.service.location,
    latitude: props.service.latitude,
    longitude: props.service.longitude,
    new_images: [], // File Baru
    deleted_gallery_ids: [] // ID Gambar lama yang mau dihapus
});

// --- LOGIC GAMBAR ---
const handleNewImageUpload = (event) => {
    const files = Array.from(event.target.files);
    newImagePreviews.value = [];
    form.new_images = files;

    files.forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => newImagePreviews.value.push(e.target.result);
        reader.readAsDataURL(file);
    });
};

// Menandai gambar lama untuk dihapus
const markGalleryForDeletion = (id, index) => {
    form.deleted_gallery_ids.push(id); // Masukkan ke daftar hapus
    existingGalleries.value.splice(index, 1); // Hilangkan dari tampilan
};

// --- LOGIC MAP (Sama seperti Create, tapi load posisi awal) ---
let map = null;
let marker = null;

// ... import dan setup lainnya ...

onMounted(() => {
    // LOGIC PERBAIKAN: Cek apakah data lama punya koordinat valid?
    // Jika ada, pakai data DB. Jika tidak (NULL), pakai Default (Monas).
    let lat = props.service.latitude ? parseFloat(props.service.latitude) : -6.175392;
    let lng = props.service.longitude ? parseFloat(props.service.longitude) : 106.827153;

    // Pastikan jika hasil parseFloat NaN, kembalikan ke default
    if (isNaN(lat) || isNaN(lng)) {
        lat = -6.175392;
        lng = 106.827153;
    }

    // Update form state agar tidak null saat disubmit ulang
    if (!props.service.latitude) {
        form.latitude = lat;
        form.longitude = lng;
    }

    // 1. Inisialisasi Map
    map = L.map('map').setView([lat, lng], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const icon = L.icon({
        iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
    });

    // 2. Pasang Marker
    marker = L.marker([lat, lng], { draggable: true, icon: icon }).addTo(map);
    
    // Event: Saat Marker Digeser
    marker.on('dragend', function (e) {
        const position = marker.getLatLng();
        updateCoordinates(position.lat, position.lng);
        fetchAddress(position.lat, position.lng);
    });

    // Event: Saat Peta Diklik
    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        updateCoordinates(e.latlng.lat, e.latlng.lng);
        fetchAddress(e.latlng.lat, e.latlng.lng);
    });
});

const updateCoordinates = (lat, lng) => {
    form.latitude = lat;
    form.longitude = lng;
};

const fetchAddress = async (lat, lng) => {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
        const data = await response.json();
        if (data && data.display_name) {
            form.location = data.display_name; 
        }
    } catch (error) {
        console.error("Gagal mengambil alamat:", error);
    }
};

// Karena method PUT tidak support multipart/form-data di beberapa server,
// Kita gunakan POST dengan _method: PUT (Standar Laravel Inertia untuk file upload)
// GANTI FUNCTION SUBMIT MENJADI INI:
const submit = () => {
    // Kita gunakan transform untuk menyelipkan '_method: PUT' ke dalam data form
    // Ini trik wajib di Laravel + Inertia jika form update memiliki upload file
    form.transform((data) => ({
        ...data,
        _method: 'PUT',
    })).post(route('services.update', props.service));
};

// ... import yang sudah ada ...

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
    <Head title="Edit Jasa" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="mb-6 flex items-center justify-between">
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900">Edit Jasa</h1>
                        <p class="text-sm text-gray-500">Perbarui informasi jasa Anda.</p>
                    </div>
                    <Link :href="route('profile.index')" class="text-sm text-gray-600 hover:text-gray-900">
                        &larr; Kembali
                    </Link>
                </div>

                <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    <form @submit.prevent="submit" class="p-6 md:p-8 space-y-6">

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="md:col-span-2">
                                <label class="block text-sm font-medium text-gray-700 mb-1">Judul Jasa</label>
                                <input v-model="form.title" type="text" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                <div v-if="form.errors.title" class="text-red-500 text-xs mt-1">{{ form.errors.title }}</div>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Kategori</label>
                                <select v-model="form.category_id" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                                </select>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Harga Minimum (Rp)</label>
                                <input v-model="form.price_min" type="number" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Harga Maksimum (Rp)</label>
                                <input v-model="form.price_max" type="number" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                            </div>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Deskripsi Lengkap</label>
                            <textarea v-model="form.description" rows="5" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"></textarea>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Foto Jasa</label>
                            
                            <p class="text-xs text-gray-500 mb-2" v-if="existingGalleries.length > 0">Foto Saat Ini (Klik X untuk menghapus)</p>
                            <div class="grid grid-cols-4 gap-4 mb-4" v-if="existingGalleries.length > 0">
                                <div v-for="(gallery, index) in existingGalleries" :key="gallery.id" class="relative group aspect-square rounded-lg overflow-hidden border border-gray-200">
                                    <img :src="'/storage/' + gallery.image" class="w-full h-full object-cover">
                                    <button type="button" @click="markGalleryForDeletion(gallery.id, index)" class="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1 h-6 w-6 flex items-center justify-center shadow-sm hover:bg-red-700 transition">
                                        <i class="fas fa-trash-alt text-xs"></i>
                                    </button>
                                </div>
                            </div>

                            <p class="text-xs text-gray-500 mb-2">Tambah Foto Baru</p>
                            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 transition cursor-pointer relative mb-4">
                                <input type="file" multiple @change="handleNewImageUpload" class="absolute inset-0 opacity-0 cursor-pointer w-full h-full">
                                <i class="fas fa-cloud-upload-alt text-3xl text-gray-400 mb-2"></i>
                                <p class="text-sm text-gray-500">Upload foto baru (max.size 2mb)</p>
                            </div>

                            <div v-if="newImagePreviews.length > 0" class="grid grid-cols-4 gap-4">
                                <div v-for="(img, index) in newImagePreviews" :key="index" class="relative aspect-square bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                                    <img :src="img" class="w-full h-full object-cover">
                                    <span class="absolute bottom-0 left-0 bg-green-500 text-white text-[10px] px-2 py-0.5 rounded-tr">Baru</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Update Lokasi</label>
                            
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

                                <div v-if="searchResults.length > 0" class="absolute z-50 w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 max-h-60 overflow-y-auto">
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
                            <Link :href="route('profile.index')" class="px-6 py-2.5 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition">
                                Batal
                            </Link>
                            <button type="submit" :disabled="form.processing" class="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition flex items-center">
                                <i v-if="form.processing" class="fas fa-spinner fa-spin mr-2"></i>
                                Simpan Perubahan
                            </button>
                        </div>

                    </form>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>