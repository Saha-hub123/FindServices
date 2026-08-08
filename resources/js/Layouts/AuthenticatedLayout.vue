<script setup>
import { ref, nextTick, onMounted, computed, watch, onUnmounted } from 'vue';
import Dropdown from '@/Components/Dropdown.vue';
import FlashMessage from '@/Components/FlashMessage.vue'; // <--- Import Komponen Baru
import DropdownLink from '@/Components/DropdownLink.vue';
import { Link, usePage, router } from '@inertiajs/vue3';

const showingNavigationDropdown = ref(false);

// State untuk dropdown
const isNotificationOpen = ref(false);

const page = usePage();
const user = computed(() => page.props.auth.user);
const notifications = computed(() => page.props.auth.notifications || []);
const unreadCount = computed(() => page.props.auth.unread_notifications_count || 0);

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

// --- LOGIC REALTIME (POLLING) ---
let pollingInterval = null;

onMounted(() => {
    // Jalankan setiap 10 detik (10000ms)
    pollingInterval = setInterval(() => {
        // Hanya reload data 'auth' (yang berisi notifikasi) agar hemat bandwidth
        router.reload({
            only: ['auth'], 
            preserveScroll: true,
            preserveState: true, 
        });
    }, 10000); 
});

onUnmounted(() => {
    // Hentikan polling saat pindah halaman/komponen di-destroy
    if (pollingInterval) clearInterval(pollingInterval);
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

// Helper: Format Tanggal (Simple version)
const timeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Baru saja';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} menit yang lalu`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} jam yang lalu`;
    return `${Math.floor(diffInSeconds / 86400)} hari yang lalu`;
};

// Ganti fungsi lama dengan ini
const handleNotificationClick = (notification) => {
    // [FIX] Gunakan 'action_url' sesuai dengan yang dikirim dari Laravel Notification
    // Kita pakai '|| notification.data.link' untuk jaga-jaga kalau ada notif lama yang pakai key 'link'
    const targetUrl = notification.data.action_url || notification.data.link; 

    // Jika URL kosong, hentikan agar tidak error
    if (!targetUrl) return;

    // 1. Jika belum dibaca, tandai baca dulu di database via API
    if (!notification.read_at) {
        router.post(route('notifications.read', notification.id), {}, {
            preserveScroll: true,
            onSuccess: () => {
                // 2. Setelah sukses update status di DB, baru pindah halaman
                router.visit(targetUrl);
            }
        });
    } else {
        // 3. Jika SUDAH DIBACA, langsung pindah halaman (Konsep Anda Benar)
        router.visit(targetUrl);
    }
};

// Action: Tandai semua dibaca
const markAllRead = () => {
    router.post(route('notifications.readAll'), {}, { preserveScroll: true });
    isNotificationOpen.value = false;
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
                            <div class="bg-blue-600 text-white font-bold text-2xl h-10 w-10 flex items-center justify-center rounded-lg cursor-pointer">
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

                        <Link v-if="$page.props.auth.user && $page.props.auth.user.role === 'admin'"
                            :href="route('admin.dashboard')"
                            class="relative group flex items-center justify-center h-full px-8 md:px-10 border-b-4 transition-all duration-200"
                            :class="routeActive('admin.dashboard') ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-100 hover:rounded-lg'">

                            <div class="relative">
                                <i class="fas fa-user-shield text-2xl mb-1"></i>
                                <span v-if="$page.props.pending_reports_count > 0"
                                    class="absolute -top-1 -right-2 bg-red-500 text-white text-[10px] font-bold h-4 min-w-[16px] px-1 flex items-center justify-center rounded-full border-2 border-white shadow-sm">
                                    {{ $page.props.pending_reports_count }}
                                </span>
                            </div>

                            <span
                                class="absolute top-full mt-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap shadow-lg z-50">
                                Admin Panel
                                <span
                                    class="absolute -top-1 left-1/2 transform -translate-x-1/2 border-4 border-transparent border-b-gray-800"></span>
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

                            <button @click="isNotificationOpen = !isNotificationOpen"
                                class="relative group flex h-10 w-10 bg-gray-100 rounded-full items-center justify-center hover:bg-gray-200 transition focus:outline-none">
                                <i class="fas fa-bell text-black text-lg"
                                    :class="{ 'animate-swing': unreadCount > 0 }"></i>

                                <span v-if="unreadCount > 0"
                                    class="absolute top-0 right-0 h-4 w-4 bg-red-600 rounded-full text-[10px] text-white flex items-center justify-center border border-white font-bold animate-pulse-once">
                                    {{ unreadCount > 9 ? '9+' : unreadCount }}
                                </span>

                                <span
                                    class="absolute top-full mt-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition duration-200 pointer-events-none z-50 whitespace-nowrap shadow-lg">
                                    Notifikasi
                                </span>
                            </button>

                            <div v-if="isNotificationOpen" @click="isNotificationOpen = false"
                                class="fixed inset-0 z-40 cursor-default bg-transparent"></div>

                            <div v-if="isNotificationOpen"
                                class="absolute top-12 right-10 mt-3 w-80 sm:w-96 bg-white rounded-xl shadow-2xl ring-1 ring-black ring-opacity-5 z-50 overflow-hidden origin-top-right animate-fade-in-up border border-gray-100">

                                <div
                                    class="px-4 py-3 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                                    <h3 class="text-sm font-bold text-gray-800">Notifikasi</h3>
                                    <button v-if="unreadCount > 0" @click="markAllRead"
                                        class="text-xs text-blue-600 hover:text-blue-800 font-semibold hover:underline">
                                        Tandai semua dibaca
                                    </button>
                                </div>

                                <div class="max-h-[400px] overflow-y-auto custom-scrollbar">
                                    <div v-if="notifications.length > 0">
                                        <div v-for="notification in notifications" :key="notification.id"
                                            class="px-4 py-3 hover:bg-gray-50 transition border-b border-gray-50 last:border-0 cursor-pointer group/item relative"
                                            :class="{ 'bg-blue-50/60': !notification.read_at }"
                                            @click="handleNotificationClick(notification)">
                                            <div class="flex items-start gap-3">
                                                <div class="shrink-0 mt-0.5">
                                                    <div
                                                        class="h-8 w-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center border border-blue-200">
                                                        <i v-if="notification.data.icon_type === 'check'" class="fas fa-check-circle"></i>
                                                        <i v-else-if="notification.data.icon_type === 'cross'" class="fas fa-times-circle"></i>
                                                        <i v-else-if="notification.data.icon_type === 'tools'" class="fas fa-tools"></i>
                                                        <i v-else-if="notification.data.icon_type === 'clock'" class="fas fa-clock"></i>
                                                        <i v-else-if="notification.data.icon_type === 'file'" class="fas fa-file-alt"></i>
                                                        <i v-else class="fas fa-bell"></i>
                                                    </div>
                                                </div>

                                                <div class="flex-1 min-w-0">
                                                    <p class="text-sm text-gray-800 leading-snug line-clamp-2">
                                                        <span v-if="!notification.read_at"
                                                            class="inline-block w-1.5 h-1.5 bg-blue-600 rounded-full mr-1.5 mb-0.5 align-middle"></span>

                                                        <span
                                                            v-html="notification.data.message || 'Pemberitahuan baru'"></span>
                                                    </p>
                                                    <p class="text-[10px] text-gray-400 mt-1 font-medium">{{
                                                        timeAgo(notification.created_at) }}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div v-else class="py-12 text-center px-6">
                                        <div
                                            class="mx-auto h-12 w-12 bg-gray-50 rounded-full flex items-center justify-center mb-3 text-gray-300 border border-gray-100">
                                            <i class="far fa-bell-slash text-xl"></i>
                                        </div>
                                        <p class="text-gray-500 text-sm font-medium">Belum ada notifikasi.</p>
                                    </div>
                                </div>

                                <Link :href="route('notifications.index')"
                                    class="block bg-gray-50 py-3 text-center text-xs font-bold text-gray-600 hover:text-blue-600 hover:bg-gray-100 transition border-t border-gray-100 uppercase tracking-wide">
                                    Lihat Semua
                                </Link>
                            </div>

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
                                        <div class="px-4 py-3 border-b border-gray-100 bg-gray-50/50">
                                            <div class="font-bold text-gray-800 leading-tight truncate">{{ $page.props.auth.user.name }}</div>
                                            <div class="text-xs text-gray-500 font-medium truncate">{{ $page.props.auth.user.email }}</div>
                                        </div>

                                        <div v-if="$page.props.auth.user && $page.props.auth.user.role === 'admin'" class="border-b border-gray-100">
                                            <DropdownLink :href="route('admin.dashboard')">
                                                <div class="flex items-center justify-between w-full">
                                                    <div class="flex items-center">
                                                        <i class="fas fa-user-shield w-5 text-center mr-2 text-gray-400"></i>
                                                        Panel Admin
                                                    </div>
                                                    <span v-if="$page.props.pending_reports_count > 0"
                                                        class="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full shadow-sm">
                                                        {{ $page.props.pending_reports_count }}
                                                    </span>
                                                </div>
                                            </DropdownLink>
                                        </div>

                                        <div class="py-1">
                                            <DropdownLink :href="route('profile.index')">
                                                <div class="flex items-center">
                                                    <i class="fas fa-user w-5 text-center mr-2 text-gray-400"></i>
                                                    Profil Saya
                                                </div>
                                            </DropdownLink>
                                            
                                            </div>

                                        <div class="border-t border-gray-100"></div>

                                        <div class="py-1">
                                            <DropdownLink :href="route('user.reports.index')">
                                                <div class="flex items-center">
                                                    <i class="fas fa-life-ring w-5 text-center mr-2 text-gray-400"></i>
                                                    Pusat Bantuan
                                                </div>
                                            </DropdownLink>
                                        </div>

                                        <div class="border-t border-gray-100"></div>

                                        <div class="py-1">
                                            <DropdownLink :href="route('profile.edit')">
                                                <div class="flex items-center">
                                                    <i class="fas fa-cog w-5 text-center mr-2 text-gray-400"></i>
                                                    Pengaturan Akun
                                                </div>
                                            </DropdownLink>

                                            <DropdownLink :href="route('logout')" method="post" as="button" class="text-red-600 hover:bg-red-50">
                                                <div class="flex items-center w-full">
                                                    <i class="fas fa-sign-out-alt w-5 text-center mr-2 text-red-500"></i>
                                                    Log Out
                                                </div>
                                            </DropdownLink>
                                        </div>
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
    
                <div :class="{ 'block': showingNavigationDropdown, 'hidden': !showingNavigationDropdown }"
                    class="md:hidden bg-white border-t border-gray-200 absolute top-16 left-0 w-full shadow-lg z-40 animate-fade-in-up">

                    <template v-if="$page.props.auth.user">

                        <div class="pt-4 pb-2 border-b border-gray-100 bg-gray-50">
                            <div class="px-4 flex items-center">
                                <div class="shrink-0">
                                    <img :src="$page.props.auth.user.avatar ? '/storage/' + $page.props.auth.user.avatar : 'https://ui-avatars.com/api/?name=' + $page.props.auth.user.name + '&background=random'"
                                        alt="Avatar" class="h-10 w-10 rounded-full object-cover border border-gray-300">
                                </div>
                                <div class="ml-3">
                                    <div class="font-bold text-base text-gray-800">{{ $page.props.auth.user.name }}
                                    </div>
                                    <div class="font-medium text-sm text-gray-500">{{ $page.props.auth.user.email }}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="pt-2 pb-3 space-y-1">

                            <Link v-if="$page.props.auth.user.role === 'admin'" :href="route('admin.dashboard')"
                                class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300 transition duration-150 ease-in-out">
                                <div class="flex items-center">
                                    <i class="fas fa-user-shield w-6 text-center mr-2 text-gray-400"></i>
                                    Panel Admin
                                </div>
                            </Link>

                            <Link :href="route('profile.index')"
                                class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300 transition duration-150 ease-in-out">
                                <div class="flex items-center">
                                    <i class="fas fa-user w-6 text-center mr-2 text-gray-400"></i>
                                    Profil Saya
                                </div>
                            </Link>

                            <Link :href="route('user.reports.index')"
                                class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300 transition duration-150 ease-in-out">
                                <div class="flex items-center">
                                    <i class="fas fa-life-ring w-6 text-center mr-2 text-gray-400"></i>
                                    Pusat Bantuan
                                </div>
                            </Link>

                            <Link :href="route('profile.edit')"
                                class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300 transition duration-150 ease-in-out">
                                <div class="flex items-center">
                                    <i class="fas fa-cog w-6 text-center mr-2 text-gray-400"></i>
                                    Pengaturan Akun
                                </div>
                            </Link>

                            <div class="border-t border-gray-100 mt-2 pt-2">
                                <Link :href="route('logout')" method="post" as="button"
                                    class="block w-full text-left pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-red-600 hover:bg-red-50 hover:border-red-300 transition duration-150 ease-in-out">
                                    <div class="flex items-center">
                                        <i class="fas fa-sign-out-alt w-6 text-center mr-2"></i>
                                        Log Out
                                    </div>
                                </Link>
                            </div>
                        </div>
                    </template>

                    <template v-else>
                        <div class="p-4 space-y-3 bg-gray-50">
                            <p class="text-center text-sm text-gray-500 mb-2">Silakan masuk untuk mengakses fitur
                                lengkap.</p>

                            <Link :href="route('login')"
                                class="block w-full text-center px-4 py-3 bg-white border border-gray-300 text-gray-800 font-bold rounded-xl shadow-sm hover:bg-gray-50">
                                Masuk
                            </Link>
                            <Link :href="route('register')"
                                class="block w-full text-center px-4 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-lg shadow-blue-200 hover:bg-blue-700">
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
        <div class="fixed bottom-0 left-0 z-50 w-full h-16 bg-white border-t border-gray-200 md:hidden pb-safe">
            <div class="grid h-full max-w-lg grid-cols-4 mx-auto font-medium">
                
                <Link :href="route('dashboard')" 
                    class="inline-flex flex-col items-center justify-center px-5 hover:bg-gray-50 group"
                    :class="routeActive('dashboard') ? 'text-blue-600' : 'text-gray-500'">
                    <i class="fas fa-home text-lg mb-1 group-hover:text-blue-600"></i>
                    <span class="text-[10px]">Beranda</span>
                </Link>

                <Link :href="route('marketplace.index')" 
                    class="inline-flex flex-col items-center justify-center px-5 hover:bg-gray-50 group"
                    :class="routeActive('marketplace.index') ? 'text-blue-600' : 'text-gray-500'">
                    <i class="fas fa-store text-lg mb-1 group-hover:text-blue-600"></i>
                    <span class="text-[10px]">Jasa</span>
                </Link>

                <Link :href="route('bookings.index')" 
                    class="inline-flex flex-col items-center justify-center px-5 hover:bg-gray-50 group"
                    :class="routeActive('bookings.index') ? 'text-blue-600' : 'text-gray-500'">
                    <i class="fas fa-clipboard-list text-lg mb-1 group-hover:text-blue-600"></i>
                    <span class="text-[10px]">Pesanan</span>
                </Link>

                <Link :href="route('profile.index')" 
                    class="inline-flex flex-col items-center justify-center px-5 hover:bg-gray-50 group"
                    :class="routeActive('profile.index') ? 'text-blue-600' : 'text-gray-500'">
                    <i class="fas fa-user text-lg mb-1 group-hover:text-blue-600"></i>
                    <span class="text-[10px]">Profil</span>
                </Link>
            </div>
        </div>
    </div>
    <Teleport to="body">
        <FlashMessage />
    </Teleport>
</template>
<style scoped>
/* Scrollbar Halus */
.custom-scrollbar::-webkit-scrollbar {
    width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e5e7eb;
    border-radius: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #d1d5db;
}

/* Animasi Masuk Dropdown */
.animate-fade-in-up {
    animation: fadeInUp 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px) scale(0.98);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* Animasi Lonceng (Swing) */
.animate-swing {
    animation: swing 2s infinite ease-in-out; 
    transform-origin: top center;
}
@keyframes swing {
    0%, 100% { transform: rotate(0deg); }
    20% { transform: rotate(15deg); }
    40% { transform: rotate(-10deg); }
    60% { transform: rotate(5deg); }
    80% { transform: rotate(-5deg); }
}

/* Animasi Badge (Pulse Sekali saat load) */
.animate-pulse-once {
    animation: pulse 1s ease-in-out;
}
/* Support untuk iPhone X ke atas (Area Poni/Home Indicator) */
.pb-safe {
    padding-bottom: env(safe-area-inset-bottom);
}
</style>