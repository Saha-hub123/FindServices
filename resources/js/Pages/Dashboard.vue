<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import ServiceCard from '@/Components/ServiceCard.vue';
import { Head, Link, router } from '@inertiajs/vue3';

// Menerima props dari controller
const props = defineProps({
    services: Object,
    categories: Array,
    is_guest: Boolean // Status apakah user tamu atau bukan
});

// Fungsi Jebakan: Redirect ke Login saat area konten diklik oleh tamu
const redirectToLogin = (event) => {
    // Stop aksi default (misal klik link) dan stop bubbling
    event.preventDefault();
    event.stopPropagation();
    // Arahkan ke halaman login
    router.get(route('login'));
};
</script>

<template>
    <Head title="Beranda Marketplace" />

    <AuthenticatedLayout>
        <div 
            class="py-6 bg-gray-100 min-h-screen" 
            @click.capture="is_guest ? redirectToLogin($event) : null"
            :class="{ 'cursor-pointer': is_guest }"
            :title="is_guest ? 'Klik untuk Login' : ''"
        >
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    
                    <div class="hidden lg:block lg:col-span-3">
                        <div class="sticky top-20 space-y-4">
                            <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                                <h3 class="font-bold text-gray-700 mb-3">Menu Pintas</h3>
                                <ul class="space-y-2">
                                    <li>
                                        <Link :href="route('dashboard')" class="flex items-center text-gray-600 hover:bg-gray-50 p-2 rounded-md font-medium">
                                            <span class="mr-2">🏠</span> Beranda
                                        </Link>
                                    </li>
                                    <li>
                                        <Link :href="route('profile.edit')" class="flex items-center text-gray-600 hover:bg-gray-50 p-2 rounded-md font-medium">
                                            <span class="mr-2">👤</span> Profil Saya
                                        </Link>
                                    </li>
                                    <li>
                                        <Link href="#" class="flex items-center text-gray-600 hover:bg-gray-50 p-2 rounded-md font-medium">
                                            <span class="mr-2">📅</span> Booking Saya
                                        </Link>
                                    </li>
                                </ul>
                            </div>

                            <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                                <h3 class="font-bold text-gray-700 mb-3">Kategori</h3>
                                <ul class="space-y-1">
                                    <li v-for="cat in categories" :key="cat.id">
                                        <Link href="#" class="block px-2 py-1.5 text-sm text-gray-600 hover:bg-gray-50 rounded-md">
                                            {{ cat.name }}
                                        </Link>
                                    </li>
                                    <li v-if="categories.length === 0" class="text-sm text-gray-400 italic">
                                        Belum ada kategori
                                    </li>
                                </ul>
                                <div class="mt-4 pt-4 border-t border-gray-100">
                                     <button class="text-blue-600 text-sm font-medium hover:underline">
                                        + Request Kategori Baru
                                     </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="lg:col-span-6">
                        
                        <div v-if="$page.props.auth.user" class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6 flex items-center space-x-4">
                            <div class="h-10 w-10 rounded-full bg-gray-200 flex-shrink-0 overflow-hidden">
                                <img :src="'https://ui-avatars.com/api/?name=' + $page.props.auth.user.name" alt="Me">
                            </div>
                            <Link :href="route('services.create')" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-500 py-2.5 px-4 rounded-full text-left cursor-pointer transition">
                                Tawarkan jasa barumu di sini, {{ $page.props.auth.user.name }}?
                            </Link>
                        </div>

                        <div v-else class="bg-blue-600 p-4 rounded-lg shadow-sm mb-6 text-white text-center">
                            <h3 class="font-bold text-lg">Selamat Datang di FindServices!</h3>
                            <p class="text-blue-100 text-sm">Login untuk mulai menawarkan jasa atau membooking layanan.</p>
                        </div>

                        <div v-if="services.data.length > 0">
                            <ServiceCard 
                                v-for="service in services.data" 
                                :key="service.id" 
                                :service="service" 
                            />
                        </div>
                        
                        <div v-else class="bg-white p-8 rounded-lg shadow-sm text-center">
                            <p class="text-gray-500">Belum ada jasa yang tersedia saat ini.</p>
                        </div>

                        <div class="mt-4 flex justify-center">
                            </div>
                    </div>

                    <div class="hidden lg:block lg:col-span-3">
                        <div class="sticky top-20 space-y-4">
                            
                            <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                                <h3 class="font-bold text-gray-500 uppercase text-xs tracking-wider mb-3">Sedang Populer</h3>
                                <div class="space-y-3">
                                    <div class="flex items-center space-x-3 cursor-pointer hover:bg-gray-50 p-1 rounded">
                                        <div class="h-10 w-10 bg-blue-100 rounded-md flex items-center justify-center text-blue-500 font-bold">
                                            AC
                                        </div>
                                        <div>
                                            <p class="text-sm font-medium text-gray-900">Service AC Dingin</p>
                                            <p class="text-xs text-gray-500">Rp 75.000</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="text-xs text-gray-400 px-2">
                                <a href="#" class="hover:underline">Privacy</a> &bull; 
                                <a href="#" class="hover:underline">Terms</a> &bull; 
                                <span>FindServices © 2025</span>
                            </div>

                        </div>
                    </div>

                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>