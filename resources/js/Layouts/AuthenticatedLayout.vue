<script setup>
import { ref } from 'vue';
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
import { Link } from '@inertiajs/vue3';

const showingNavigationDropdown = ref(false);

// Helper untuk mengecek active route agar icon berwarna biru
const routeActive = (routeName) => {
    // Gunakan try-catch agar tidak error jika route belum dibuat
    try {
        return route().current(routeName);
    } catch (e) {
        return false;
    }
};
</script>

<template>
    <div class="min-h-screen bg-gray-100">
        <nav class="bg-white border-b border-gray-200 fixed z-50 w-full top-0 shadow-sm h-16">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full">
                <div class="flex justify-between h-full">
                    
                    <div class="flex items-center shrink-0 w-1/4">
                        <Link :href="route('dashboard')">
                            <div class="bg-blue-600 text-white font-bold text-2xl h-10 w-10 flex items-center justify-center rounded-full cursor-pointer">
                                FS
                            </div>
                        </Link>
                        
                        <div class="ml-2 hidden md:block">
                            <input type="text" placeholder="Cari Jasa..." class="bg-gray-100 border-none rounded-full px-4 py-2 text-sm w-48 focus:ring-2 focus:ring-blue-500 focus:bg-white transition">
                        </div>
                    </div>

                    <div class="flex justify-center flex-1 space-x-1 md:space-x-8 h-full">
                        
                        <Link :href="route('dashboard')" 
                            class="flex items-center justify-center h-full px-4 md:px-10 border-b-4 transition-all duration-200 group relative"
                            :class="routeActive('dashboard') ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-100 hover:rounded-lg'">
                            
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                            </svg>

                            <span class="absolute bottom-1 text-[10px] hidden group-hover:block text-gray-500">Beranda</span>
                        </Link>

                        <Link :href="route('marketplace.index')" 
                            class="flex items-center justify-center h-full px-4 md:px-10 border-b-4 transition-all duration-200 group relative"
                            :class="routeActive('marketplace.index') ? 'border-blue-600' : 'border-transparent hover:bg-gray-100 hover:rounded-lg'">
                            
                            <i class="fas fa-store text-2xl h-7 w-7 flex items-center justify-center transition-colors duration-200"
                            :class="routeActive('marketplace.index') ? 'text-blue-600' : 'text-gray-500 group-hover:text-gray-700'">
                            </i>

                            <span class="absolute bottom-1 text-[10px] hidden group-hover:block text-gray-500">Market</span>
                        </Link>

                        <Link :href="route('bookings.index')" 
                            class="flex items-center justify-center h-full px-4 md:px-10 border-b-4 transition-all duration-200 group relative"
                            :class="routeActive('bookings.index') ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-100 hover:rounded-lg'">
                            
                            <i class="fas fa-clipboard-list text-2xl mb-1"></i>

                            <span class="absolute bottom-1 text-[10px] hidden group-hover:block text-gray-500">Booking</span>
                        </Link>

                         <Link :href="route('profile.index')" 
                            class="flex items-center justify-center h-full px-4 md:px-10 border-b-4 transition-all duration-200 group relative"
                            :class="routeActive('profile.index') ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-100 hover:rounded-lg'">
                            
                            <i class="fas fa-user text-2xl h-7 w-7 flex items-center justify-center transition-colors duration-200"
                            :class="routeActive('profile.index') ? 'text-blue-600' : 'text-gray-500 group-hover:text-gray-700'">
                            </i>

                            <span class="absolute bottom-1 text-[10px] hidden group-hover:block text-gray-500">Profil</span>
                        </Link>
                    </div>

                    <div class="flex items-center justify-end w-1/4 space-x-2">
                        
                        <Link :href="route('chats.index')" class="hidden md:flex h-10 w-10 bg-gray-200 rounded-full items-center justify-center hover:bg-gray-300 cursor-pointer transition relative">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-black" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                            </svg>
                            
                            <div v-if="$page.props.unread_global_count > 0" 
                                class="absolute -top-1 -right-1 h-5 w-5 bg-red-600 rounded-full border-2 border-white flex items-center justify-center">
                                <span class="text-[10px] text-white font-bold">
                                    {{ $page.props.unread_global_count > 99 ? '99+' : $page.props.unread_global_count }}
                                </span>
                            </div>
                        </Link>

                        <div class="hidden md:flex h-10 w-10 bg-gray-200 rounded-full items-center justify-center hover:bg-gray-300 cursor-pointer transition">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-black" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
                            </svg>
                        </div>

                        <div class="ml-1 relative">
    
                            <template v-if="$page.props.auth.user">
                                <Dropdown align="right" width="48">
                                    <template #trigger>
                                        <button type="button" class="flex items-center focus:outline-none">
                                            <div class="h-10 w-10 rounded-full overflow-hidden border border-gray-300 hover:opacity-90 transition">
                                                <img :src="($page.props.auth.user.avatar ? '/storage/' + $page.props.auth.user.avatar : 'https://ui-avatars.com/api/?name=' + $page.props.auth.user.name + '&background=random')" alt="Avatar" class="h-full w-full object-cover">
                                            </div>
                                            <div class="absolute bottom-0 right-0 bg-gray-100 rounded-full p-0.5 border border-white">
                                                <svg class="h-3 w-3 text-black" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                                </svg>
                                            </div>
                                        </button>
                                    </template>

                                    <template #content>
                                        <div class="px-4 py-2 border-b border-gray-100">
                                            <div class="font-bold text-gray-800">{{ $page.props.auth.user.name }}</div>
                                            <div class="text-xs text-gray-500">Lihat profil Anda</div>
                                        </div>
                                        <DropdownLink :href="route('profile.index')"> Profil Saya </DropdownLink>
                                        <DropdownLink :href="route('profile.edit')"> Pengaturan </DropdownLink>
                                        <DropdownLink :href="route('logout')" method="post" as="button"> Log Out </DropdownLink>
                                    </template>
                                </Dropdown>
                            </template>

                            <template v-else>
                                <div class="flex items-center space-x-2">
                                    <Link :href="route('login')" class="px-5 py-2 bg-blue-600 text-white text-sm font-bold rounded-full hover:bg-blue-700 transition shadow-sm z-[10000] relative">
                                        Masuk
                                    </Link>
                                    <Link :href="route('register')" class="hidden md:inline-block px-4 py-2 text-gray-600 text-sm font-bold hover:bg-gray-100 rounded-full transition z-[10000] relative">
                                        Daftar
                                    </Link>
                                </div>
                            </template>

                        </div>
                    </div>
                </div>
            </div>
        </nav>

        <main class="pt-16">
            <slot />
        </main>
    </div>
</template>