<script setup>
import { ref, nextTick, onMounted, computed, watch } from 'vue';
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
import { Link, usePage, router } from '@inertiajs/vue3';

const showingNavigationDropdown = ref(false);

const page = usePage();
const user = computed(() => page.props.auth.user);

// 1. STATE LOKAL UNTUK REALTIME COUNT
// Inisialisasi awal ambil dari database (via props Inertia)
const unreadMsgCount = ref(page.props.unread_global_count || 0);
const unreadNotifCount = ref(0); // Misal nanti ada notifikasi sistem

// 2. WATCHER (PENTING UNTUK IS READ/RESET)
// Ini intinya! Saat kamu klik menu Chat, halaman pindah -> Backend kirim data baru (0).
// Watcher ini mendeteksi perubahan itu dan mereset angka di navbar jadi 0.
watch(() => page.props.unread_global_count, (newCount) => {
    unreadMsgCount.value = newCount;
});

// 2. LISTENER REALTIME (Laravel Echo)
onMounted(() => {
    if (window.Echo && user.value) {
        
        // [PERBAIKAN DISINI]
        // Ganti 'users.${user.value.id}' menjadi 'chat.${user.value.id}'
        // Sesuai dengan channels.php Anda: Broadcast::channel('chat.{userId}'...
        window.Echo.private(`chat.${user.value.id}`)
            
            .listen('MessageSent', (e) => {
                // Debugging: Cek di console apakah event masuk
                console.log('Pesan baru diterima:', e);

                // Tambah counter notifikasi
                unreadMsgCount.value++; 
                
                // 2. MAINKAN SUARA
                try {
                    // Pastikan path ini sesuai dengan lokasi file Anda di folder public
                    const audio = new Audio('/audio/coin-recieved.mp3');
                    
                    // Mainkan suara
                    const playPromise = audio.play();

                    if (playPromise !== undefined) {
                        playPromise.catch((error) => {
                            // Error ini wajar jika user belum pernah klik apapun di halaman (Autoplay Policy)
                            console.log("Browser memblokir autoplay audio:", error);
                        });
                    }
                } catch (err) {
                    console.error("Gagal memuat audio:", err);
                }
            })

            // B. DENGARKAN NOTIFIKASI SISTEM (DatabaseNotification)
            // Ini bawaan Laravel Notification
            .notification((notification) => {
                unreadNotifCount.value++;
            });
    }
});

// Logic Search Mobile
const isMobileSearchActive = ref(false);
const searchInputRef = ref(null);

const toggleMobileSearch = () => {
    isMobileSearchActive.value = true;
    nextTick(() => { if (searchInputRef.value) searchInputRef.value.focus(); });
};

const closeMobileSearch = () => {
    // Delay sedikit agar klik tombol search/submit terbaca dulu
    setTimeout(() => { isMobileSearchActive.value = false; }, 200);
};

const routeActive = (routeName) => {
    try { return route().current(routeName); } catch (e) { return false; }
};

// State Search Query
const searchQuery = ref('');

const handleSearch = () => {
    if (searchQuery.value.trim() !== '') {
        router.get(route('search.index'), { q: searchQuery.value });
        // Opsional: Tutup search mobile setelah enter
        closeMobileSearch();
    }
};
</script>

