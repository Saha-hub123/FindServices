<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, router } from '@inertiajs/vue3';

defineProps({
    services: Array
});

// Helper Format Rupiah
const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value);
};

// Fungsi Restore
const restoreService = (id) => {
    router.post(route('services.restore', id), {}, {
        preserveScroll: true,
    });
};

// Fungsi Hapus Permanen
const forceDeleteService = (id) => {
    if (confirm('PERINGATAN: Apakah Anda yakin ingin menghapus jasa ini secara permanen? Data tidak bisa dikembalikan.')) {
        router.delete(route('services.force-delete', id), {
            preserveScroll: true,
        });
    }
};
</script>

<template>
    <Head title="Sampah Jasa" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h1 class="text-2xl font-bold text-gray-800">Tong Sampah</h1>
                        <p class="text-sm text-gray-500">Jasa yang dihapus sementara. Bisa dikembalikan atau dihapus selamanya.</p>
                    </div>
                    <Link :href="route('profile.index')" class="text-sm text-gray-600 hover:text-blue-600 font-medium">
                        &larr; Kembali ke Profil
                    </Link>
                </div>

                <div v-if="services.length > 0" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    
                    <div v-for="service in services" :key="service.id" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col opacity-75 hover:opacity-100 transition duration-200">
                        
                        <div class="h-40 w-full bg-gray-200 relative grayscale">
                            <img v-if="service.galleries && service.galleries.length > 0" 
                                 :src="'/storage/' + service.galleries[0].image" 
                                 class="w-full h-full object-cover">
                            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                                <i class="fas fa-image text-3xl"></i>
                            </div>
                            <div class="absolute top-2 right-2 bg-red-600 text-white text-[10px] font-bold px-2 py-1 rounded shadow-sm">
                                TERHAPUS
                            </div>
                        </div>

                        <div class="p-4 flex-1">
                            <h3 class="font-bold text-gray-800 line-clamp-1 mb-1">{{ service.title }}</h3>
                            <p class="text-sm text-gray-500 line-clamp-2 mb-2">{{ service.description }}</p>
                            <p class="text-blue-600 font-bold text-sm">{{ formatCurrency(service.price_min) }}</p>
                        </div>

                        <div class="p-3 bg-gray-50 border-t border-gray-100 grid grid-cols-2 gap-2">
                            
                            <button @click="restoreService(service.id)" 
                                    class="flex items-center justify-center px-3 py-2 bg-green-100 text-green-700 text-xs font-bold rounded hover:bg-green-200 transition">
                                <i class="fas fa-trash-restore mr-1.5"></i> Restore
                            </button>

                            <!-- <button @click="forceDeleteService(service.id)" 
                                    class="flex items-center justify-center px-3 py-2 bg-red-100 text-red-700 text-xs font-bold rounded hover:bg-red-200 transition">
                                <i class="fas fa-times mr-1.5"></i> Hapus
                            </button> -->
                            <button 
                                    class="flex items-center justify-center px-3 py-2 bg-red-100 text-red-700 text-xs font-bold rounded hover:bg-red-200 transition">
                                <i class="fas fa-times mr-1.5"></i> Hapus
                            </button>

                        </div>
                    </div>

                </div>

                <div v-else class="flex flex-col items-center justify-center py-20 bg-white rounded-xl border border-dashed border-gray-300 text-center">
                    <div class="h-16 w-16 bg-green-50 rounded-full flex items-center justify-center mb-4">
                        <i class="fas fa-leaf text-2xl text-green-500"></i>
                    </div>
                    <h3 class="text-lg font-bold text-gray-800">Tong Sampah Kosong</h3>
                    <p class="text-gray-500 text-sm mt-1">Tidak ada jasa yang dihapus saat ini.</p>
                </div>

            </div>
        </div>
    </AuthenticatedLayout>
</template>