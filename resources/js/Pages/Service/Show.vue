<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link } from '@inertiajs/vue3';
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    service: Object,
    auth_user_id: Number
});

// State untuk toggle deskripsi
const isDescExpanded = ref(false);

// State untuk Galeri Gambar
const activeImage = ref(
    props.service.galleries.length > 0 
    ? '/storage/' + props.service.galleries[0].image 
    : null
);

// Helper Format Rupiah
const formatCurrency = (val) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(val);
};

// Helper Format Tanggal Review
const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' });
};

// Variabel untuk menyimpan instance map
let mapDesktop = null;
let mapMobile = null;

// Fungsi Reusable untuk Membuat Map
const initSingleMap = (elementId) => {
    // 1. Cek apakah elemen HTML-nya ada?
    const element = document.getElementById(elementId);
    if (!element) return null;

    // 2. Cek koordinat
    if (!props.service.latitude || !props.service.longitude) return null;

    const lat = parseFloat(props.service.latitude);
    const lng = parseFloat(props.service.longitude);

    // 3. Inisialisasi Map (Mode Ringan/Lite sesuai kode Anda)
    const mapInstance = L.map(elementId, {
        center: [lat, lng],
        zoom: 13,
        zoomControl: false,      // Hilangkan tombol +/-
        dragging: false,         // Matikan geser
        scrollWheelZoom: false,  // Matikan scroll mouse
        doubleClickZoom: false,  // Matikan double click
        boxZoom: false,
        keyboard: false,
        attributionControl: false // Hilangkan teks copyright
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OSM'
    }).addTo(mapInstance);

    // 4. Custom Icon Kecil (Sesuai kode Anda)
    const icon = L.icon({
        iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
        iconSize: [20, 32], 
        iconAnchor: [10, 32],
        popupAnchor: [1, -34],
    });

    L.marker([lat, lng], { icon: icon }).addTo(mapInstance);

    return mapInstance;
};

// Handler agar map tidak rusak saat resize layar (hidden -> visible)
const handleResize = () => {
    if (mapDesktop) mapDesktop.invalidateSize();
    if (mapMobile) mapMobile.invalidateSize();
};

onMounted(() => {
    // Panggil fungsi untuk kedua ID
    mapDesktop = initSingleMap('mini-map-desktop');
    mapMobile = initSingleMap('mini-map-mobile');

    // Pasang listener resize window
    window.addEventListener('resize', handleResize);
    
    // Panggil sekali di awal dengan sedikit delay untuk memastikan render CSS selesai
    setTimeout(handleResize, 500);
});

