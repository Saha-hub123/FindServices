<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import MarketplaceCard from '@/Components/MarketplaceCard.vue';
import { Head, Link } from '@inertiajs/vue3';
import { ref } from 'vue';

const props = defineProps({
    services: Array,
    users: Array,
    query: String
});

// LOGIKA OTOMATIS PINDAH TAB:
// Jika jasa KOSONG, tapi user ADA -> Otomatis ke tab 'users'
// Selain itu (jasa ada, atau dua-duanya kosong) -> Tetap default ke 'services'
const activeTab = ref(
    props.services.length === 0 && props.users.length > 0 
    ? 'users' 
    : 'services'
);
</script>

<template>
    <Head :title="`Pencarian: ${query}`" />

    <AuthenticatedLayout>
        <div class="py-8 bg-gray-50 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="mb-6">
                    <h1 class="text-2xl font-bold text-gray-800">
                        Hasil pencarian untuk "<span class="text-blue-600">{{ query }}</span>"
                    </h1>
                    <p class="text-gray-500 text-sm mt-1">
                        Ditemukan {{ services.length }} jasa dan {{ users.length }} pengguna.
                    </p>
                </div>

                <div class="flex border-b border-gray-300 mb-6">
                    <button @click="activeTab = 'services'" 
                            class="px-6 py-3 font-bold text-sm transition border-b-2"
                            :class="activeTab === 'services' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
                        Jasa ({{ services.length }})
                    </button>
                    <button @click="activeTab = 'users'" 
                            class="px-6 py-3 font-bold text-sm transition border-b-2"
                            :class="activeTab === 'users' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
                        Orang ({{ users.length }})
                    </button>
                </div>

                <div v-if="activeTab === 'services'" class="animate-fade-in">
                    <div v-if="services.length > 0" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        <MarketplaceCard v-for="service in services" :key="service.id" :service="service" />
                    </div>
                    <div v-else class="text-center py-12 bg-white rounded-xl shadow-sm">
                        <i class="fas fa-search text-4xl text-gray-300 mb-3"></i>
                        <p class="text-gray-500">Tidak ada jasa yang cocok dengan pencarian Anda.</p>
                    </div>
                </div>

                <div v-if="activeTab === 'users'" class="animate-fade-in space-y-3">
                    <div v-if="users.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div v-for="user in users" :key="user.id" class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 flex items-center gap-4">
                            <img :src="user.avatar ? '/storage/' + user.avatar : 'https://ui-avatars.com/api/?name=' + user.name + '&background=random'" 
                                 class="h-14 w-14 rounded-full object-cover border border-gray-100">
                            
                            <div class="flex-1 min-w-0">
                                <h3 class="font-bold text-gray-800 truncate">{{ user.name }}</h3>
                                <p class="text-xs text-gray-500 mb-2 truncate">{{ user.email }}</p>
                                <div class="flex items-center gap-2">
                                    <span class="bg-blue-50 text-blue-700 text-[10px] px-2 py-0.5 rounded font-bold">
                                        {{ user.services_count }} Jasa Aktif
                                    </span>
                                </div>
                            </div>
                            
                            <Link :href="route('profile.show', user.id)" class="bg-gray-100 hover:bg-blue-50 text-gray-600 px-3 py-1.5 rounded-lg text-xs font-bold hover:text-blue-600 hover:border-blue-200 transition whitespace-nowrap">
                                Lihat
                            </Link>
                        </div>
                    </div>
                    <div v-else class="text-center py-12 bg-white rounded-xl shadow-sm">
                        <i class="fas fa-user-slash text-4xl text-gray-300 mb-3"></i>
                        <p class="text-gray-500">Tidak ada pengguna dengan nama tersebut.</p>
                    </div>
                </div>

            </div>
        </div>
    </AuthenticatedLayout>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>