<template>
    <div class="min-h-screen bg-gray-100">
        
        <nav class="bg-white border-b border-gray-200 fixed z-50 w-full top-0 shadow-sm h-16">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full">
                
                <div class="flex justify-between h-full items-center">
                    
                    <div class="flex items-center flex-1 md:flex-none md:w-1/3 lg:w-1/4 gap-4">
                        
                        <Link :href="route('dashboard')" class="shrink-0 transition-opacity duration-200"
                              :class="isMobileSearchActive ? 'opacity-0 w-0 overflow-hidden' : 'opacity-100'">
                            <div class="bg-blue-600 text-white font-bold text-2xl h-10 w-10 flex items-center justify-center rounded-full cursor-pointer">
                                F
                            </div>
                        </Link>

                        <div class="relative transition-all duration-300 w-full max-w-xs"
                             :class="isMobileSearchActive ? 'absolute left-0 right-0 px-4 bg-white h-full flex items-center z-50' : 'hidden md:block'">
                            
                            <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" 
                               :class="isMobileSearchActive ? 'left-8' : 'left-3'"></i>
                            
                            <input 
                                ref="searchInputRef"
                                type="text" 
                                v-model="searchQuery"  @keydown.enter="handleSearch" placeholder="Cari Jasa atau Pengguna..."
                                class="bg-gray-100 border-none rounded-full py-2 text-sm w-full focus:ring-2 focus:ring-blue-500 focus:bg-white transition shadow-inner"
                                :class="isMobileSearchActive ? 'pl-10 pr-4' : 'pl-10 pr-4'"
                                @blur="closeMobileSearch"
                            >
                        </div>
                    </div>

                    <div class="hidden md:flex justify-center flex-1 space-x-1 h-full">
                        
                        <Link :href="route('dashboard')" 
                              class="relative group flex items-center justify-center h-full px-8 md:px-10 border-b-4 transition-all duration-200"
                              :class="routeActive('dashboard') ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-100 hover:rounded-lg'">
                            <i class="fas fa-home text-2xl mb-1"></i>
                            
                            <span class="absolute top-full mt-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap shadow-lg z-50">
                                Beranda
                                <span class="absolute -top-1 left-1/2 transform -translate-x-1/2 border-4 border-transparent border-b-gray-800"></span>
                            </span>
                        </Link>

                        <Link :href="route('marketplace.index')" 
                              class="relative group flex items-center justify-center h-full px-8 md:px-10 border-b-4 transition-all duration-200"
                              :class="routeActive('marketplace.index') ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-100 hover:rounded-lg'">
                            <i class="fas fa-store text-2xl mb-1"></i>
                            
                            <span class="absolute top-full mt-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap shadow-lg z-50">
                                Marketplace
                                <span class="absolute -top-1 left-1/2 transform -translate-x-1/2 border-4 border-transparent border-b-gray-800"></span>
                            </span>
                        </Link>

                        <Link :href="route('bookings.index')" 
                              class="relative group flex items-center justify-center h-full px-8 md:px-10 border-b-4 transition-all duration-200"
                              :class="routeActive('bookings.index') ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-100 hover:rounded-lg'">
                            <i class="fas fa-clipboard-list text-2xl mb-1"></i>
                            
                            <span class="absolute top-full mt-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap shadow-lg z-50">
                                Pesanan Saya
                                <span class="absolute -top-1 left-1/2 transform -translate-x-1/2 border-4 border-transparent border-b-gray-800"></span>
                            </span>
                        </Link>

                        <Link :href="route('profile.index')" 
                              class="relative group flex items-center justify-center h-full px-8 md:px-10 border-b-4 transition-all duration-200"
                              :class="routeActive('profile.index') ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-100 hover:rounded-lg'">
                            <i class="fas fa-user text-2xl mb-1"></i>
                            
                            <span class="absolute top-full mt-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap shadow-lg z-50">
                                Profil
                                <span class="absolute -top-1 left-1/2 transform -translate-x-1/2 border-4 border-transparent border-b-gray-800"></span>
                            </span>
                        </Link>

                    </div>

                    <div class="flex items-center justify-end w-auto md:w-1/3 lg:w-1/4 space-x-2 transition-opacity duration-200"
                            :class="isMobileSearchActive ? 'opacity-0 pointer-events-none' : 'opacity-100'">
                        
                        <button @click="toggleMobileSearch" class="md:hidden flex h-10 w-10 bg-gray-100 rounded-full items-center justify-center text-gray-600 hover:bg-gray-200">
                            <i class="fas fa-search"></i>
                        </button>

                        <template v-if="$page.props.auth.user">
                            
                            <Link :href="route('chats.index')" class="relative group flex h-10 w-10 bg-gray-100 rounded-full items-center justify-center hover:bg-gray-200 transition">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-6 text-black" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                                </svg>
                                
                                <span v-if="unreadMsgCount > 0" class="absolute top-0 right-0 h-4 w-4 bg-red-600 rounded-full text-[10px] text-white flex items-center justify-center border border-white font-bold">
                                    {{ unreadMsgCount > 99 ? '99+' : unreadMsgCount }}
                                </span>
                                
                                <span class="absolute top-full mt-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition duration-200 pointer-events-none z-50">Pesan</span>
                            </Link>

                            <button class="relative group flex h-10 w-10 bg-gray-100 rounded-full items-center justify-center hover:bg-gray-200 transition">
                                <i class="fas fa-bell text-black text-lg"></i>
                                
                                <span v-if="unreadNotifCount > 0" class="absolute top-0 right-0 h-4 w-4 bg-red-600 rounded-full text-[10px] text-white flex items-center justify-center border border-white font-bold">
                                    {{ unreadNotifCount }}
                                </span>

                                <span class="absolute top-full mt-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition duration-200 pointer-events-none z-50">Notifikasi</span>
                            </button>

                            <div class="hidden md:block ml-1 relative">
                                <Dropdown align="right" width="48">
                                    <template #trigger>
                                        <button type="button" class="flex items-center focus:outline-none group">
                                            <div class="h-10 w-10 rounded-full overflow-hidden border border-gray-300 hover:opacity-90 transition">
                                                <img :src="$page.props.auth.user.avatar ? '/storage/' + $page.props.auth.user.avatar : 'https://ui-avatars.com/api/?name=' + $page.props.auth.user.name + '&background=random'" alt="Avatar" class="h-full w-full object-cover">
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
                            </div>
                        </template>

                        <template v-else>
                            <div class="hidden md:flex items-center gap-2">
                                <Link :href="route('login')" class="px-4 py-2 text-sm font-bold text-gray-600 hover:text-gray-900">
                                    Masuk
                                </Link>
                                <Link :href="route('register')" class="px-4 py-2 text-sm font-bold text-white bg-blue-600 rounded-full hover:bg-blue-700 transition shadow-sm">
                                    Daftar
                                </Link>
                            </div>
                        </template>

                        <div class="-mr-2 flex items-center md:hidden">
                            <button @click="showingNavigationDropdown = !showingNavigationDropdown" class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none transition duration-150 ease-in-out">
                                <svg class="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                                    <path :class="{'hidden': showingNavigationDropdown, 'inline-flex': !showingNavigationDropdown }" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                                    <path :class="{'hidden': !showingNavigationDropdown, 'inline-flex': showingNavigationDropdown }" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div :class="{'block': showingNavigationDropdown, 'hidden': !showingNavigationDropdown}" class="md:hidden bg-white border-t border-gray-200">
    
                <div class="pt-2 pb-3 space-y-1">
                    <Link :href="route('dashboard')" class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition duration-150 ease-in-out" :class="routeActive('dashboard') ? 'border-blue-400 text-blue-700 bg-blue-50' : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'">
                        Beranda
                    </Link>
                    <Link :href="route('marketplace.index')" class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition duration-150 ease-in-out" :class="routeActive('marketplace.index') ? 'border-blue-400 text-blue-700 bg-blue-50' : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'">
                        Marketplace
                    </Link>
                    <Link v-if="$page.props.auth.user" :href="route('bookings.index')" class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition duration-150 ease-in-out" :class="routeActive('bookings.index') ? 'border-blue-400 text-blue-700 bg-blue-50' : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'">
                        Booking & Pesanan
                    </Link>
                </div>

                <div class="pt-4 pb-1 border-t border-gray-200">
                    
                    <template v-if="$page.props.auth.user">
                        <div class="px-4 flex items-center">
                            <div class="shrink-0">
                                    <img :src="$page.props.auth.user.avatar ? '/storage/' + $page.props.auth.user.avatar : 'https://ui-avatars.com/api/?name=' + $page.props.auth.user.name + '&background=random'" alt="Avatar" class="h-10 w-10 rounded-full object-cover">
                            </div>
                            <div class="ml-3">
                                <div class="font-medium text-base text-gray-800">{{ $page.props.auth.user.name }}</div>
                                <div class="font-medium text-sm text-gray-500">{{ $page.props.auth.user.email }}</div>
                            </div>
                        </div>

                        <div class="mt-3 space-y-1">
                            <Link :href="route('profile.index')" class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300 transition duration-150 ease-in-out">
                                Profil Saya
                            </Link>
                            <Link :href="route('profile.edit')" class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300 transition duration-150 ease-in-out">
                                Pengaturan Akun
                            </Link>
                            <Link :href="route('logout')" method="post" as="button" class="block w-full text-left pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300 transition duration-150 ease-in-out">
                                Log Out
                            </Link>
                        </div>
                    </template>

                    <template v-else>
                        <div class="mt-3 space-y-1 px-4">
                            <Link :href="route('login')" class="block w-full text-center px-4 py-2 bg-gray-100 text-gray-800 font-bold rounded-lg mb-2">
                                Masuk
                            </Link>
                            <Link :href="route('register')" class="block w-full text-center px-4 py-2 bg-blue-600 text-white font-bold rounded-lg">
                                Daftar Sekarang
                            </Link>
                        </div>
                    </template>

                </div>
            </div>
        </nav>

        <main class="pt-16">
            <slot />
        </main>
    </div>
</template>