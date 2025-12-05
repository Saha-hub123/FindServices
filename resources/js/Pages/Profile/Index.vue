<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import MarketplaceCard from '@/Components/MarketplaceCard.vue';
import ServiceCard from '@/Components/ServiceCard.vue';
import { Head, Link, router } from '@inertiajs/vue3'; // Tambahkan router
import { ref } from 'vue';

// --- IMPORT KOMPONEN BREEZE ---
import Modal from '@/Components/Modal.vue';
import DangerButton from '@/Components/DangerButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';

const props = defineProps({
    auth_user: Object,
    services: Array,
    stats: Object
});

const viewMode = ref('grid');

// --- LOGIC KONFIRMASI HAPUS ---
const confirmingServiceDeletion = ref(false);
const serviceToDeleteId = ref(null);

const confirmServiceDeletion = (id) => {
    serviceToDeleteId.value = id;
    confirmingServiceDeletion.value = true;
};

const deleteService = () => {
    router.delete(route('services.destroy', serviceToDeleteId.value), {
        preserveScroll: true,
        onSuccess: () => closeModal(),
        onFinish: () => serviceToDeleteId.value = null,
    });
};

const closeModal = () => {
    confirmingServiceDeletion.value = false;
    setTimeout(() => serviceToDeleteId.value = null, 300); // Delay clear ID agar animasi modal mulus
};
</script>

