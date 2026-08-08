<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import MarketplaceCard from '@/Components/MarketplaceCard.vue';
import ServiceCard from '@/Components/ServiceCard.vue';
import { Head, Link } from '@inertiajs/vue3';
import { ref, watch } from 'vue'; // Tambah Watch
import axios from 'axios'; // Tambah Axios

const props = defineProps({
    user: Object,        // User yang sedang dilihat
    services: Object,     // Jasa user tersebut
    reviews: Object,      // [BARU] Data Review
    stats: Object,       // Statistik
    auth_id: Number      // ID Kita (Login)
});

// State untuk Tab & View Mode
const activeTab = ref('services'); // Default: 'services' atau 'reviews'
const viewMode = ref('grid');

// Helper Format Tanggal
const formatDate = (date) => {
    return new Date(date).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' });
};

// --- 1. LOAD MORE SERVICES ---
const allServices = ref([...props.services.data]);
const nextServicesUrl = ref(props.services.next_page_url);
const isLoadingServices = ref(false);

const loadMoreServices = async () => {
    if (!nextServicesUrl.value || isLoadingServices.value) return;
    isLoadingServices.value = true;
    try {
        const res = await axios.get(nextServicesUrl.value);
        const newData = res.data.services.data; // Ambil key 'services' dari JSON controller
        allServices.value = [...allServices.value, ...newData];
        nextServicesUrl.value = res.data.services.next_page_url;
    } catch (e) { console.error(e); } 
    finally { isLoadingServices.value = false; }
};

// --- 2. LOAD MORE REVIEWS ---
const allReviews = ref([...props.reviews.data]);
const nextReviewsUrl = ref(props.reviews.next_page_url);
const isLoadingReviews = ref(false);

const loadMoreReviews = async () => {
    if (!nextReviewsUrl.value || isLoadingReviews.value) return;
    isLoadingReviews.value = true;
    try {
        const res = await axios.get(nextReviewsUrl.value);
        const newData = res.data.reviews.data; // Ambil key 'reviews' dari JSON controller
        allReviews.value = [...allReviews.value, ...newData];
        nextReviewsUrl.value = res.data.reviews.next_page_url;
    } catch (e) { console.error(e); } 
    finally { isLoadingReviews.value = false; }
};

