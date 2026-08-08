<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import MarketplaceCard from '@/Components/MarketplaceCard.vue';
import { Head, Link } from '@inertiajs/vue3';
import { ref, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
    services: Object,
    users: Object,
    query: String
});

// LOGIKA OTOMATIS PINDAH TAB:
// Jika jasa KOSONG, tapi user ADA -> Otomatis ke tab 'users'
// Selain itu (jasa ada, atau dua-duanya kosong) -> Tetap default ke 'services'
// 2. PERBAIKAN LOGIKA AUTO-TAB
// Kita harus cek 'services.data.length' karena services adalah object pagination
const activeTab = ref(
    props.services.data.length === 0 && props.users.data.length > 0 
    ? 'users' 
    : 'services'
);

// --- LOGIC LOAD MORE: SERVICES ---
const allServices = ref([...props.services.data]);
const nextServicesUrl = ref(props.services.next_page_url);
const isLoadingServices = ref(false);

const loadMoreServices = async () => {
    if (!nextServicesUrl.value || isLoadingServices.value) return;
    isLoadingServices.value = true;
    try {
        const res = await axios.get(nextServicesUrl.value);
        // Perhatikan struktur response JSON dari controller
        const newData = res.data.services.data;
        allServices.value = [...allServices.value, ...newData];
        nextServicesUrl.value = res.data.services.next_page_url;
    } catch (e) { console.error(e); } 
    finally { isLoadingServices.value = false; }
};

// --- LOGIC LOAD MORE: USERS ---
const allUsers = ref([...props.users.data]);
const nextUsersUrl = ref(props.users.next_page_url);
const isLoadingUsers = ref(false);

const loadMoreUsers = async () => {
    if (!nextUsersUrl.value || isLoadingUsers.value) return;
    isLoadingUsers.value = true;
    try {
        const res = await axios.get(nextUsersUrl.value);
        // Ambil data users dari response
        const newData = res.data.users.data;
        allUsers.value = [...allUsers.value, ...newData];
        nextUsersUrl.value = res.data.users.next_page_url;
    } catch (e) { console.error(e); } 
    finally { isLoadingUsers.value = false; }
};

// --- WATCHER (RESET SAAT SEARCH BERUBAH) ---
watch(() => props.services, (newVal) => {
    allServices.value = [...newVal.data];
    nextServicesUrl.value = newVal.next_page_url;
});

watch(() => props.users, (newVal) => {
    allUsers.value = [...newVal.data];
    nextUsersUrl.value = newVal.next_page_url;
});
</script>

<template>
    <Head :title="`Pencarian: ${query}`" />

    <AuthenticatedLayout>
        <div class="py-8 bg-gray-50 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 lg:mb-0 mb-12">
                
                <div class="mb-6">
                    <h1 class="text-2xl font-bold text-gray-800">
                        Hasil pencarian untuk "<span class="text-blue-600">{{ query }}</span>"
                    </h1>
                    <p class="text-gray-500 text-sm mt-1">
                        Ditemukan {{ allServices.length }} jasa dan {{ allUsers.length }} pengguna.
                    </p>
                </div>

                <div class="flex border-b border-gray-300 mb-6">
                    <button @click="activeTab = 'services'" 
                            class="px-6 py-3 font-bold text-sm transition border-b-2"
                            :class="activeTab === 'services' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
                        Jasa ({{ allServices.length }})
                    </button>
                    <button @click="activeTab = 'users'" 
                            class="px-6 py-3 font-bold text-sm transition border-b-2"
                            :class="activeTab === 'users' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
                        Orang ({{ allUsers.length }})
                    </button>
                </div>

                <div v-if="activeTab === 'services'" class="animate-fade-in">
                    <div v-if="allServices.length > 0">
                        
                        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            <MarketplaceCard v-for="service in allServices" :key="service.id" :service="service" />
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

                    <div v-else class="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
                        <i class="fas fa-search text-4xl text-gray-300 mb-3"></i>
                        <p class="text-gray-500">Tidak ada jasa yang cocok dengan pencarian Anda.</p>
                    </div>
                </div>

                <div v-if="activeTab === 'users'" class="animate-fade-in space-y-3">
                    <div v-if="allUsers.length > 0">
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div v-for="user in allUsers" :key="user.id" class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 flex items-center gap-4 transition hover:shadow-md">
                                <img :src="user.avatar ? '/storage/' + user.avatar : 'https://ui-avatars.com/api/?name=' + user.name + '&background=random'" 
                                    class="h-14 w-14 rounded-full object-cover border border-gray-100">
                                
                                <div class="flex-1 min-w-0">
                                    <h3 class="font-bold text-gray-800 truncate">{{ user.name }}</h3>
                                    <p class="text-xs text-gray-500 mb-2 truncate">{{ user.email }}</p>
                                    <div class="flex items-center gap-2">
                                        <span class="bg-blue-50 text-blue-700 text-[10px] px-2 py-0.5 rounded font-bold border border-blue-100">
                                            {{ user.services_count || 0 }} Jasa Aktif
                                        </span>
                                    </div>
                                </div>
                                
                                <Link :href="route('profile.show', user.hash_id)" class="bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-200 text-gray-600 px-3 py-1.5 rounded-lg text-xs font-bold hover:text-blue-600 transition whitespace-nowrap">
                                    Lihat
                                </Link>
                            </div>
                        </div>

                        <div v-if="nextUsersUrl" class="mt-8 flex justify-center">
                            <button 
                                @click="loadMoreUsers" 
                                :disabled="isLoadingUsers"
                                class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-full font-bold shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-70 transition-all flex items-center gap-2 text-sm"
                            >
                                <span v-if="isLoadingUsers"><i class="fas fa-spinner fa-spin"></i> Memuat...</span>
                                <span v-else>Muat User Lainnya <i class="fas fa-chevron-down ml-1"></i></span>
                            </button>
                        </div>

                    </div>

                    <div v-else class="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
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