<template>
    <Head title="Profil Saya" />

    <AuthenticatedLayout>
        <div class="bg-gray-50 min-h-screen py-8">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8 mb-8">
                    <div class="flex flex-col md:flex-row items-center md:items-start gap-6 md:gap-10">
                        
                        <div class="shrink-0 relative group">
                            <div class="h-24 w-24 md:h-36 md:w-36 rounded-full p-1 border-2 border-gray-200 overflow-hidden">
                                <img 
                                    :src="auth_user.avatar ? '/storage/' + auth_user.avatar : 'https://ui-avatars.com/api/?name=' + auth_user.name + '&background=random&size=150'" 
                                    alt="Profile Photo" 
                                    class="h-full w-full rounded-full object-cover"
                                >
                            </div>
                            <Link :href="route('profile.edit')" class="absolute bottom-2 right-2 bg-gray-100 p-2 rounded-full border border-gray-300 hover:bg-gray-200 transition">
                                <i class="fas fa-camera text-gray-600"></i>
                            </Link>
                        </div>

                        <div class="flex-1 text-center md:text-left w-full">
                            
                            <div class="flex flex-col md:flex-row items-center gap-4 mb-4">
                                <h1 class="text-2xl md:text-3xl font-light text-gray-800">{{ auth_user.name }}</h1>
                                <div class="flex gap-2">
                                    <Link :href="route('profile.edit')" class="px-4 py-3 bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold rounded-md text-sm border border-gray-300 transition">
                                        Edit Profil
                                    </Link>
                                    <button class="p-2 text-gray-800 hover:text-gray-600">
                                        <i class="fas fa-cog text-xl"></i>
                                    </button>
                                </div>
                            </div>

                            <div class="flex justify-center md:justify-start gap-8 mb-4 border-t border-b md:border-0 py-3 md:py-0 border-gray-100">
                                <div class="text-center md:text-left">
                                    <span class="font-bold text-gray-900 block md:inline text-lg md:text-base">{{ stats.services_count }}</span>
                                    <span class="text-gray-600 ml-1">Jasa</span>
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
                                <p class="font-semibold">{{ auth_user.email }} || {{ auth_user.phone }}</p> <p class="whitespace-pre-line">{{ auth_user.bio || 'Belum ada bio. Tulis sesuatu tentang keahlian Anda!' }}</p>
                                <p v-if="auth_user.address" class="text-gray-500 mt-1">
                                    <i class="fas fa-map-marker-alt mr-1"></i> {{ auth_user.address }}
                                </p>
                            </div>

                        </div>
                    </div>
                </div>

                <div class="border-t border-gray-300 mb-6">
                    <div class="flex justify-center gap-12">
                        <button class="border-t-2 border-black py-3 flex items-center gap-2 text-xs md:text-sm font-bold tracking-widest text-gray-800">
                            <i class="fas fa-th"></i> ETALASE JASA
                        </button>
                        <button class="border-t-2 border-transparent py-3 flex items-center gap-2 text-xs md:text-sm font-bold tracking-widest text-gray-400 hover:text-gray-600">
                            <i class="fas fa-star"></i> REVIEW
                        </button>
                        <Link :href="route('services.trash')" class="text-gray-400 hover:text-red-600 transition py-3" title="Lihat Sampah">
                            <i class="fas fa-trash-alt text-lg"></i>
                        </Link>
                    </div>
                </div>

                <div class="mt-4">
        
                    <div class="flex justify-end px-2 mb-4">
                        <div class="bg-white border border-gray-300 rounded-lg p-1 flex space-x-1">
                            <button 
                                @click="viewMode = 'grid'"
                                class="p-2 rounded-md transition-all flex items-center justify-center"
                                :class="viewMode === 'grid' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'"
                                title="Tampilan Grid"
                            >
                                <i class="fas fa-th-large text-lg"></i>
                            </button>

                            <button 
                                @click="viewMode = 'list'"
                                class="p-2 rounded-md transition-all flex items-center justify-center"
                                :class="viewMode === 'list' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'"
                                title="Tampilan List"
                            >
                                <i class="fas fa-list text-lg"></i>
                            </button>
                        </div>
                    </div>

                    <div v-if="services.length > 0">
                        
                        <div v-if="viewMode === 'grid'" class="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-4 animate-fade-in">
                
                            <Link :href="route('services.create')" class="group relative bg-gray-50 border-2 border-dashed border-gray-300 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all duration-200 flex flex-col items-center justify-center min-h-[260px] cursor-pointer">
                                <div class="h-14 w-14 bg-white rounded-full shadow-sm border border-gray-200 flex items-center justify-center mb-3 group-hover:scale-110 group-hover:shadow-md transition-all">
                                    <i class="fas fa-plus text-2xl text-gray-400 group-hover:text-blue-600"></i>
                                </div>
                                <span class="text-sm font-bold text-gray-500 group-hover:text-blue-700">Tambah Jasa Baru</span>
                                <span class="text-xs text-gray-400 mt-1 group-hover:text-blue-600/70">Mulai berjualan</span>
                            </Link>

                            <div v-for="service in services" :key="service.id" class="relative group h-full">
                                <div class="h-full">
                                    <MarketplaceCard :service="service" />
                                </div>
                                
                                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center gap-3 rounded-xl z-20 pointer-events-none md:pointer-events-auto">
                                    <Link :href="route('service.show', service.id)" class="bg-white text-gray-800 h-10 w-10 flex items-center justify-center rounded-full hover:bg-gray-100 pointer-events-auto shadow-lg transform hover:scale-110 transition" title="Lihat">
                                        <i class="fas fa-eye"></i>
                                    </Link>
                                    <Link :href="route('services.edit', service.id)" class="bg-blue-600 text-white h-10 w-10 flex items-center justify-center rounded-full hover:bg-blue-700 pointer-events-auto shadow-lg transform hover:scale-110 transition" title="Edit">
                                        <i class="fas fa-edit"></i>
                                    </Link>
                                    <button @click="confirmServiceDeletion(service.id)" class="bg-red-600 text-white h-10 w-10 flex items-center justify-center rounded-full hover:bg-red-700 pointer-events-auto shadow-lg transform hover:scale-110 transition" title="Hapus">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>

                        </div>

                        <div v-else class="flex flex-col space-y-3 max-w-2xl mx-auto animate-fade-in">
                            <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-3 flex items-center space-x-4">
                                <div class="h-10 w-10 rounded-full bg-gray-200 flex-shrink-0 overflow-hidden">
                                    <img :src="'https://ui-avatars.com/api/?name=' + $page.props.auth.user.name" alt="Me">
                                </div>
                                <Link :href="route('services.create')" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-500 py-2.5 px-4 rounded-full text-left cursor-pointer transition">
                                    Tawarkan jasa barumu di sini, {{ $page.props.auth.user.name }}?
                                </Link>
                            </div>
                            
                            <div v-for="service in services" :key="'list-' + service.id" class="relative">
                                <ServiceCard :service="service" />

                                <div class="absolute top-4 right-4 bg-white/80 backdrop-blur rounded-lg shadow-sm border border-gray-200 p-1 flex space-x-1">
                                    <Link :href="route('services.edit', service.id)" class="p-2 text-blue-600 hover:bg-blue-50 rounded" title="Edit Jasa">
                                        <i class="fas fa-pencil-alt"></i>
                                    </Link>
                                    <button @click="confirmServiceDeletion(service.id)" class="p-2 text-red-600 hover:bg-red-50 rounded" title="Hapus Jasa">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>

                    </div>

                    <div v-else class="flex flex-col items-center justify-center py-12 bg-white rounded-lg border border-dashed border-gray-300">
                        <div class="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                            <i class="fas fa-camera text-2xl text-gray-400"></i>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900">Belum ada Jasa</h3>
                        <p class="text-gray-500 mb-6 text-sm text-center">Mulai tawarkan keahlian Anda sekarang.</p>
                        <Link :href="route('services.create')" class="text-blue-500 font-bold hover:underline">
                            + Buat Jasa Pertama
                        </Link>
                    </div>

                </div>

            </div>
        </div>
        <Modal :show="confirmingServiceDeletion" @close="closeModal">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900">
                    Apakah Anda yakin ingin menghapus jasa ini?
                </h2>

                <p class="mt-1 text-sm text-gray-600">
                    Jasa yang dihapus tidak akan tampil lagi di etalase, namun riwayat transaksi yang sudah terjadi akan tetap tersimpan aman.
                </p>

                <div class="mt-6 flex justify-end">
                    <SecondaryButton @click="closeModal">
                        Batal
                    </SecondaryButton>

                    <DangerButton
                        class="ml-3"
                        @click="deleteService"
                    >
                        Hapus Jasa
                    </DangerButton>
                </div>
            </div>
        </Modal>

    </AuthenticatedLayout>
</template>

<style scoped>
/* Animasi halus saat switch tab */
.animate-fade-in {
    animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>