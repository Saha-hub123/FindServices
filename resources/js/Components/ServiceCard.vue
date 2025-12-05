<script setup>
import { Link } from '@inertiajs/vue3';

// Props menerima data 1 service
defineProps({
    service: Object,
});

// Helper untuk format mata uang
const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' }).format(value);
};
</script>

<template>
    <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-5 border border-gray-200">
        <div class="p-4 flex items-center space-x-3">
            <div class="flex-shrink-0">
                <Link :href="route('profile.show', service.user.id)">
                <img class="h-10 w-10 rounded-full bg-gray-300 object-cover hover:opacity-80 transition hover:ring-4 hover:ring-blue-100" 
                    :src="service.user.avatar ? '/storage/' + service.user.avatar : 'https://ui-avatars.com/api/?name=' + service.user.name + '&background=random'" 
                    alt="Provider Avatar" />
                </Link>
            </div>
            <div class="min-w-0 flex-1">
                <Link :href="route('profile.show', service.user.id)" class="text-sm font-medium text-gray-900 hover:text-gray-600 hover:underline transition">
                    {{ service.user.name }}
                </Link>
                <p class="text-xs text-gray-500">
                    <span class="font-semibold text-indigo-600">{{ service.category.name }}</span> 
                    &bull; {{ service.location || 'Online' }}
                </p>
            </div>
            <button class="text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z" />
                </svg>
            </button>
        </div>

        <div class="px-4 pb-2">
            <h3 class="text-lg font-bold text-gray-800">{{ service.title }}</h3>
            <p class="mt-1 text-sm text-gray-600 line-clamp-3">
                {{ service.description }}
            </p>
        </div>

        <div v-if="service.galleries.length > 0" class="mt-2 bg-gray-100">
            <img :src="'/storage/' + service.galleries[0].image" 
                 class="w-full h-64 object-cover hover:opacity-95 transition-opacity cursor-pointer" 
                 alt="Service Image">
        </div>

        <div class="px-4 py-3 bg-gray-50 flex justify-between items-center border-t border-gray-100">
            <div>
                <span class="text-xs text-gray-500 block">Mulai dari</span>
                <span class="text-lg font-bold text-gray-900">{{ formatCurrency(service.price_min) }}</span>
            </div>
            
            
            <Link :href="route('service.show', service.id)" 
                  class="inline-flex items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-blue-700 active:bg-blue-900 focus:outline-none transition ease-in-out duration-150">
                Lihat Detail & Booking
            </Link>
        </div>
        
        <div class="px-4 py-2 border-t border-gray-100 flex items-center text-sm text-gray-500">
            <div class="flex items-center mr-4">
                <svg class="h-4 w-4 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                <span>{{ service.rating_avg.toFixed(1) }} ({{ service.reviews_count }} Review)</span>
            </div>
        </div>
    </div>
</template>