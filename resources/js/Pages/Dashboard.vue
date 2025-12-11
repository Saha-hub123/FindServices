<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import ServiceCard from '@/Components/ServiceCard.vue';
import { Head, Link, router, usePage } from '@inertiajs/vue3'; // Tambah usePage
import { ref, watch } from 'vue'; // Tambah watch

const props = defineProps({
    services: Object,
    categories: Array,      // Semua Kategori
    trendingCategories: Array, // [BARU] Kategori Pilihan (Top 5)
    popularServices: Array,    // [BARU] Jasa Paling Laris
    topProviders: Array,       // [BARU] User dengan rating tertinggi
    filters: Object, // Terima props filter dari controller
    is_guest: Boolean
});

// State Filter: Default ambil dari props (agar tombol tetap aktif saat reload)
const activeFilter = ref(props.filters.filter || 'latest');

// Fungsi Filter: Reload halaman dengan parameter baru
const applyQuickFilter = (filter) => {
    activeFilter.value = filter;
    router.get(route('dashboard'), { filter: filter }, { 
        preserveState: true, 
        preserveScroll: true, // Agar tidak scroll ke atas saat klik filter
        replace: true 
    });
};

const redirectToLogin = (event) => {
    event.preventDefault();
    event.stopPropagation();
    router.get(route('login'));
};

const formatCurrency = (val) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(val);
</script>

