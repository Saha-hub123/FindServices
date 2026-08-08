<script setup>
import { Link, usePage, router } from '@inertiajs/vue3';
import { ref, computed } from 'vue';

const props = defineProps({
    service: Object,
});

// Helper mata uang
const formatCurrency = (value) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value);

// 1. Cek apakah user yang login adalah pemilik jasa ini
const page = usePage();
const isOwner = computed(() => {
    return page.props.auth.user && page.props.auth.user.id === props.service.user_id;
});

// 2. Logic Dropdown
const showDropdown = ref(false);

// 3. Action Toggle Status
const toggleStatus = () => {
    router.patch(route('services.toggle-status', props.service.slug), {}, {
        preserveScroll: true,
        onSuccess: () => showDropdown.value = false
    });
};

// 4. Action Delete
const deleteService = () => {
    if(confirm('Yakin ingin menghapus jasa ini?')) {
        router.delete(route('services.destroy', props.service.slug));
    }
};
</script>

<template>
    <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-5 border border-gray-200 relative group transition hover:shadow-md">
        
        <div v-if="service.status === 'inactive'" class="absolute inset-0 bg-gray-100/50 z-10 pointer-events-none"></div>
        

        <div class="p-4 flex items-center space-x-3 relative z-20">
            <div class="flex-shrink-0">
                <Link :href="route('profile.show', service.user.hash_id)">
                    <img class="h-10 w-10 rounded-full bg-gray-300 object-cover hover:opacity-80 transition hover:ring-2 hover:ring-blue-100" 
                        :src="service.user.avatar ? '/storage/' + service.user.avatar : 'https://ui-avatars.com/api/?name=' + service.user.name + '&background=random'" 
                        alt="Provider" />
                </Link>
            </div>
            <div class="min-w-0 flex-1">
                <Link :href="route('profile.show', service.user.hash_id)" class="text-sm font-medium text-gray-900 hover:text-gray-600 hover:underline transition">
                    {{ service.user.name }}
                </Link>
                <p class="text-xs text-gray-500 truncate lg:max-w-[500px] max-w-[300px]">
                    <Link v-if="service.category"
                        :href="route('marketplace.index', { category: service.category.slug })"
                        class="font-semibold text-indigo-600 hover:text-indigo-800 hover:underline transition">
                        {{ service.category.name }}
                    </Link>
                    &bull; {{ service.location || 'Online' }}
                </p>
            </div>
            
            <div class="relative flex items-center gap-2">
                <span v-if="service.status === 'inactive'" class="bg-gray-800 text-white text-[10px] font-bold px-2 py-1 rounded z-20">JASA DITUTUP</span>
                <button @click="showDropdown = !showDropdown" class="text-gray-400 hover:text-gray-600 p-1 transition">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z" />
                    </svg>
                </button>

                <div v-if="showDropdown"
                    class="absolute right-0 top-8 mt-1 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100 animate-fade-in origin-top-right">
                    <Link :href="route('service.show', service.slug)"
                        class="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 transition">
                        <i class="fas fa-external-link-alt text-blue-500 w-5 text-center"></i> Lihat Halaman
                    </Link>

                    <template v-if="isOwner">
                        <div class="border-t border-gray-100 my-1"></div>

                        <button @click="toggleStatus(service)"
                            class="w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 flex items-center gap-2 transition"
                            :class="service.status === 'active' ? 'text-gray-700' : 'text-green-600 font-bold'">
                            <i class="fas w-5 text-center"
                                :class="service.status === 'active' ? 'fa-ban text-gray-400' : 'fa-door-open'"></i>
                            {{ service.status === 'active' ? 'Tutup Jasa' : 'Buka Jasa' }}
                        </button>

                        <Link :href="route('services.edit', service.slug)"
                            class="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 transition">
                            <i class="fas fa-edit text-yellow-500 w-5 text-center"></i> Edit Jasa
                        </Link>

                        <button @click="confirmServiceDeletion(service)"
                            class="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 transition">
                            <i class="fas fa-trash-alt w-5 text-center"></i> Hapus Jasa
                        </button>
                    </template>
                </div>

                <div v-if="showDropdown" @click="showDropdown = false" class="fixed inset-0 z-40 cursor-default"></div>
            </div>
        </div>

        <Link :href="route('service.show', service.slug)" class="block relative z-0">
            <div class="px-4 pb-2">
                <h3 class="text-lg font-bold text-gray-800 hover:text-blue-600 transition">{{ service.title }}</h3> 
                <p class="mt-1 text-sm text-gray-600 line-clamp-2">
                    {{ service.description }}
                </p>
            </div>

            <div v-if="service.galleries && service.galleries.length > 0" class="mt-2 bg-gray-100 relative">
                <img :src="'/storage/' + service.galleries[0].image" 
                     class="w-full h-64 object-cover transition"
                     :class="service.status === 'inactive' ? 'grayscale opacity-80' : ''"
                     alt="Service Image">
            </div>
            <div v-else class="mt-2 h-64 bg-gray-100 flex items-center justify-center text-gray-400">
                <i class="fas fa-image text-4xl"></i>
            </div>
        </Link>

        <div class="px-4 py-3 bg-gray-50 flex justify-between items-center border-t border-gray-100 relative z-20">
            <div>
                <span class="text-xs text-gray-500 block">Mulai dari</span>
                <span class="text-lg font-bold text-gray-900">{{ formatCurrency(service.price_min) }}</span>
            </div>

            <Link :href="route('service.show', service.slug)"
                  class="inline-flex items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-blue-700 active:bg-blue-900 focus:outline-none transition ease-in-out duration-150">
                Lihat Detail & Booking
            </Link>
        </div>
        
        <div class="px-4 py-2 border-t border-gray-100 flex items-center text-sm text-gray-500">
            <div class="flex items-center mr-4">
                <svg class="h-4 w-4 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                <span>{{ Number(service.rating_avg || 0).toFixed(1) }} ({{ service.reviews_count }} Review)</span>
            </div>
        </div>
        
    </div>
</template>