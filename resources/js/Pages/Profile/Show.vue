<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import MarketplaceCard from '@/Components/MarketplaceCard.vue';
import ServiceCard from '@/Components/ServiceCard.vue';
import { Head, Link } from '@inertiajs/vue3';
import { ref } from 'vue';

const props = defineProps({
    user: Object,        // User yang sedang dilihat
    services: Array,     // Jasa user tersebut
    stats: Object,       // Statistik
    auth_id: Number      // ID Kita (Login)
});

const viewMode = ref('grid');
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
                                <h1 class="text-2xl md:text-3xl font-light text-gray-800">{{ user.name }}</h1>
                                
                                <Link :href="route('chats.index', { user_id: user.id })" 
                                      class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-full text-sm shadow-sm transition flex items-center">
                                    <i class="fab fa-facebook-messenger mr-2"></i> Chat Penjual
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
                                </div>
                            </div>

                            <div class="text-sm text-gray-700 leading-relaxed max-w-lg mx-auto md:mx-0">
                                <p class="whitespace-pre-line">{{ user.bio || 'Pengguna ini belum menulis bio.' }}</p>
                                <p v-if="user.address" class="text-gray-500 mt-2 flex items-center justify-center md:justify-start">
                                    <i class="fas fa-map-marker-alt mr-1.5 text-red-500"></i> {{ user.address }}
                                </p>
                            </div>

                        </div>
                    </div>
                </div>

                <div class="border-t border-gray-300 mb-6 flex justify-between items-center px-2 pt-4">
                    <h3 class="text-lg font-bold text-gray-800 tracking-wide">
                        <i class="fas fa-th mr-2"></i> ETALASE JASA
                    </h3>

                    <div class="bg-white border border-gray-300 rounded-lg p-1 flex space-x-1">
                        <button @click="viewMode = 'grid'" class="p-2 rounded-md transition-all flex items-center justify-center" :class="viewMode === 'grid' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'">
                            <i class="fas fa-th-large"></i>
                        </button>
                        <button @click="viewMode = 'list'" class="p-2 rounded-md transition-all flex items-center justify-center" :class="viewMode === 'list' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'">
                            <i class="fas fa-list"></i>
                        </button>
                    </div>
                </div>

                <div v-if="services.length > 0">
                    
                    <div v-if="viewMode === 'grid'" class="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-4 animate-fade-in">
                        <div v-for="service in services" :key="service.id" class="h-full">
                            <MarketplaceCard :service="service" />
                            </div>
                    </div>

                    <div v-else class="flex flex-col space-y-6 max-w-2xl mx-auto animate-fade-in">
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
        </div>
    </AuthenticatedLayout>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>