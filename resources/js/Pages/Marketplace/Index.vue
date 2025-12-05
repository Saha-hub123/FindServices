<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import MarketplaceCard from '@/Components/MarketplaceCard.vue';
import { Head, useForm } from '@inertiajs/vue3';

const props = defineProps({
    services: Object,
    categories: Array,
    filters: Object
});

const searchForm = useForm({
    search: props.filters.search || '',
    category: props.filters.category || ''
});

const submitSearch = () => {
    searchForm.get(route('marketplace.index'), { preserveState: true });
};
</script>

<template>
    <Head title="Marketplace Jasa" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="flex flex-col md:flex-row gap-6">
                    
                    <div class="w-full md:w-1/4">
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden sticky top-24">
                            <div class="p-4 border-b border-gray-100 flex justify-between items-center">
                                <h2 class="font-bold text-lg text-gray-800">Filter Pencarian</h2>
                                <button @click="searchForm.reset(); submitSearch()" class="text-xs text-blue-600 hover:underline" v-if="searchForm.search || searchForm.category">
                                    Reset
                                </button>
                            </div>

                            <div class="p-4 space-y-6">
                                <div>
                                    <label class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block">Kata Kunci</label>
                                    <div class="relative">
                                        <i class="fas fa-search absolute left-3 top-3 text-gray-400"></i>
                                        <input 
                                            v-model="searchForm.search"
                                            @keyup.enter="submitSearch"
                                            type="text" 
                                            placeholder="Cari jasa..." 
                                            class="w-full bg-gray-50 border border-gray-200 rounded-lg py-2.5 pl-10 pr-4 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                                        >
                                    </div>
                                </div>

                                <div>
                                    <label class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block">Kategori</label>
                                    <div class="space-y-1 max-h-[400px] overflow-y-auto custom-scrollbar pr-1">
                                        
                                        <button 
                                            @click="searchForm.category = ''; submitSearch()"
                                            class="w-full text-left px-3 py-2 rounded-lg flex items-center transition-colors group"
                                            :class="searchForm.category === '' ? 'bg-blue-50 text-blue-700 font-semibold' : 'hover:bg-gray-50 text-gray-600'"
                                        >
                                            <div class="w-6 h-6 rounded flex items-center justify-center mr-3 transition-colors"
                                                 :class="searchForm.category === '' ? 'bg-blue-200 text-blue-700' : 'bg-gray-200 text-gray-500 group-hover:bg-gray-300'">
                                                <i class="fas fa-th-large text-xs"></i>
                                            </div>
                                            <span class="text-sm">Semua Jasa</span>
                                        </button>

                                        <button 
                                            v-for="cat in categories" 
                                            :key="cat.id"
                                            @click="searchForm.category = cat.slug; submitSearch()"
                                            class="w-full text-left px-3 py-2 rounded-lg flex items-center transition-colors group"
                                            :class="searchForm.category === cat.slug ? 'bg-blue-50 text-blue-700 font-semibold' : 'hover:bg-gray-50 text-gray-600'"
                                        >
                                            <div class="w-6 h-6 rounded flex items-center justify-center mr-3 transition-colors"
                                                 :class="searchForm.category === cat.slug ? 'bg-blue-200 text-blue-700' : 'bg-gray-200 text-gray-500 group-hover:bg-gray-300'">
                                                <i class="fas fa-tag text-xs"></i>
                                            </div>
                                            <span class="text-sm truncate">{{ cat.name }}</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="w-full md:w-3/4">
                        
                        <div class="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
                            <div>
                                <h1 class="text-2xl font-bold text-gray-900">Marketplace Jasa</h1>
                                <p class="text-sm text-gray-500 mt-1">Temukan profesional terbaik untuk kebutuhan Anda.</p>
                            </div>
                            
                            <div class="inline-flex items-center px-4 py-2 bg-white border border-gray-200 rounded-full shadow-sm text-sm text-gray-600 cursor-pointer hover:bg-gray-50 transition">
                                <i class="fas fa-map-marker-alt text-red-500 mr-2"></i>
                                <span>Lokasi: <strong>Bandung</strong></span>
                                <i class="fas fa-chevron-down ml-2 text-xs text-gray-400"></i>
                            </div>
                        </div>

                        <div v-if="services.data.length > 0">
                            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
                                <MarketplaceCard 
                                    v-for="service in services.data" 
                                    :key="service.id" 
                                    :service="service" 
                                />
                            </div>

                            <div v-if="services.next_page_url" class="mt-8 flex justify-center">
                                <a :href="services.next_page_url" class="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-full font-semibold hover:bg-gray-50 transition shadow-sm">
                                    Muat Lebih Banyak
                                </a>
                            </div>
                        </div>

                        <div v-else class="bg-white rounded-xl border border-gray-200 p-12 text-center shadow-sm">
                            <div class="h-20 w-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <i class="fas fa-search text-3xl text-gray-400"></i>
                            </div>
                            <h3 class="text-lg font-bold text-gray-900 mb-1">Tidak ada hasil ditemukan</h3>
                            <p class="text-gray-500">Coba ubah kata kunci atau kategori pencarian Anda.</p>
                            <button @click="searchForm.reset(); submitSearch()" class="mt-4 text-blue-600 font-semibold hover:underline">
                                Reset Pencarian
                            </button>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<style scoped>
/* Scrollbar tipis untuk kategori list */
.custom-scrollbar::-webkit-scrollbar {
    width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: #cbd5e1;
    border-radius: 20px;
}
</style>