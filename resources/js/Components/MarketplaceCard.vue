<script setup>
import { Link } from '@inertiajs/vue3';

defineProps({
    service: Object,
});

const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value);
};
</script>

<template>
    <div class="group relative bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 flex flex-col h-full overflow-hidden">
        
        <div class="relative w-full pt-[75%] bg-gray-100 overflow-hidden">
            <img 
                v-if="service.galleries.length > 0" 
                :src="'/storage/' + service.galleries[0].image" 
                class="absolute top-0 left-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                alt="Service Image"
            >
            <div v-else class="absolute top-0 left-0 w-full h-full flex items-center justify-center text-gray-400">
                <i class="fas fa-image text-4xl"></i>
            </div>

            <span class="absolute top-2 left-2 bg-black/50 backdrop-blur-sm text-white text-[10px] font-bold px-2 py-1 rounded">
                {{ service.category.name }}
            </span>
        </div>

        <div class="p-3 flex flex-col flex-1">
            
            <div class="text-lg font-bold text-gray-900 mb-1">
                {{ formatCurrency(service.price_min) }}
            </div>

            <h3 class="text-sm font-medium text-gray-700 line-clamp-2 mb-2 leading-snug min-h-[2.5rem]">
                {{ service.title }}
            </h3>

            <div class="mt-auto flex items-center justify-between text-xs text-gray-500">
                <div class="flex items-center">
                    <i class="fas fa-map-marker-alt mr-1 text-gray-400"></i>
                    <span class="truncate max-w-[80px]">{{ service.location || 'Online' }}</span>
                </div>
                <div class="flex items-center text-yellow-500 font-bold">
                    <i class="fas fa-star mr-1"></i>
                    <span>{{ service.rating_avg > 0 ? service.rating_avg : 'New' }}</span>
                </div>
            </div>
        </div>

        <div class="px-3 py-2 border-t border-gray-100 bg-gray-50 flex items-center justify-between">
    
            <div class="flex items-center space-x-2 relative z-20">
                <Link :href="route('profile.show', service.user.id)" class="flex items-center group/user">
                    
                    <img :src="service.user.avatar ? '/storage/' + service.user.avatar : 'https://ui-avatars.com/api/?name=' + service.user.name + '&background=random'" 
                        class="h-6 w-6 rounded-full border border-white shadow-sm object-cover group-hover/user:opacity-80 transition group-hover:ring-2 group-hover:ring-blue-100" 
                        alt="Provider">
                    
                    <span class="ml-2 text-xs text-gray-600 truncate max-w-[100px] group-hover/user:underline transition">
                        {{ service.user.name }}
                    </span>
                </Link>
            </div>
            
            <Link :href="route('service.show', service.slug)" class="absolute inset-0 z-10"></Link>
        </div>
    </div>
</template>