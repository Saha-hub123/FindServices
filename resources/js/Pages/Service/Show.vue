<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link } from '@inertiajs/vue3';
import { onMounted, ref } from 'vue';

const props = defineProps({
    service: Object,
    auth_user_id: Number
});

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

onMounted(() => {
    // Cek apakah service punya koordinat valid
    if (props.service.latitude && props.service.longitude) {
        
        const lat = parseFloat(props.service.latitude);
        const lng = parseFloat(props.service.longitude);

        // Inisialisasi Map (Mode Ringan/Lite)
        const map = L.map('mini-map', {
            center: [lat, lng],
            zoom: 13,
            zoomControl: false,      // Hilangkan tombol +/-
            dragging: false,         // Matikan geser
            scrollWheelZoom: false,  // Matikan scroll mouse
            doubleClickZoom: false,  // Matikan double click
            boxZoom: false,
            keyboard: false,
            attributionControl: false // Hilangkan teks copyright (opsional, biar bersih)
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OSM'
        }).addTo(map);

        // Custom Icon Kecil
        const icon = L.icon({
            iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
            shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
            iconSize: [20, 32], // Ukuran agak kecil biar pas di sidebar
            iconAnchor: [10, 32],
            popupAnchor: [1, -34],
        });

        L.marker([lat, lng], { icon: icon }).addTo(map);
    }
});

</script>

<template>
    <Head :title="service.title" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="flex flex-col lg:flex-row gap-6">
                    
                    <div class="w-full lg:w-3/4 space-y-6">
                        <div>
                           <Link :href="route('marketplace.index')" class="text-sm text-gray-500 hover:text-blue-600">&larr; Kembali ke Marketplace</Link>
                            <h1 class="text-2xl font-bold text-gray-900">Detail Jasa</h1>
                        </div>
                        
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            
                            <div class="aspect-w-16 aspect-h-9 bg-gray-200 relative h-[400px] flex items-center justify-center overflow-hidden">
                                <img v-if="activeImage" :src="activeImage" class="w-full h-full object-cover transition-all duration-300">
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
                                    <span class="bg-blue-100 text-blue-700 text-xs font-bold px-2.5 py-0.5 rounded uppercase tracking-wide">
                                        {{ service.category.name }}
                                    </span>
                                </div>

                                <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">{{ service.title }}</h1>

                                <div class="flex items-center text-sm text-gray-600 gap-6 border-y border-gray-100 py-4">
                                    <div class="flex items-center">
                                        <i class="fas fa-star text-yellow-400 mr-1.5 text-lg"></i>
                                        <span class="font-bold text-gray-900 mr-1 text-lg">{{ service.rating_avg.toFixed(1) }}</span>
                                        <span class="text-gray-500">({{ service.reviews.length }} Ulasan)</span>
                                    </div>
                                    <div class="h-4 w-px bg-gray-300"></div>
                                    <div class="flex items-center">
                                        <i class="fas fa-shopping-bag text-gray-400 mr-2"></i>
                                        <span class="font-bold text-gray-900 mr-1">{{ service.bookings_count }}x</span>
                                        <span>Dipesan</span>
                                    </div>
                                </div>

                                <div class="mt-6 prose prose-blue max-w-none text-gray-600 leading-relaxed">
                                    <h3 class="font-bold text-gray-900 text-lg mb-2">Deskripsi Jasa</h3>
                                    <p class="whitespace-pre-line">{{ service.description }}</p>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h3 class="font-bold text-gray-900 text-lg mb-4">Tentang Penyedia Jasa</h3>
                            <div class="flex items-start md:items-center gap-4">
                                <Link :href="route('profile.show', service.user.id)">
                                <img :src="service.user.avatar ? '/storage/' + service.user.avatar : 'https://ui-avatars.com/api/?name=' + service.user.name + '&background=random'" 
                                     class="h-16 w-16 rounded-full border border-gray-200 object-cover hover:ring-4 hover:ring-blue-100">
                                </Link>
                                <div class="flex-1">
                                    <Link :href="route('profile.show', service.user.id)" class="font-bold text-gray-900 text-lg hover:text-gray-600 transition">{{ service.user.name }}</Link>
                                    <p class="text-sm text-gray-500 mb-2">Bergabung sejak {{ new Date(service.user.created_at).getFullYear() }}</p>
                                    <p class="text-gray-600 text-sm italic">
                                        "{{ service.user.bio || 'Penyedia jasa ini belum menambahkan bio.' }}"
                                    </p>
                                </div>
                                <Link :href="route('profile.show', service.user.id)" class="hidden md:block px-4 py-2 border bg-white border-blue-600 rounded-lg text-sm font-semibold text-blue-600 hover:bg-blue-100 transition">
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
                                    <div class="flex items-center justify-between mb-2">
    
                                        <Link :href="route('profile.show', review.user.id)" class="flex items-center gap-2 group">
                                            
                                            <img :src="review.user.avatar ? '/storage/' + review.user.avatar : 'https://ui-avatars.com/api/?name=' + review.user.name + '&background=random'" 
                                                class="h-8 w-8 rounded-full object-cover border border-gray-200 group-hover:opacity-80 transition group-hover:ring-2 group-hover:ring-blue-100"
                                                alt="User Avatar">
                                            
                                            <span class="font-semibold text-sm text-gray-900 group-hover:text-gray-600 group-hover:underline transition">
                                                {{ review.user.name }}
                                            </span>
                                        </Link>

                                        <span class="text-xs text-gray-500">{{ formatDate(review.created_at) }}</span>
                                    </div>
                                    
                                    <div class="flex items-center mb-2">
                                        <i v-for="n in 5" :key="n" class="fas fa-star text-xs mr-0.5" :class="n <= review.rating ? 'text-yellow-400' : 'text-gray-200'"></i>
                                    </div>
                                    
                                    <p class="text-gray-600 text-sm leading-relaxed">
                                        {{ review.review }}
                                    </p>
                                </div>
                            </div>

                            <div v-else class="text-center py-8 text-gray-500">
                                <i class="far fa-comment-dots text-3xl mb-2 opacity-30"></i>
                                <p>Belum ada ulasan untuk jasa ini.</p>
                            </div>
                        </div>

                    </div>
                    <div class="w-full lg:w-1/4">
                        <div class="sticky top-24 space-y-4">
                            
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
                                        <div class="text-center p-3 bg-yellow-50 text-yellow-800 rounded-lg text-sm border border-yellow-200 flex items-center justify-center">
                                            <i class="fas fa-info-circle mr-2"></i> 
                                            <span>Ini adalah jasa milik Anda.</span>
                                        </div>
                                        <Link :href="route('services.edit', service.id)" 
                                            class="w-full py-3 px-4 bg-white border border-blue-600 text-blue-600 hover:bg-blue-50 font-bold rounded-lg shadow-sm transition flex items-center justify-center">
                                            <i class="fas fa-edit mr-2"></i> Edit Jasa
                                        </Link>
                                    </div>

                                    <Link v-else :href="route('bookings.create', { service_id: service.id })" class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-sm transition flex items-center justify-center">
                                        <i class="fas fa-clipboard-list mr-2"></i> Booking Sekarang
                                    </Link>

                                    <Link v-if="service.user_id !== auth_user_id" 
                                          :href="route('chats.index', { user_id: service.user_id, service_id: service.id })"
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
                                    <div id="mini-map" class="h-48 w-full z-0"></div>
                                    
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
    </AuthenticatedLayout>
</template>