onUnmounted(() => {
    // Bersihkan map saat komponen dihancurkan (mencegah memory leak)
    window.removeEventListener('resize', handleResize);
    if (mapDesktop) mapDesktop.remove();
    if (mapMobile) mapMobile.remove();
});

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
    <Head :title="service.title" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 lg:mb-0 mb-10">
                
                <div class="flex flex-col lg:flex-row gap-6">
                    
                    <div class="w-full lg:w-3/4 space-y-6">
                        <div>
                           <Link :href="route('marketplace.index')" class="text-sm text-gray-500 hover:text-blue-600">&larr; Kembali ke Marketplace</Link>
                            <h1 class="text-2xl font-bold text-gray-900">Detail Jasa</h1>
                        </div>
                        
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            
                            <div class="aspect-w-16 aspect-h-9 bg-gray-200 relative h-[400px] flex items-center justify-center overflow-hidden cursor-zoom-in group"
                                @click="openLightbox(activeImage)">
                                <img v-if="activeImage" :src="activeImage"
                                    class="w-full h-full object-cover transition-all duration-300 group-hover:scale-105">

                                <div v-if="activeImage"
                                    class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition flex items-center justify-center opacity-0 group-hover:opacity-100">
                                    <i class="fas fa-search-plus text-white text-3xl drop-shadow-lg"></i>
                                </div>

                                <div v-else class="text-gray-400 flex flex-col items-center">
                                    <i class="fas fa-image text-4xl mb-2"></i>
                                    <span>Tidak ada gambar</span>
                                </div>
                            </div>

                            <div v-if="service.galleries.length > 1" class="flex p-4 gap-2 overflow-x-auto bg-white border-t border-gray-100">
                                <button 
                                    v-for="gallery in service.galleries" 
                                    :key="gallery.id"
                                    @click="activeImage = '/storage/' + gallery.image"
                                    class="h-16 w-16 rounded-lg overflow-hidden border-2 transition-all flex-shrink-0"
                                    :class="activeImage === '/storage/' + gallery.image ? 'border-blue-600 opacity-100' : 'border-transparent opacity-60 hover:opacity-100'"
                                >
                                    <img :src="'/storage/' + gallery.image" class="w-full h-full object-cover">
                                </button>
                            </div>

                            <div class="p-6 md:p-8">

                                <div class="flex items-center gap-2 mb-2">
                                    <span
                                        class="bg-blue-100 text-blue-700 text-xs font-bold px-2.5 py-0.5 rounded uppercase tracking-wide">
                                        {{ service.category.name }}
                                    </span>
                                </div>

                                <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">{{ service.title }}</h1>
                                <div class="lg:hidden flex justify-between items-center">
                                    <div>
                                        <p class="text-xs text-gray-500 font-bold uppercase tracking-wider mb-1">
                                            Harga Mulai</p>
                                        <div class="text-2xl font-bold text-blue-600">
                                            {{ formatCurrency(service.price_min) }}
                                        </div>
                                    </div>
                                    <div class="text-right">
                                        <p class="text-[10px] text-gray-400">s/d</p>
                                        <p class="text-sm font-bold text-gray-500">{{
                                            formatCurrency(service.price_max) }}</p>
                                    </div>
                                </div>

                                <div class="flex items-center text-sm text-gray-600 gap-6 border-y border-gray-100 py-4 lg:mb-6">
                                    <div class="flex items-center">
                                        <i class="fas fa-star text-yellow-400 mr-1.5 text-lg"></i>
                                        <span class="font-bold text-gray-900 mr-1 text-lg">{{
                                            Number(service.rating_avg || 0).toFixed(1) }}</span>
                                        <span class="text-gray-500">({{ service.reviews.length }} Ulasan)</span>
                                    </div>
                                    <div class="h-4 w-px bg-gray-300"></div>
                                    <div class="flex items-center">
                                        <i class="fas fa-shopping-bag text-gray-400 mr-2"></i>
                                        <span class="font-bold text-gray-900 mr-1">{{ service.bookings_count }}x</span>
                                        <span>Dipesan</span>
                                    </div>
                                </div>

                                <div class="lg:hidden py-4 mb-2 border-b">

                                    <div v-if="service.user_id === auth_user_id" class="flex gap-3">

                                        <div class="flex-none w-14 bg-yellow-50 text-yellow-800 border border-yellow-600 rounded-lg flex items-center justify-center"
                                            title="Jasa milik Anda">
                                            <i class="fas fa-info-circle text-xl"></i>
                                        </div>

                                        <Link :href="route('services.edit', service)"
                                            class="flex-1 py-3 px-4 bg-yellow-50 border border-yellow-600 text-yellow-800 hover:bg-yellow-100 font-bold rounded-lg shadow-sm transition flex items-center justify-center">
                                            <i class="fas fa-edit mr-2"></i> Edit Jasa
                                        </Link>
                                    </div>

                                    <template v-else>
                                        <div class="flex gap-3">

                                            <Link
                                                :href="route('chats.index', { user_id: service.user_id, service_id: service.id })"
                                                class="flex-none w-14 bg-white border border-blue-600 text-blue-600 hover:bg-blue-50 font-bold rounded-lg transition flex items-center justify-center">
                                                <i class="fas fa-comment-dots text-xl"></i>
                                            </Link>

                                            <Link :href="route('bookings.create', { service_id: service.id })"
                                                class="flex-1 py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-sm transition flex items-center justify-center">
                                                <i class="fas fa-clipboard-list mr-2"></i> Booking Sekarang
                                            </Link>

                                        </div>
                                    </template>

                                </div>

                                <div class="prose prose-blue max-w-none text-gray-600 leading-relaxed">
                                    <h3 class="font-bold text-gray-900 text-lg mb-2">Deskripsi Jasa</h3>

                                    <div class="whitespace-pre-line relative"
                                        :class="{ 'line-clamp-6 max-h-[160px] overflow-hidden': !isDescExpanded }">
                                        {{ service.description }}

                                        <div v-if="!isDescExpanded && service.description.length > 100"
                                            class="absolute bottom-0 left-0 w-full h-12 bg-gradient-to-t from-white to-transparent">
                                        </div>
                                    </div>

                                    <button v-if="service.description.length > 100"
                                        @click="isDescExpanded = !isDescExpanded"
                                        class="mt-2 text-blue-600 font-bold text-sm hover:underline flex items-center gap-1 focus:outline-none">

                                        <span>{{ isDescExpanded ? 'Sembunyikan' : 'Baca Selengkapnya' }}</span>
                                        <i class="fas"
                                            :class="isDescExpanded ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                                    </button>
                                </div>

                            </div>
                        </div>

                            <div class="lg:hidden bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                <div class="p-4 border-b border-gray-100">
                                    <h3 class="font-bold text-gray-800 text-sm">Lokasi Jasa</h3>
                                </div>
                                
                                <div v-if="service.latitude && service.longitude" class="relative group">
                                    <div id="mini-map-mobile" class="h-48 w-full z-0"></div>
                                    
                                    <a :href="`https://www.google.com/maps/search/?api=1&query=${service.latitude},${service.longitude}`" 
                                    target="_blank"
                                    class="absolute inset-0 bg-black/0 hover:bg-black/5 transition z-10 flex items-center justify-center cursor-pointer group-hover:opacity-100">
                                        <span class="bg-white text-gray-800 text-xs font-bold px-3 py-1.5 rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity transform translate-y-2 group-hover:translate-y-0">
                                            Buka di Google Maps
                                        </span>
                                    </a>
                                </div>

                                <div v-else class="bg-gray-100 h-48 relative flex items-center justify-center">
                                    <div class="absolute inset-0 bg-[url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg')] bg-cover opacity-10"></div>
                                    <div class="z-10 text-center">
                                        <i class="fas fa-map-marker-alt text-3xl text-gray-400 mb-2"></i>
                                        <p class="text-xs font-bold text-gray-500 bg-white/80 px-2 py-1 rounded backdrop-blur-sm">
                                            {{ service.location || 'Lokasi Online' }}
                                        </p>
                                    </div>
                                </div>

                                <div class="p-3 bg-gray-50 text-xs text-gray-500 text-center border-t border-gray-100">
                                    <i class="fas fa-map-pin mr-1"></i> {{ service.location }}
                                </div>
                            </div>
                        
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h3 class="font-bold text-gray-900 text-lg mb-4">Tentang Penyedia Jasa</h3>
                            <div class="flex items-start md:items-center gap-4">
                                <Link :href="route('profile.show', service.user.hash_id)">
                                <img :src="service.user.avatar ? '/storage/' + service.user.avatar : 'https://ui-avatars.com/api/?name=' + service.user.name + '&background=random'" 
                                     class="h-16 w-16 rounded-full border border-gray-200 object-cover hover:ring-4 hover:ring-blue-100">
                                </Link>
                                <div class="flex-1">
                                    <Link :href="route('profile.show', service.user.hash_id)" class="font-bold text-gray-900 text-lg hover:text-gray-600 transition">{{ service.user.name }}</Link>
                                    <p class="text-sm text-gray-500 mb-2">Bergabung sejak {{ new Date(service.user.created_at).getFullYear() }}</p>
                                    <p class="text-gray-600 text-sm italic truncate lg:max-w-[500px] max-w-[250px]">
                                        "{{ service.user.bio || 'Penyedia jasa ini belum menambahkan bio.' }}"
                                    </p>
                                </div>
                                <Link :href="route('profile.show', service.user.hash_id)" class="hidden md:block px-4 py-2 border bg-white border-blue-600 rounded-lg text-sm font-semibold text-blue-600 hover:bg-blue-100 transition">
                                    <i class="fas fa-user mr-2"></i>Lihat Profil
                                </Link>
                            </div>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h3 class="font-bold text-gray-900 text-lg mb-6 flex items-center">
                                Ulasan Pengguna 
                                <span class="ml-2 bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">{{ service.reviews.length }}</span>
                            </h3>

                            <div v-if="service.reviews.length > 0" class="space-y-6">
                                <div v-for="review in service.reviews" :key="review.id" class="border-b border-gray-100 last:border-0 pb-6 last:pb-0">
                                    
                                    <div class="flex items-start justify-between mb-2">
            
                                        <div class="flex items-center gap-2">
                                            <Link :href="route('profile.show', review.user.hash_id)" class="flex items-center gap-2 group">
                                                <img :src="review.user.avatar ? '/storage/' + review.user.avatar : 'https://ui-avatars.com/api/?name=' + review.user.name + '&background=random'" 
                                                    class="h-8 w-8 rounded-full object-cover border border-gray-200 group-hover:opacity-80 transition"
                                                    alt="User Avatar">
                                                <span class="font-semibold text-sm text-gray-900 group-hover:text-gray-600 group-hover:underline transition">
                                                    {{ review.user.name }}
                                                </span>
                                            </Link>
                                            <span class="text-xs text-gray-400">&bull;</span>
                                            <span class="text-xs text-gray-500">{{ formatDate(review.created_at) }}</span>
                                        </div>

                                        <div v-if="$page.props.auth.user && review.user_id === $page.props.auth.user.id">
                                            <Link :href="route('bookings.show', review.booking_id)" 
                                                class="text-xs font-bold text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-3 py-1.5 rounded-lg transition flex items-center gap-1">
                                                <i class="fas fa-pencil-alt"></i> Edit Ulasan
                                            </Link>
                                        </div>

                                    </div>
                                    
                                    <div class="flex items-center mb-2">
                                        <i v-for="n in 5" :key="n" class="fas fa-star text-xs mr-0.5" :class="n <= review.rating ? 'text-yellow-400' : 'text-gray-200'"></i>
                                    </div>
                                    
                                    <p class="text-gray-600 text-sm leading-relaxed italic mb-3">
                                        "{{ review.review }}"
                                    </p>

                                    <div v-if="review.images && review.images.length > 0" class="flex flex-wrap gap-2 mt-2">
                                        <div v-for="(img, idx) in review.images" :key="idx" class="relative group cursor-pointer">
                                            <img :src="'/storage/' + img" 
                                                class="h-16 w-16 object-cover rounded-lg border border-gray-200 hover:scale-105 transition shadow-sm"
                                                @click="openLightbox('/storage/' + img)"
                                                title="Lihat foto penuh">
                                        </div>
                                    </div>

                                </div>
                            </div>

                            <div v-else class="text-center py-8 text-gray-500">
                                <i class="far fa-comment-dots text-3xl mb-2 opacity-30"></i>
                                <p>Belum ada ulasan untuk jasa ini.</p>
                            </div>
                        </div>

                    </div>
                    <div class="w-full lg:w-1/4">
                        <div class="hidden lg:block sticky top-24 space-y-4">
                            
                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                <div class="p-5 border-b border-gray-100 bg-gray-50">
                                    <p class="text-xs text-gray-500 font-bold uppercase tracking-wider mb-1">Harga Mulai</p>
                                    <div class="text-2xl font-bold text-blue-600">
                                        {{ formatCurrency(service.price_min) }}
                                    </div>
                                    <!-- <p class="text-xs text-gray-400 mt-1" v-if="service.price_max > service.price_min">
                                        s/d {{ formatCurrency(service.price_max) }}
                                    </p> -->
                                    <p class="text-xs text-gray-400 mt-1">
                                        s/d {{ formatCurrency(service.price_max) }}
                                    </p>
                                </div>

                                <div class="p-5 space-y-3">
                                    <div v-if="service.user_id === auth_user_id" class="space-y-3">
                                        <div class="text-center p-3 bg-yellow-50 text-yellow-800 rounded-lg text-sm border border-yellow-600 flex items-center justify-center">
                                            <i class="fas fa-info-circle mr-2"></i> 
                                            <span>Ini adalah jasa milik Anda.</span>
                                        </div>
                                        <Link :href="route('services.edit', service)" 
                                            class="w-full py-3 px-4 bg-yellow-50 border border-yellow-600 text-yellow-800 hover:bg-yellow-100 font-bold rounded-lg shadow-sm transition flex items-center justify-center">
                                            <i class="fas fa-edit mr-2"></i> Edit Jasa
                                        </Link>
                                    </div>

                                    <Link v-else :href="route('bookings.create', { service_id: service.id })" class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-sm transition flex items-center justify-center">
                                        <i class="fas fa-clipboard-list mr-2"></i> Booking Sekarang
                                    </Link>

                                    <Link v-if="service.user_id !== auth_user_id" 
                                          :href="route('chats.index', { user_id: service.user?.hash_id, service_id: service.id })"
                                          class="w-full py-3 px-4 bg-white border border-blue-600 text-blue-600 hover:bg-blue-50 font-bold rounded-lg transition flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                                            </svg> Chat Penyedia
                                    </Link>
                                </div>
                            </div>

                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                <div class="p-4 border-b border-gray-100">
                                    <h3 class="font-bold text-gray-800 text-sm">Lokasi Jasa</h3>
                                </div>
                                
                                <div v-if="service.latitude && service.longitude" class="relative group">
                                    <div id="mini-map-desktop" class="h-48 w-full z-0"></div>
                                    
                                    <a :href="`https://www.google.com/maps/search/?api=1&query=${service.latitude},${service.longitude}`" 
                                    target="_blank"
                                    class="absolute inset-0 bg-black/0 hover:bg-black/5 transition z-10 flex items-center justify-center cursor-pointer group-hover:opacity-100">
                                        <span class="bg-white text-gray-800 text-xs font-bold px-3 py-1.5 rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity transform translate-y-2 group-hover:translate-y-0">
                                            Buka di Google Maps
                                        </span>
                                    </a>
                                </div>

                                <div v-else class="bg-gray-100 h-48 relative flex items-center justify-center">
                                    <div class="absolute inset-0 bg-[url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg')] bg-cover opacity-10"></div>
                                    <div class="z-10 text-center">
                                        <i class="fas fa-map-marker-alt text-3xl text-gray-400 mb-2"></i>
                                        <p class="text-xs font-bold text-gray-500 bg-white/80 px-2 py-1 rounded backdrop-blur-sm">
                                            {{ service.location || 'Lokasi Online' }}
                                        </p>
                                    </div>
                                </div>

                                <div class="p-3 bg-gray-50 text-xs text-gray-500 text-center border-t border-gray-100">
                                    <i class="fas fa-map-pin mr-1"></i> {{ service.location }}
                                </div>
                            </div>

                            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                                <div class="flex items-center gap-3 mb-3">
                                    <i class="fas fa-shield-alt text-green-500 text-xl"></i>
                                    <div>
                                        <h4 class="font-bold text-gray-800 text-sm">Jaminan Aman</h4>
                                        <p class="text-xs text-gray-500">Pembayaran diteruskan setelah jasa selesai.</p>
                                    </div>
                                </div>
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
.animate-fade-in {
    animation: fadeIn 0.3s ease-out;
}
.animate-zoom-in {
    animation: zoomIn 0.3s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes zoomIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}
</style>