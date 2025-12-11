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
    reviews: Array,      // Review Saya
    givenReviews: Array, // [BARU] Ulasan Keluar
    stats: Object
});

const viewMode = ref('grid');
const activeTab = ref('services');
const reviewFilter = ref('received'); // [BARU] 'received' atau 'given'

const formatDate = (date) => {
    return new Date(date).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' });
};

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
                        </div>

                        <div class="flex-1 text-center md:text-left w-full">
                            
                            <div class="flex flex-col md:flex-row items-center gap-4 mb-4">
                                <h1 class="text-xl md:text-2xl font-light text-gray-800">{{ auth_user.name }}</h1>
                                
                                <div class="flex gap-2 items-center">
                                    <Link :href="route('profile.edit')" class="px-4 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold rounded-md text-sm border border-gray-300 transition">
                                        Edit Profil
                                    </Link>
                                    
                                    <Link :href="route('profile.settings')" class="p-2 text-gray-800 hover:text-gray-600">
                                        <i class="fas fa-cog text-xl"></i>
                                    </Link>
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
                                <p class="font-semibold">{{ auth_user.email }} || {{ auth_user.phone }}</p> <p class="whitespace-pre-line mt-1">{{ auth_user.bio || 'Belum ada bio. Tulis sesuatu tentang keahlian Anda!' }}</p>
                                <p v-if="auth_user.address" class="text-gray-500 mt-2 flex items-center justify-center md:justify-start">
                                    <i class="fas fa-map-marker-alt mr-1.5 text-red-500"></i> {{ auth_user.address }}
                                </p>
                            </div>

                        </div>
                    </div>
                </div>

            <div class="border-t border-gray-300 mb-6 relative"> 
                <div class="flex justify-center gap-8 md:gap-12 px-12"> 
                    <button @click="activeTab = 'services'" class="py-4 flex items-center gap-2 text-xs md:text-sm font-bold tracking-widest transition-colors duration-200" :class="activeTab === 'services' ? 'border-t-2 border-black text-gray-800' : 'border-t-2 border-transparent text-gray-400 hover:text-gray-600'">
                        <i class="fas fa-th"></i> ETALASE JASA
                    </button>
                    <button @click="activeTab = 'reviews'" class="py-4 flex items-center gap-2 text-xs md:text-sm font-bold tracking-widest transition-colors duration-200" :class="activeTab === 'reviews' ? 'border-t-2 border-black text-gray-800' : 'border-t-2 border-transparent text-gray-400 hover:text-gray-600'">
                        <i class="fas fa-star"></i> REVIEW
                    </button>
                    <Link :href="route('services.trash')" class="text-gray-400 hover:text-red-600 transition py-3 flex items-center" title="Lihat Sampah">
                        <i class="fas fa-trash-alt text-lg"></i>
                    </Link>
                </div>

                <div v-if="activeTab === 'services'" class="absolute right-0 top-1/2 -translate-y-1/2 pr-2 md:pr-4">
                    <div class="bg-white border border-gray-300 rounded-lg p-1 flex space-x-1">
                        <button @click="viewMode = 'grid'" class="p-1 rounded-md transition-all flex items-center justify-center" :class="viewMode === 'grid' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'"><i class="fas fa-th-large text-lg"></i></button>
                        <button @click="viewMode = 'list'" class="p-1 rounded-md transition-all flex items-center justify-center" :class="viewMode === 'list' ? 'bg-gray-200 text-black shadow-sm' : 'text-gray-400 hover:text-gray-600'"><i class="fas fa-list text-lg"></i></button>
                    </div>
                </div>
                <div v-if="activeTab === 'reviews'" class="absolute right-0 top-1/2 -translate-y-1/2 pr-2 md:pr-4">
                    <div class="bg-white border border-gray-300 rounded-lg p-1 flex space-x-1">
                        <button @click="reviewFilter = 'received'" class="px-3 py-1 rounded-md text-xs font-bold transition-all" :class="reviewFilter === 'received' ? 'bg-gray-800 text-white shadow-sm' : 'text-gray-500 hover:bg-gray-100'">
                            Masuk
                        </button>
                        <button @click="reviewFilter = 'given'" class="px-3 py-1 rounded-md text-xs font-bold transition-all" :class="reviewFilter === 'given' ? 'bg-gray-800 text-white shadow-sm' : 'text-gray-500 hover:bg-gray-100'">
                            Keluar
                        </button>
                    </div>
                </div>
            </div>
                

                <div class="mt-4">
                    <div v-if="activeTab === 'services'" class="animate-fade-in mt-4">
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
                                    
                                    <div class="absolute inset-0 bg-black/40 rounded-xl opacity-0 group-hover:opacity-100 transition flex flex-col items-center justify-center gap-3 z-30 backdrop-blur-sm">
                                        <Link :href="route('service.show', service.slug)" class="bg-blue-400 text-blue-900 px-6 py-2 rounded-full font-bold text-sm hover:bg-blue-300 transition w-28 text-center">
                                            <i class="fas fa-sign-in-alt mr-1"></i> Lihat
                                        </Link>
                                        <Link :href="route('services.edit', service.slug)" class="bg-yellow-400 text-yellow-900 px-6 py-2 rounded-full font-bold text-sm hover:bg-yellow-300 transition w-28 text-center">
                                            <i class="fas fa-edit mr-1"></i> Edit
                                        </Link>
                                        <button @click="deleteService(service)" class="bg-red-500 text-white px-6 py-2 rounded-full font-bold text-sm hover:bg-red-600 transition w-28">
                                            <i class="fas fa-trash-alt mr-1"></i> Hapus
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
                                        <Link :href="route('services.edit', service)" class="p-2 text-yellow-600 hover:bg-yellow-50 rounded" title="Edit Jasa">
                                            <i class="fas fa-edit"></i>
                                        </Link>
                                        <button @click="confirmServiceDeletion(service)" class="p-2 text-red-600 hover:bg-red-50 rounded" title="Hapus Jasa">
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

                    <div v-if="activeTab === 'reviews'" class="mt-4 animate-fade-in space-y-4">
    
                        <div v-if="reviewFilter === 'received'">
                            <div v-if="reviews.length > 0" class="space-y-4">
                                <div v-for="review in reviews" :key="review.id" class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
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
                                    
                                    <p class="text-gray-700 text-sm leading-relaxed mb-4 pl-1">"{{ review.review }}"</p>
                                    
                                    <div class="bg-gray-50 p-2.5 rounded-lg flex items-center gap-3 border border-gray-100">
                                        <img v-if="review.service.galleries && review.service.galleries[0]" :src="'/storage/' + review.service.galleries[0].image" class="h-8 w-8 rounded object-cover">
                                        <Link :href="route('service.show', review.service.slug)" class="text-xs font-bold text-gray-600 hover:text-blue-600 truncate hover:underline flex-1">
                                            <span class="font-normal text-gray-400 mr-1">Jasa Saya:</span> {{ review.service.title }}
                                        </Link>
                                    </div>
                                </div>
                            </div>
                            <div v-else class="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
                                <i class="fas fa-inbox text-4xl text-gray-300 mb-3"></i>
                                <p class="text-gray-500">Belum ada ulasan masuk.</p>
                            </div>
                        </div>

                        <div v-else-if="reviewFilter === 'given'">
                            <div v-if="givenReviews.length > 0" class="space-y-4">
                                <div v-for="review in givenReviews" :key="'given-'+review.id" class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm opacity-90 hover:opacity-100 transition">
                                    <div class="flex justify-between items-start mb-3">
                                        <Link :href="route('profile.show', review.service.user.id)" class="flex items-center gap-3 group">
                                            <img :src="review.service.user.avatar ? '/storage/' + review.service.user.avatar : 'https://ui-avatars.com/api/?name=' + review.service.user.name" class="h-10 w-10 rounded-full object-cover border border-gray-100 group-hover:opacity-80 transition">
                                            <div>
                                                <p class="text-sm font-bold text-gray-800 group-hover:text-blue-600 group-hover:underline transition">
                                                    <span class="font-normal text-gray-400 text-xs block">Untuk:</span>
                                                    {{ review.service.user.name }}
                                                </p>
                                                <p class="text-[10px] text-gray-400">{{ formatDate(review.created_at) }}</p>
                                            </div>
                                        </Link>
                                        <div class="flex text-yellow-400 text-xs">
                                            <i v-for="n in 5" :key="n" class="fas fa-star" :class="n <= review.rating ? 'text-yellow-400' : 'text-gray-200'"></i>
                                        </div>
                                    </div>
                                    
                                    <p class="text-gray-700 text-sm leading-relaxed mb-4 pl-1 italic">"{{ review.review }}"</p>
                                    
                                    <div class="bg-blue-50 p-2.5 rounded-lg flex items-center gap-3 border border-blue-100">
                                        <img v-if="review.service.galleries && review.service.galleries[0]" :src="'/storage/' + review.service.galleries[0].image" class="h-8 w-8 rounded object-cover">
                                        <Link :href="route('service.show', review.service.slug)" class="text-xs font-bold text-blue-800 hover:text-blue-600 truncate hover:underline flex-1">
                                            <span class="font-normal text-blue-400 mr-1">Jasa:</span> {{ review.service.title }}
                                        </Link>
                                    </div>
                                </div>
                            </div>
                            <div v-else class="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
                                <i class="fas fa-paper-plane text-4xl text-gray-300 mb-3"></i>
                                <p class="text-gray-500">Anda belum pernah memberikan ulasan.</p>
                            </div>
                        </div>

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