<template>
    <Head title="Beranda Marketplace" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen" 
             @click.capture="is_guest ? redirectToLogin($event) : null"
             :class="{ 'cursor-pointer': is_guest }"
             :title="is_guest ? 'Klik untuk Login' : ''">
            
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    
                    <div class="hidden lg:block lg:col-span-3">
                        <div class="sticky top-24 space-y-6">
                            
                            <div class="bg-white p-2 rounded-xl shadow-sm border border-gray-200">
                                <Link :href="route('dashboard')" class="flex items-center px-4 py-3 text-gray-700 font-bold bg-gray-50 rounded-lg mb-1">
                                    <i class="fas fa-home w-6 text-blue-600"></i> Beranda
                                </Link>
                                <Link :href="route('bookings.index')" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition">
                                    <i class="fas fa-clipboard-list w-6"></i> Pesanan Saya
                                </Link>
                                <Link :href="route('profile.index')" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition">
                                    <i class="fas fa-user w-6"></i> Profil
                                </Link>
                            </div>

                            <div>
                                <div class="flex justify-between items-center px-2 mb-3">
                                    <h3 class="font-bold text-gray-700">Kategori Ramai</h3>
                                    <Link :href="route('marketplace.index')" class="text-xs text-blue-600 hover:underline">Lihat Semua</Link>
                                </div>
                                <div class="bg-white p-3 rounded-xl shadow-sm border border-gray-200 space-y-2">
                                    <Link v-for="(cat, index) in (trendingCategories || categories.slice(0, 5))" :key="cat.id" 
                                          :href="route('marketplace.index', { category: cat.slug })"
                                          class="flex items-center p-2 rounded-lg hover:bg-gray-50 transition group cursor-pointer">
                                        <div class="w-8 h-8 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mr-3 group-hover:bg-blue-600 group-hover:text-white transition">
                                            <i :class="cat.icon_class || 'fas fa-hashtag'"></i>
                                        </div>
                                        <div class="flex-1">
                                            <p class="text-sm font-bold text-gray-700 group-hover:text-blue-700">{{ cat.name }}</p>
                                            <p class="text-[10px] text-gray-400">Sedang naik daun 🔥</p>
                                        </div>
                                    </Link>
                                </div>
                            </div>

                        </div>
                    </div>

                    <div class="lg:col-span-6">
                        
                        <div v-if="$page.props.auth.user" class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6 flex items-center gap-4">
                            <img :src="$page.props.auth.user.avatar ? '/storage/' + $page.props.auth.user.avatar : 'https://ui-avatars.com/api/?name=' + $page.props.auth.user.name" class="h-10 w-10 rounded-full object-cover border border-gray-100">
                            <Link :href="route('services.create')" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-500 py-2.5 px-4 rounded-full text-left cursor-pointer transition text-sm">
                                Apa keahlian baru Anda hari ini, {{ $page.props.auth.user.name }}?
                            </Link>
                        </div>

                        <div v-else class="bg-blue-600 p-4 rounded-lg shadow-sm mb-6 text-white text-center">
                            <h3 class="font-bold text-lg">Selamat Datang di FindServices!</h3>
                            <p class="text-blue-100 text-sm">Login untuk mulai menawarkan jasa atau membooking layanan.</p>
                        </div>

                        <div class="flex gap-2 mb-4 overflow-x-auto pb-2 custom-scrollbar">
                            <button @click="applyQuickFilter('latest')" 
                                    class="px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap transition border"
                                    :class="activeFilter === 'latest' ? 'bg-black text-white border-black' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'">
                                Terbaru
                            </button>
                            <button @click="applyQuickFilter('popular')" 
                                    class="px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap transition border"
                                    :class="activeFilter === 'popular' ? 'bg-black text-white border-black' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'">
                                Paling Laris
                            </button>
                            <button @click="applyQuickFilter('rating')" 
                                    class="px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap transition border"
                                    :class="activeFilter === 'rating' ? 'bg-black text-white border-black' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'">
                                Rating Tinggi ⭐
                            </button>
                        </div>

                        <div v-if="services.data.length > 0" class="space-y-6">
                            <ServiceCard v-for="service in services.data" :key="service.id" :service="service" />
                        </div>
                        <div v-else class="bg-white p-12 rounded-xl shadow-sm text-center border border-gray-200">
                            <div class="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400 text-2xl">
                                <i class="fas fa-search"></i>
                            </div>
                            <p class="text-gray-500 font-medium">Belum ada jasa yang tersedia.</p>
                        </div>
                    </div>

                    <div class="hidden lg:block lg:col-span-3">
                        <div class="sticky top-24 space-y-6">
                            
                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
                                <h3 class="font-bold text-gray-700 mb-4 flex items-center">
                                    <i class="fas fa-fire text-orange-500 mr-2"></i> Sedang Populer
                                </h3>
                                <div class="space-y-4">
                                    <Link v-for="pop in (popularServices || services.data.slice(0,3))" :key="'pop-'+pop.id" 
                                          :href="route('service.show', pop.slug)"
                                          class="flex gap-3 group cursor-pointer">
                                        <img v-if="pop.galleries?.[0]" :src="'/storage/' + pop.galleries[0].image" class="h-12 w-12 rounded-lg object-cover bg-gray-100">
                                        <div class="min-w-0">
                                            <p class="text-sm font-bold text-gray-800 line-clamp-1 group-hover:text-blue-600">{{ pop.title }}</p>
                                            <p class="text-xs text-gray-500">{{ formatCurrency(pop.price_min) }}</p>
                                        </div>
                                    </Link>
                                </div>
                            </div>

                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
                                <h3 class="font-bold text-gray-700 mb-4 flex items-center">
                                    <i class="fas fa-medal text-yellow-500 mr-2"></i> Penyedia Terbaik
                                </h3>
                                <div class="space-y-4">
                                    <div v-for="provider in topProviders" :key="provider.id" class="flex items-center justify-between">
                                        
                                        <Link :href="route('profile.show', provider.id)" class="flex items-center gap-2 group min-w-0">
                                            <img :src="provider.avatar ? '/storage/' + provider.avatar : 'https://ui-avatars.com/api/?name=' + provider.name + '&background=random'" 
                                                 class="h-9 w-9 rounded-full border border-gray-100 object-cover group-hover:opacity-80 transition">
                                            <div class="min-w-0">
                                                <p class="text-xs font-bold text-gray-800 truncate group-hover:text-blue-600 group-hover:underline transition">
                                                    {{ provider.name }}
                                                </p>
                                                <p class="text-[10px] text-gray-500 truncate">
                                                    Rekomendasi ⭐
                                                </p>
                                            </div>
                                        </Link>

                                        <Link :href="route('profile.show', provider.id)" 
                                              class="text-[10px] bg-gray-50 text-gray-600 border border-gray-200 px-3 py-1.5 rounded-full font-bold hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition whitespace-nowrap">
                                            Lihat
                                        </Link>
                                    </div>

                                    <div v-if="topProviders.length === 0" class="text-center text-xs text-gray-400 py-2">
                                        Belum ada penyedia.
                                    </div>
                                </div>
                            </div>

                            <div class="text-[10px] text-gray-400 px-2 leading-relaxed">
                                <a href="#" class="hover:underline">Tentang Kami</a> &bull; 
                                <a href="#" class="hover:underline">Bantuan</a> &bull; 
                                <a href="#" class="hover:underline">Privasi</a> &bull; 
                                <span>FindServices © 2025</span>
                            </div>

                        </div>
                    </div>

                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { height: 0px; background: transparent; }
</style>