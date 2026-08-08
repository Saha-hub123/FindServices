<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, router } from '@inertiajs/vue3';
import { ref, onMounted } from 'vue';
import axios from 'axios'; // Wajib import axios untuk load more

const props = defineProps({
    notifications: Object, // Data awal dari Inertia
});

// --- STATE UNTUK LOAD MORE ---
// Kita tampung data di ref lokal agar bisa di-push (append)
const allNotifications = ref(props.notifications.data || []);
const nextUrl = ref(props.notifications.next_page_url);
const isLoadingMore = ref(false);

// Helper Waktu
const timeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    if (diffInSeconds < 60) return 'Baru saja';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} menit yang lalu`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} jam yang lalu`;
    return `${Math.floor(diffInSeconds / 86400)} hari yang lalu`;
};

const handleNotificationClick = (notification) => {
    // [FIX] Ambil action_url
    const targetUrl = notification.data.action_url || notification.data.link;

    if (!targetUrl) return;

    // 1. Jika belum dibaca
    if (!notification.read_at) {
        router.post(route('notifications.read', notification.id), {}, {
            preserveScroll: true,
            onSuccess: () => {
                // Update tampilan lokal biar langsung jadi 'read' tanpa refresh
                notification.read_at = new Date().toISOString(); 
                
                // Pindah halaman
                router.visit(targetUrl);
            }
        });
    } else {
        // 2. Jika sudah dibaca (tetap bisa diklik)
        router.visit(targetUrl);
    }
};

const deleteNotification = (id) => {
    if(confirm('Hapus notifikasi ini?')) {
        router.delete(route('notifications.destroy', id), { 
            preserveScroll: true,
            onSuccess: () => {
                // Hapus dari list lokal
                allNotifications.value = allNotifications.value.filter(n => n.id !== id);
            }
        });
    }
};

const markAllRead = () => {
    if(confirm('Tandai semua sebagai sudah dibaca?')) {
        router.post(route('notifications.readAll'), {}, {
            onSuccess: () => {
                // Update semua list lokal jadi read
                allNotifications.value.forEach(n => n.read_at = new Date().toISOString());
            }
        });
    }
};

// --- FUNGSI LOAD MORE ---
const loadMore = async () => {
    if (!nextUrl.value || isLoadingMore.value) return;

    isLoadingMore.value = true;

    try {
        // Request ke URL halaman selanjutnya (misal: /notifications?page=2)
        const response = await axios.get(nextUrl.value);
        
        // 1. Masukkan data baru ke list yang sudah ada (Append)
        const newItems = response.data.data;
        allNotifications.value.push(...newItems);

        // 2. Update link halaman selanjutnya
        nextUrl.value = response.data.next_page_url;

    } catch (error) {
        console.error("Gagal memuat notifikasi:", error);
    } finally {
        isLoadingMore.value = false;
    }
};
</script>

<template>
    <Head title="Notifikasi" />

    <AuthenticatedLayout>
        <div class="py-12">
            <div class="max-w-2xl mx-auto sm:px-6 lg:px-8 lg:mb-0 mb-5">
                
                <div class="flex items-center justify-between mb-6 px-4 sm:px-0">
                    <h2 class="text-2xl font-bold text-gray-800">Notifikasi Anda</h2>
                    <button 
                        v-if="allNotifications.length > 0"
                        @click="markAllRead" 
                        class="text-sm font-medium text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-4 py-2 rounded-lg transition"
                    >
                        <i class="fas fa-check mr-1"></i> Baca Semua
                    </button>
                </div>

                <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    
                    <div v-if="allNotifications.length > 0">
                        <div v-for="notification in allNotifications" :key="notification.id" 
                             class="group relative border-b border-gray-100 last:border-0 p-5 hover:bg-gray-50 transition duration-200"
                             :class="{'bg-blue-50/30': !notification.read_at}"
                        >
                            <div class="flex gap-4">
                                <div class="shrink-0">
                                    <div class="h-10 w-10 rounded-full flex items-center justify-center text-lg shadow-sm border"
                                         :class="notification.read_at ? 'bg-gray-100 text-gray-500 border-gray-200' : 'bg-blue-100 text-blue-600 border-blue-200'">
                                        
                                        <i v-if="notification.data.icon_type === 'check'" class="fas fa-check-circle"></i>
                                        <i v-else-if="notification.data.icon_type === 'cross'" class="fas fa-times-circle"></i>
                                        <i v-else-if="notification.data.icon_type === 'tools'" class="fas fa-tools"></i>
                                        <i v-else-if="notification.data.icon_type === 'clock'" class="fas fa-clock"></i>
                                        <i v-else-if="notification.data.icon_type === 'file'" class="fas fa-file-alt"></i>
                                        <i v-else class="fas fa-bell"></i>
                                    </div>
                                </div>

                                <div class="flex-1 cursor-pointer" @click="handleNotificationClick(notification)">
                                    <p class="text-gray-800 text-sm leading-relaxed mb-1">
                                        <span v-html="notification.data.message || 'Pemberitahuan baru'"></span>
                                        <span v-if="!notification.read_at" class="inline-block w-2 h-2 bg-blue-500 rounded-full ml-2 align-middle animate-pulse"></span>
                                    </p>
                                    <p class="text-xs text-gray-400 font-medium">{{ timeAgo(notification.created_at) }}</p>
                                </div>

                                <div class="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button @click.stop="deleteNotification(notification.id)" 
                                            class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full transition"
                                            title="Hapus Notifikasi">
                                        <i class="fas fa-trash-alt"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-else class="py-16 text-center flex flex-col items-center">
                        <div class="h-20 w-20 bg-gray-50 rounded-full flex items-center justify-center mb-4 text-gray-300">
                            <i class="far fa-bell-slash text-4xl"></i>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900">Tidak ada notifikasi</h3>
                        <p class="text-gray-500 text-sm max-w-xs mx-auto">Semua pemberitahuan tentang aktivitas akun Anda akan muncul di sini.</p>
                    </div>

                </div>

                <div v-if="nextUrl" class="mt-6 flex justify-center pb-8">
                    <button 
                        @click="loadMore" 
                        :disabled="isLoadingMore"
                        class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-full font-bold shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-70 transition-all flex items-center gap-2 text-sm"
                    >
                        <span v-if="isLoadingMore"><i class="fas fa-spinner fa-spin"></i> Memuat...</span>
                        <span v-else>Muat Lebih Banyak <i class="fas fa-chevron-down ml-1"></i></span>
                    </button>
                </div>

            </div>
        </div>
    </AuthenticatedLayout>
</template>