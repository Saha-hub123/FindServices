<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import MarketplaceCard from '@/Components/MarketplaceCard.vue';
import ServiceCard from '@/Components/ServiceCard.vue';
import { Head, Link } from '@inertiajs/vue3';
import { ref } from 'vue';

const props = defineProps({
    user: Object,        // User yang sedang dilihat
    services: Array,     // Jasa user tersebut
    reviews: Array,      // [BARU] Data Review
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
</script>

<template>
    <Head :title="`Profil ${user.name}`" />

    <AuthenticatedLayout>
        <div class="bg-gray-50 min-h-screen py-8">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8 mb-8">
                    <div class="flex flex-col md:flex-row items-center md:items-start gap-6 md:gap-10">
                        
                        <div class="shrink-0">
                            <div class="h-24 w-24 md:h-36 md:w-36 rounded-full p-1 border-2 border-gray-200 overflow-hidden">
                                <img 
                                    :src="user.avatar ? '/storage/' + user.avatar : 'https://ui-avatars.com/api/?name=' + user.name + '&background=random&size=150'" 
                                    alt="Profile Photo" 
                                    class="h-full w-full rounded-full object-cover"
                                >
                            </div>
                        </div>

                        <div class="flex-1 text-center md:text-left w-full">
                            
                            <div class="flex flex-col md:flex-row items-center gap-4 mb-4">
                                <h1 class="text-xl md:text-2xl font-light text-gray-800">{{ user.name }}</h1>
                                
                                <Link :href="route('chats.index', { user_id: user.id })"
                                      class="px-4 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold rounded-md text-sm border border-gray-300 transition flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-800" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                                    </svg> Chat Penjual
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
                                <p class="font-semibold">{{ user.email }} || {{ user.phone }}</p> 
                                <p class="whitespace-pre-line mt-1">{{ user.bio || 'Belum ada bio. Tulis sesuatu tentang keahlian Anda!' }}</p>
                                <p v-if="user.address" class="text-gray-500 mt-2 flex items-center justify-center md:justify-start">
                                    <i class="fas fa-map-marker-alt mr-1.5 text-red-500"></i> {{ user.address }}
                                </p>
                            </div>

                        </div>
                    </div>
                </div>

                <div class="border-t border-gray-300 mb-6 relative"> 
                    <div class="flex justify-center gap-8 md:gap-12 px-12"> 
                        <button 
                            @click="activeTab = 'services'"
                            class="py-4 flex items-center gap-2 text-xs md:text-sm font-bold tracking-widest transition-colors duration-200"
                            :class="activeTab === 'services' ? 'border-t-2 border-black text-gray-800' : 'border-t-2 border-transparent text-gray-400 hover:text-gray-600'"
                        >
                            <i class="fas fa-th"></i> ETALASE JASA
                        </button>
                        <button 
                            @click="activeTab = 'reviews'"
                            class="py-4 flex items-center gap-2 text-xs md:text-sm font-bold tracking-widest transition-colors duration-200"
                            :class="activeTab === 'reviews' ? 'border-t-2 border-black text-gray-800' : 'border-t-2 border-transparent text-gray-400 hover:text-gray-600'"
                        >
                            <i class="fas fa-star"></i> REVIEW
                        </button>
                    </div>

                    <div v-if="activeTab === 'services'" class="absolute right-0 top-1/2 -translate-y-1/2 pr-2 md:pr-4">
                        <div class="bg-white border border-gray-300 rounded-lg p-1 flex space-x-1">
                            <button @click="viewMode = 'grid'" class="p-1 rounded-md transition-all flex items-center justify-center" :class="viewMode === 'grid' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'" title="Tampilan Grid">
                                <i class="fas fa-th-large text-lg"></i>
                            </button>
                            <button @click="viewMode = 'list'" class="p-1 rounded-md transition-all flex items-center justify-center" :class="viewMode === 'list' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'" title="Tampilan List">
                                <i class="fas fa-list text-lg"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div v-if="activeTab === 'services'" class="animate-fade-in">
                    <div v-if="services.length > 0">
                        <div v-if="viewMode === 'grid'" class="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
                            <div v-for="service in services" :key="service.id" class="h-full">
                                <MarketplaceCard :service="service" />
                            </div>
                        </div>
                        <div v-else class="flex flex-col space-y-6 max-w-2xl mx-auto">
                            <div v-for="service in services" :key="'list-' + service.id">
                                <ServiceCard :service="service" />
                            </div>
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
                    
                    <div v-if="reviews.length > 0" class="space-y-4">
                        <div v-for="review in reviews" :key="review.id" class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition">
                            <div class="flex justify-between items-start mb-3">
                                <Link :href="route('profile.show', review.user.id)" class="flex items-center gap-3 group">
                                    <img :src="review.user.avatar ? '/storage/' + review.user.avatar : 'https://ui-avatars.com/api/?name=' + review.user.name" class="h-10 w-10 rounded-full object-cover border border-gray-100 group-hover:opacity-80 transition">
                                    <div>
                                        <p class="text-sm font-bold text-gray-800 group-hover:text-blue-600 group-hover:underline transition">{{ review.user.name }}</p>
                                        <p class="text-[10px] text-gray-400">{{ formatDate(review.created_at) }}</p>
                                    </div>
                                </Link>
                                
                                <div class="flex text-yellow-400 text-xs">
                                    <i v-for="n in 5" :key="n" class="fas fa-star" :class="n <= review.rating ? 'text-yellow-400' : 'text-gray-200'"></i>
                                </div>
                            </div>

                            <p class="text-gray-700 text-sm leading-relaxed mb-4 pl-1">
                                "{{ review.review }}"
                            </p>

                            <div class="bg-gray-50 p-2.5 rounded-lg flex items-center gap-3 border border-gray-100">
                                <img v-if="review.service.galleries && review.service.galleries[0]" :src="'/storage/' + review.service.galleries[0].image" class="h-8 w-8 rounded object-cover">
                                <Link :href="route('service.show', review.service.slug)" class="text-xs font-bold text-gray-600 hover:text-blue-600 truncate hover:underline flex-1">
                                    <span class="font-normal text-gray-400 mr-1">Jasa:</span> {{ review.service.title }}
                                </Link>
                            </div>
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
    </AuthenticatedLayout>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>