// --- WATCHER (Agar data sinkron jika user di-refresh via Inertia) ---
watch(() => props.services, (newVal) => {
    allServices.value = [...newVal.data];
    nextServicesUrl.value = newVal.next_page_url;
});
watch(() => props.reviews, (newVal) => {
    allReviews.value = [...newVal.data];
    nextReviewsUrl.value = newVal.next_page_url;
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
    <Head :title="`Profil ${user.name}`" />

    <AuthenticatedLayout>
        <div class="bg-gray-50 min-h-screen py-8">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 lg:mb-0 mb-12">
                
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8 mb-8">
                    <div class="flex flex-col md:flex-row items-center md:items-start gap-6 md:gap-10">
                        
                        <div class="shrink-0 relative group cursor-zoom-in" 
                            @click="openLightbox(user.avatar ? '/storage/' + user.avatar : 'https://ui-avatars.com/api/?name=' + user.name + '&background=random&size=150')">
                            
                            <div class="h-24 w-24 md:h-36 md:w-36 rounded-full overflow-hidden relative transition-all duration-300 ease-out
                                        ring-2 ring-gray-200 ring-offset-2 
                                        group-hover:ring-4 group-hover:ring-blue-100 group-hover:ring-offset-4 
                                        shadow-sm group-hover:shadow-xl">
                                
                                <img 
                                    :src="user.avatar ? '/storage/' + user.avatar : 'https://ui-avatars.com/api/?name=' + user.name + '&background=random&size=150'" 
                                    alt="Profile Photo" 
                                    class="h-full w-full rounded-full object-cover transition-transform duration-500 group-hover:scale-110"
                                >
                                
                                <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                    <i class="fas fa-search-plus text-white text-xl drop-shadow-md transform scale-75 group-hover:scale-100 transition-transform duration-300"></i>
                                </div>
                            </div>
                        </div>

                        <div class="flex-1 text-center md:text-left w-full">
                            
                            <div class="flex items-center justify-center md:justify-start gap-3 mb-4">
                                <h1
                                    class="text-2xl lg:text-3xl font-light text-gray-800 truncate max-w-[200px] md:max-w-none">
                                    {{ user.name }}
                                </h1>

                                <Link :href="route('chats.index', { user_id: user.hash_id })" class="flex items-center justify-center bg-gray-100 hover:bg-gray-200 text-gray-800 border border-gray-300 rounded-md transition duration-200 p-1">

                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-800 transition-all"
                                        :class="'mr-2'" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd"
                                            d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z"
                                            clip-rule="evenodd" />
                                    </svg>
                                    <span class="font-semibold lg:text-sm text-xs mr-1"> Chat</span>
                                    <span class="hidden md:inline font-semibold text-sm"> Penjual</span>
                                </Link>
                            </div>

                            <div class="flex justify-center md:justify-start gap-8 mb-4 border-t border-b md:border-0 py-3 md:py-0 border-gray-100">
                                <div class="text-center md:text-left">
                                    <span class="font-bold text-gray-900 block md:inline text-lg md:text-base">{{ stats.services_count }}</span>
                                    <span class="text-gray-600 ml-1">Jasa Aktif</span>
                                </div>
                                <div class="text-center md:text-left">
                                    <span class="font-bold text-gray-900 block md:inline text-lg md:text-base">{{ stats.orders_completed }}</span>
                                    <span class="text-gray-600 ml-1">Pesanan Selesai</span>
                                </div>
                                <div class="text-center md:text-left">
                                    <span class="font-bold text-gray-900 block md:inline text-lg md:text-base">{{ parseFloat(stats.rating_avg).toFixed(1) }}</span>
                                    <span class="text-gray-600 ml-1">Rating</span>
                                    <span class="text-xs text-gray-400 block md:inline">({{ stats.total_reviews }} ulasan)</span>
                                </div>
                            </div>

                            <div class="text-sm text-gray-700 leading-relaxed max-w-lg mx-auto md:mx-0"> 
                                <p class="whitespace-pre-line mt-1">{{ user.bio || 'Belum ada bio. Tulis sesuatu tentang keahlian Anda!' }}</p>
                                <p v-if="user.address" class="text-gray-500 mt-2 flex items-center justify-center md:justify-start">
                                    <i class="fas fa-map-marker-alt mr-1.5 text-red-500"></i> {{ user.address }}
                                </p>
                            </div>

                        </div>
                    </div>
                </div>

                <div class="border-t border-gray-300 mb-6 relative">
                    <div class="flex justify-center gap-6 md:gap-12 px-4 md:px-12">
                        <button @click="activeTab = 'services'"
                            class="py-4 flex items-center gap-2 text-xs md:text-sm font-bold tracking-widest transition-colors duration-200"
                            :class="activeTab === 'services' ? 'border-t-2 border-black text-gray-800' : 'border-t-2 border-transparent text-gray-400 hover:text-gray-600'">
                            <i class="fas fa-th"></i> ETALASE JASA
                        </button>
                        <button @click="activeTab = 'reviews'"
                            class="py-4 flex items-center gap-2 text-xs md:text-sm font-bold tracking-widest transition-colors duration-200"
                            :class="activeTab === 'reviews' ? 'border-t-2 border-black text-gray-800' : 'border-t-2 border-transparent text-gray-400 hover:text-gray-600'">
                            <i class="fas fa-star"></i> REVIEW
                        </button>
                    </div>

                    <div v-if="activeTab === 'services'" class="absolute right-0 top-1/2 -translate-y-1/2 pr-3 md:pr-4">
                        <div class="bg-white border border-gray-300 rounded-lg p-0.5 md:p-1 flex space-x-1 shadow-sm">

                            <button @click="viewMode = 'grid'"
                                class="rounded-md transition-all flex items-center justify-center p-1 md:p-1"
                                :class="viewMode === 'grid' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'"
                                title="Tampilan Grid">
                                <i class="fas fa-th-large text-xs md:text-lg"></i>
                            </button>

                            <button @click="viewMode = 'list'"
                                class="rounded-md transition-all flex items-center justify-center p-1 md:p-1"
                                :class="viewMode === 'list' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'"
                                title="Tampilan List">
                                <i class="fas fa-list text-xs md:text-lg"></i>
                            </button>

                        </div>
                    </div>
                </div>

                <div v-if="activeTab === 'services'" class="animate-fade-in">
                    <div v-if="allServices.length > 0">
                        
                        <div v-if="viewMode === 'grid'" class="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
                            <div v-for="service in allServices" :key="service.id" class="h-full">
                                <MarketplaceCard :service="service" />
                            </div>
                        </div>
                        <div v-else class="flex flex-col space-y-6 max-w-2xl mx-auto">
                            <div v-for="service in allServices" :key="'list-' + service.id">
                                <ServiceCard :service="service" />
                            </div>
                        </div>

                        <div v-if="nextServicesUrl" class="mt-8 flex justify-center">
                            <button 
                                @click="loadMoreServices" 
                                :disabled="isLoadingServices"
                                class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-full font-bold shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-70 transition-all flex items-center gap-2 text-sm"
                            >
                                <span v-if="isLoadingServices"><i class="fas fa-spinner fa-spin"></i> Memuat...</span>
                                <span v-else>Muat Jasa Lainnya <i class="fas fa-chevron-down ml-1"></i></span>
                            </button>
                        </div>
                    </div>

                    <div v-else class="flex flex-col items-center justify-center py-16 bg-white rounded-lg border border-dashed border-gray-300">
                        <div class="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                            <i class="fas fa-box-open text-2xl text-gray-400"></i>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900">Belum ada Jasa</h3>
                        <p class="text-gray-500 text-sm">Pengguna ini belum menawarkan jasa apapun.</p>
                    </div>
                </div>

                <div v-if="activeTab === 'reviews'" class="space-y-4 animate-fade-in">
    
                    <div v-if="allReviews.length > 0" class="space-y-4">
                        <div v-for="review in allReviews" :key="review.id" class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition group/card">
                            
                            <div class="flex justify-between items-start mb-3">
                                <Link :href="route('profile.show', review.user.hash_id)" class="flex items-center gap-3 group">
                                    <img :src="review.user.avatar ? '/storage/' + review.user.avatar : 'https://ui-avatars.com/api/?name=' + review.user.name" 
                                        class="h-10 w-10 rounded-full object-cover border border-gray-100 group-hover:opacity-80 transition">
                                    <div>
                                        <p class="text-sm font-bold text-gray-800 group-hover:text-blue-600 group-hover:underline transition">{{ review.user.name }}</p>
                                        <p class="text-[10px] text-gray-400">{{ formatDate(review.created_at) }}</p>
                                    </div>
                                </Link>
                            </div>
                            
                            <div class="flex text-yellow-400 text-xs mb-2">
                                <i v-for="n in 5" :key="n" class="fas fa-star" :class="n <= review.rating ? 'text-yellow-400' : 'text-gray-200'"></i>
                            </div>
                            
                            <p class="text-gray-700 text-sm leading-relaxed mb-3 pl-1 italic">
                                "{{ review.review }}"
                            </p>

                            <div v-if="review.images && review.images.length > 0" class="flex flex-wrap gap-2 mb-3 pl-1">
                                <div v-for="(img, idx) in review.images" :key="idx" class="relative group cursor-pointer">
                                    <img :src="'/storage/' + img" 
                                        class="h-16 w-16 object-cover rounded-lg border border-gray-200 hover:scale-105 transition shadow-sm"
                                        @click="openLightbox('/storage/' + img)"
                                        title="Lihat foto penuh">
                                </div>
                            </div>

                            <div class="bg-gray-50 p-2.5 rounded-lg flex items-center gap-3 border border-gray-100">
                                <img v-if="review.service.galleries && review.service.galleries[0]" :src="'/storage/' + review.service.galleries[0].image" class="h-8 w-8 rounded object-cover">
                                <Link :href="route('service.show', review.service.slug)" class="text-xs font-bold text-gray-600 hover:text-blue-600 truncate hover:underline flex-1">
                                    <span class="font-normal text-gray-400 mr-1">Jasa:</span> {{ review.service.title }}
                                </Link>
                            </div>
                        </div>

                        <div v-if="nextReviewsUrl" class="mt-8 flex justify-center">
                            <button 
                                @click="loadMoreReviews" 
                                :disabled="isLoadingReviews"
                                class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-full font-bold shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-70 transition-all flex items-center gap-2 text-sm"
                            >
                                <span v-if="isLoadingReviews"><i class="fas fa-spinner fa-spin"></i> Memuat...</span>
                                <span v-else>Muat Ulasan Lainnya <i class="fas fa-chevron-down ml-1"></i></span>
                            </button>
                        </div>
                    </div>

                    <div v-else class="flex flex-col items-center justify-center py-16 bg-white rounded-lg border border-dashed border-gray-300">
                        <div class="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                            <i class="fas fa-comment-slash text-2xl text-gray-400"></i>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900">Belum ada Ulasan</h3>
                        <p class="text-gray-500 text-sm">Pengguna ini belum menerima ulasan dari pembeli.</p>
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
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>