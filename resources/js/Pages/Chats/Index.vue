<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, useForm, router } from '@inertiajs/vue3';
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue';

const props = defineProps({
    conversations: Array,
    activeChat: Object,
    messages: Array,
    targetService: Object,
    targetBooking: Object,
    auth_id: Number
});

// State Lokal
const localConversations = ref([...props.conversations]);
const onlineUsers = ref([]);
const messagesContainer = ref(null);
const messageInput = ref(null);
const replyingTo = ref(null);
const isContextHidden = ref(false);
const searchQuery = ref('');

// Computed Filter
const filteredConversations = computed(() => {
    if (!searchQuery.value) return localConversations.value;
    return localConversations.value.filter(user => 
        user.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
});

// State Header
const activeContextBooking = ref(props.targetBooking);
const activeContextService = ref(props.targetService);

const form = useForm({
    receiver_id: props.activeChat ? props.activeChat.id : null,
    message: '',
    service_id: props.targetService ? props.targetService.id : null,
    booking_id: props.targetBooking ? props.targetBooking.id : null,
    reply_to_id: null
});

// --- HELPER BARU: UPDATE SIDEBAR ---
const updateConversationList = (userId, newMessageObj, incrementUnread = false) => {
    // 1. Cari index user di list percakapan
    const index = localConversations.value.findIndex(c => c.id === userId);

    if (index !== -1) {
        // Ambil datanya
        const conv = localConversations.value[index];
        
        // 2. Update Pesan Terakhir
        conv.last_message = newMessageObj;

        // 3. Tambah Counter (Jika perlu)
        if (incrementUnread) {
            conv.unread_count = (conv.unread_count || 0) + 1;
        }

        // 4. Pindahkan ke Paling Atas (Reordering)
        localConversations.value.splice(index, 1); // Hapus dari posisi lama
        localConversations.value.unshift(conv);    // Masukkan ke posisi 0
    }
};
// -----------------------------------

// Watcher Ganti Chat
watch(() => props.activeChat, (newChat) => {
    if (newChat) {
        form.receiver_id = newChat.id;
        form.message = '';
        cancelReply();
        activeContextBooking.value = props.targetBooking;
        activeContextService.value = props.targetService;
        isContextHidden.value = false;
        form.booking_id = props.targetBooking ? props.targetBooking.id : null;
        form.service_id = props.targetService ? props.targetService.id : null;
        
        // Reset Unread Count saat dibuka
        const conversation = localConversations.value.find(c => c.id === newChat.id);
        if (conversation) conversation.unread_count = 0;

        // GANTI scrollToBottom() DENGAN INI:
        jumpToUnread(); 
    }
});

watch(() => props.messages, () => { scrollToBottom(); }, { deep: true });

onMounted(() => {
    jumpToUnread();

    if (window.Echo) {
        window.Echo.join('online')
            .here((users) => { onlineUsers.value = users.map(u => u.id); })
            .joining((user) => { onlineUsers.value.push(user.id); })
            .leaving((user) => { onlineUsers.value = onlineUsers.value.filter(id => id !== user.id); });

        window.Echo.private(`chat.${props.auth_id}`)
            .listen('MessageSent', (e) => {
                // Skenario: Pesan Masuk dari Orang Lain
                if (props.activeChat && e.chat.sender_id === props.activeChat.id) {
                    props.messages.push(e.chat);
                    // Update sidebar tanpa nambah unread (sedang dibuka)
                    axios.post(route('chats.markAsRead'), {
                        sender_id: e.chat.sender_id
                    });
                } else {
                    // Update sidebar DAN tambah unread
                    updateConversationList(e.chat.sender_id, e.chat, true);
                }
            })
            .listen('MessageRead', (e) => {
                console.log("Pesan dibaca oleh:", e.reader_id);

                // Jika orang yang membaca adalah orang yang sedang kita buka chatnya
                if (props.activeChat && e.reader_id === props.activeChat.id) {
                    
                    // Loop semua pesan di layar
                    props.messages.forEach((msg) => {
                        // Jika pesan itu buatan saya (Auth ID) dan statusnya belum read
                        if (msg.sender_id === props.auth_id && !msg.is_read) {
                            msg.is_read = true; // Ubah jadi true (Centang Biru)
                        }
                    });
                }
            })
            .listen('MessageDeleted', (e) => {
                // Cari pesan di layar dan tandai sebagai terhapus
                const msg = props.messages.find(m => m.id === e.chatId);
                if (msg) {
                    msg.deleted_at = new Date().toISOString(); // Isi deleted_at agar UI berubah
                }
            });
            
    }
});

onUnmounted(() => {
    if (window.Echo) {
        window.Echo.leave(`chat.${props.auth_id}`);
        window.Echo.leave('online');
    }
});

const sendMessage = () => {
    // Simpan pesan teks sementara sebelum direset formnya
    const tempMessage = form.message; 
    const receiverId = props.activeChat.id;

    // Simpan konteks URL
    const sentBookingId = form.booking_id;
    const sentServiceId = form.service_id;

    form.post(route('chats.store'), {
        preserveScroll: true,
        onSuccess: () => {
            form.message = '';
            cancelReply();
            
            // --- UPDATE SIDEBAR (PENGIRIM) ---
            // Kita update manual agar langsung berubah tanpa nunggu refresh
            updateConversationList(receiverId, {
                message: tempMessage,
                created_at: new Date().toISOString(), // Waktu sekarang
                sender_id: props.auth_id,
                is_read: false
            }, false);
            // --------------------------------

            if (sentBookingId) {
                updateUrlSilent(sentBookingId, null);
                activeContextBooking.value = props.messages.find(m => m.booking_id == sentBookingId)?.booking;
                isContextHidden.value = false;
                form.booking_id = sentBookingId;
            } else if (sentServiceId) {
                updateUrlSilent(null, sentServiceId);
                activeContextService.value = props.messages.find(m => m.service_id == sentServiceId)?.service;
                isContextHidden.value = false;
                form.service_id = sentServiceId;
            } else {
                cancelReply();
            }
        }
    });
};

const openChat = (userId) => {
    // Reset Unread count saat diklik
    const index = localConversations.value.findIndex(c => c.id === userId);
    if(index !== -1) localConversations.value[index].unread_count = 0;

    router.get(route('chats.index'), { user_id: userId }, { preserveState: true, replace: true });
};

// ... (Sisa fungsi handleReply, cancelReply, updateUrlSilent, formatTime, dll TETAP SAMA) ...
// Copy paste saja fungsi-fungsi di bawah ini dari kode sebelumnya

const handleReply = (msg) => {
    replyingTo.value = msg;
    form.reply_to_id = msg.id;
    isContextHidden.value = false;
    if (msg.booking) {
        form.booking_id = msg.booking.id;
        form.service_id = null;
        activeContextBooking.value = msg.booking;
        activeContextService.value = null;
        updateUrlSilent(msg.booking.id, null);
    } else if (msg.service) {
        form.service_id = msg.service.id;
        form.booking_id = null;
        activeContextService.value = msg.service;
        activeContextBooking.value = null;
        updateUrlSilent(null, msg.service.id);
    } else {
        form.service_id = null;
        form.booking_id = null;
    }
    nextTick(() => messageInput.value.focus());
};

const cancelReply = () => {
    replyingTo.value = null;
    form.reply_to_id = null;
    form.booking_id = null;
    form.service_id = null;
    activeContextBooking.value = null;
    activeContextService.value = null;
    isContextHidden.value = true;
    updateUrlSilent(null, null);
};

const clearContext = () => {
    isContextHidden.value = true;
    form.service_id = null;
    form.booking_id = null;
    activeContextBooking.value = null;
    activeContextService.value = null;
    updateUrlSilent(null, null);
};

const updateUrlSilent = (bookingId, serviceId) => {
    const url = new URL(window.location.href);
    url.searchParams.delete('booking_id');
    url.searchParams.delete('service_id');
    if (bookingId) url.searchParams.set('booking_id', bookingId);
    if (serviceId) url.searchParams.set('service_id', serviceId);
    window.history.replaceState({}, '', url);
};

const scrollToBottom = async () => {
    await nextTick();
    if (messagesContainer.value) {
        messagesContainer.value.scrollTo({ top: messagesContainer.value.scrollHeight, behavior: 'smooth' });
    }
};

const formatTime = (dateString) => new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
const getStatusClass = (status) => {
    switch(status) {
        case 'unpaid': return 'bg-gray-200 text-gray-800';
        case 'pending': return 'bg-yellow-100 text-yellow-800';
        case 'confirmed': return 'bg-blue-100 text-blue-800';
        case 'in_progress': return 'bg-purple-100 text-purple-800';
        case 'completed': return 'bg-green-600 text-white';
        case 'cancelled': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
};
const getStatusLabel = (status) => status;
const isUserOnline = (userId) => onlineUsers.value.includes(userId);

// Fungsi untuk loncat ke pesan belum dibaca (Tanpa Animasi)
const jumpToUnread = async () => {
    await nextTick(); // Tunggu render HTML selesai

    if (!messagesContainer.value) return;

    // 1. Cari pesan pertama yang: 
    //    - Bukan punya saya (sender_id !== auth_id)
    //    - Belum dibaca (!is_read)
    const firstUnread = props.messages.find(m => m.sender_id !== props.auth_id && !m.is_read);

    if (firstUnread) {
        // 2. Jika ada, cari elemen HTML-nya berdasarkan ID
        const element = document.getElementById(`msg-${firstUnread.id}`);
        
        if (element) {
            // 3. Scroll element tersebut ke tengah layar secara INSTAN (auto)
            element.scrollIntoView({ behavior: 'auto', block: 'center' });
        }
    } else {
        // 4. Jika semua sudah terbaca, langsung ke paling bawah (Tanpa Animasi)
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
};

const deleteMessage = (msgId) => {
    if (confirm('Hapus pesan ini?')) {
        // Hapus secara Optimistic UI (Langsung ubah tampilan biar cepat)
        const msgIndex = props.messages.findIndex(m => m.id === msgId);
        if (msgIndex !== -1) {
            props.messages[msgIndex].deleted_at = new Date().toISOString();
        }

        // Request ke server
        router.delete(route('chats.destroy', msgId), { 
            preserveScroll: true 
        });
    }
};
</script>

<template>
    <Head title="Pesan" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                
                <div class="flex flex-col md:flex-row gap-6 h-[calc(100vh-140px)]"> 
                    
                    <div class="w-full md:w-1/3 lg:w-1/4 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden"
                         :class="activeChat ? 'hidden md:flex' : 'flex'">
                        
                        <div class="p-4 border-b border-gray-100 flex-shrink-0">
                            <h2 class="font-bold text-lg text-gray-800 mb-3">Percakapan</h2>
                            <div class="relative">
                                <i class="fas fa-search absolute left-3 top-3 text-gray-400"></i>
                                <input v-model="searchQuery" type="text" placeholder="Cari kontak..." class="w-full bg-gray-50 border border-gray-200 rounded-full py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition">
                            </div>
                        </div>

                        <div class="flex-1 overflow-y-auto custom-scrollbar">
                            <div v-if="filteredConversations.length === 0" class="p-8 text-center text-gray-400 text-sm flex flex-col items-center">
                                <i class="fas fa-inbox text-3xl mb-2 opacity-50"></i>
                                <p>Belum ada percakapan.</p>
                            </div>

                            <div v-for="user in filteredConversations" :key="user.id" 
                                @click="openChat(user.id)"
                                class="flex items-center p-3 cursor-pointer hover:bg-gray-50 transition relative border-b border-gray-50 last:border-0"
                                :class="activeChat && activeChat.id === user.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : 'border-l-4 border-l-transparent'">
                                
                                <div class="relative">
                                    <img :src="user.avatar ? '/storage/' + user.avatar : 'https://ui-avatars.com/api/?name=' + user.name" 
                                        class="h-10 w-10 rounded-full shadow-sm object-cover" 
                                        alt="Avatar">
                                    
                                    <span v-if="isUserOnline(user.id)" 
                                          class="absolute bottom-0 right-0 block h-3 w-3 rounded-full ring-2 ring-white bg-green-500 shadow-sm animate-pulse">
                                    </span>
                                </div>
                                
                                <div class="ml-3 flex-1 overflow-hidden pr-2">
                                    <div class="flex justify-between items-baseline mb-0.5">
                                        <h3 class="text-sm font-semibold truncate" :class="user.unread_count > 0 ? 'text-black font-bold' : 'text-gray-900'">{{ user.name }}</h3>
                                        <span v-if="user.last_message" class="text-[10px]" :class="user.unread_count > 0 ? 'text-blue-600 font-bold' : 'text-gray-400'">
                                            {{ formatTime(user.last_message.created_at) }}
                                        </span>
                                    </div>
                                    <p v-if="user.last_message" class="text-xs truncate" :class="user.unread_count > 0 ? 'font-bold text-gray-800' : 'text-gray-500'">
                                        <span v-if="user.last_message.sender_id === auth_id">Anda: </span>
                                        {{ user.last_message.message }}
                                    </p>
                                </div>

                                <div v-if="user.unread_count > 0" class="absolute right-3 top-2/3 transform -translate-y-1/2 bg-red-600 min-w-[1.25rem] h-5 px-1 rounded-full flex items-center justify-center shadow-sm">
                                    <span class="text-[10px] text-white font-bold">{{ user.unread_count }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden" v-if="activeChat">
                        
                        <div class="p-3 px-4 border-b border-gray-100 flex items-center justify-between bg-white z-10">
                            <div class="flex items-center group">
                                <Link :href="route('chats.index')" class="md:hidden mr-3 text-gray-500"><i class="fas fa-arrow-left text-lg"></i></Link>
                                <div class="relative">
                                    <Link :href="route('profile.show', activeChat.id)" class="relative cursor-pointer">
                                        <img :src="activeChat.avatar ? '/storage/' + activeChat.avatar : 'https://ui-avatars.com/api/?name=' + activeChat.name" class="h-10 w-10 rounded-full group-hover:opacity-80 transition object-cover group-hover:ring-4 group-hover:ring-blue-100" alt="Avatar">
                                        <span v-if="isUserOnline(activeChat.id)" class="absolute bottom-0 right-0 block h-2.5 w-2.5 rounded-full ring-2 ring-white bg-green-500"></span>
                                    </Link>
                                    <span v-if="isUserOnline(activeChat.id)" class="absolute bottom-0 right-0 block h-2.5 w-2.5 rounded-full ring-2 ring-white bg-green-500"></span>
                                </div>
                                <div class="ml-3">
                                    <h3 class="font-bold text-gray-800 text-sm">
                                        <Link :href="route('profile.show', activeChat.id)" class="group-hover:underline transition group-hover:text-gray-600">
                                            {{ activeChat.name }}
                                        </Link>
                                    </h3>
                                    
                                    <p v-if="isUserOnline(activeChat.id)" class="text-xs text-green-600 font-bold flex items-center">
                                        • Online
                                    </p>
                                    <p v-else class="text-xs text-gray-400">Offline</p>
                                </div>
                            </div>
                            <button class="text-gray-400 hover:text-gray-600 p-2"><i class="fas fa-ellipsis-v"></i></button>
                        </div>

                        <div v-if="activeContextBooking && !isContextHidden" class="bg-blue-50/80 backdrop-blur-sm p-3 flex items-center border-b border-blue-100 justify-between animate-fade-in">
                            <div class="flex items-center overflow-hidden">
                                <img v-if="activeContextBooking.service?.galleries?.[0]" :src="'/storage/' + activeContextBooking.service.galleries[0].image" class="h-10 w-10 rounded object-cover border border-blue-200 mr-3 bg-white shrink-0">
                                <div class="min-w-0">
                                    <div class="flex items-center space-x-2">
                                        <p class="text-[10px] text-blue-600 font-bold uppercase">Booking #{{ activeContextBooking.id }}</p>
                                        <span class="px-1.5 py-0.5 rounded-full text-[9px] font-bold uppercase" :class="getStatusClass(activeContextBooking.status)">{{ getStatusLabel(activeContextBooking.status) }}</span>
                                    </div>
                                    <h4 class="font-bold text-gray-800 text-xs truncate">{{ activeContextBooking.service?.title ?? 'Jasa Tidak Ditemukan' }}</h4>
                                </div>
                            </div>
                            <div class="flex items-center space-x-1 shrink-0 ml-2">
                                <Link :href="route('bookings.show', activeContextBooking.id)" class="text-xs bg-white border border-blue-300 text-blue-700 px-2 py-1 rounded shadow-sm hover:bg-blue-50">Detail</Link>
                                <button @click="clearContext" class="text-gray-400 hover:text-red-500 p-1"><i class="fas fa-times"></i></button>
                            </div>
                        </div>

                        <div v-else-if="activeContextService && !isContextHidden" class="bg-blue-50/80 backdrop-blur-sm p-3 flex items-center border-b border-blue-100 justify-between animate-fade-in">
                            <div class="flex items-center overflow-hidden">
                                <img v-if="activeContextService.galleries?.[0]" :src="'/storage/' + activeContextService.galleries[0].image" class="h-10 w-10 rounded object-cover border border-blue-200 mr-3 shrink-0">
                                <div class="min-w-0">
                                    <p class="text-[10px] text-blue-600 font-bold uppercase">Membahas Jasa</p>
                                    <h4 class="font-bold text-gray-800 text-xs truncate">{{ activeContextService.title }}</h4>
                                </div>
                            </div>
                            <div class="flex items-center space-x-1 shrink-0 ml-2">
                                <Link :href="route('service.show', activeContextService.id)" class="text-xs bg-white border border-blue-200 text-blue-600 px-2 py-1 rounded hover:bg-blue-50">Lihat</Link>
                                <button @click="clearContext" class="text-gray-400 hover:text-red-500 p-1"><i class="fas fa-times"></i></button>
                            </div>
                        </div>

                        <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50 custom-scrollbar" ref="messagesContainer">
                            <div v-for="msg in messages" :key="msg.id" :id="'msg-' + msg.id" class="flex w-full group relative" :class="msg.sender_id === auth_id ? 'justify-end' : 'justify-start'">
                                
                                <div class="flex flex-col gap-1 justify-center mx-2 opacity-0 group-hover:opacity-100 transition-opacity" 
                                    :class="msg.sender_id === auth_id ? 'order-first items-end' : 'order-last items-start'">
                                    
                                    <button v-if="!msg.deleted_at" @click="handleReply(msg)" class="bg-white hover:bg-blue-50 text-gray-400 hover:text-blue-500 shadow-sm border border-gray-200 rounded-full h-7 w-7 flex items-center justify-center text-xs transition" title="Balas">
                                        <i class="fas fa-reply"></i>
                                    </button>

                                    <button v-if="msg.sender_id === auth_id && !msg.deleted_at" @click="deleteMessage(msg.id)" class="bg-white hover:bg-red-50 text-gray-400 hover:text-red-500 shadow-sm border border-gray-200 rounded-full h-7 w-7 flex items-center justify-center text-xs transition" title="Hapus">
                                        <i class="fas fa-trash-alt"></i>
                                    </button>
                                </div>

                                <div class="max-w-[75%] flex flex-col">
                                    <div class="px-3 py-2 rounded-2xl shadow-sm text-sm relative border"
                                        :class="[
                                            msg.deleted_at 
                                                ? 'bg-gray-100 border-gray-200 text-gray-500 italic' // Style jika dihapus
                                                : (msg.sender_id === auth_id ? 'bg-blue-600 text-white border-blue-600 rounded-br-none' : 'bg-white text-gray-800 border-gray-200 rounded-bl-none') // Style normal
                                        ]">
                                        
                                        <div v-if="msg.deleted_at" class="flex items-center gap-2 py-1">
                                            <i class="fas fa-ban text-xs opacity-50"></i>
                                            <span>Pesan telah dihapus</span>
                                        </div>

                                        <div v-else>
                                            <div v-if="msg.reply_to" class="mb-1.5 p-1.5 rounded text-xs border-l-2 cursor-pointer bg-opacity-20" :class="msg.sender_id === auth_id ? 'bg-black border-white/50 text-blue-100' : 'bg-gray-100 border-blue-500 text-gray-600'">
                                                <p class="font-bold mb-0.5 text-[9px] uppercase opacity-80">{{ msg.reply_to.sender_id === auth_id ? 'Anda' : activeChat.name }}</p>
                                                <p class="line-clamp-1 opacity-90">
                                                    {{ msg.reply_to.deleted_at ? '🚫 Pesan dihapus' : msg.reply_to.message }}
                                                </p>
                                            </div>

                                            <div v-if="msg.booking" @click="router.visit(route('bookings.show', msg.booking.id))" class="bg-white/90 p-2 mb-2 rounded text-gray-800 cursor-pointer border-l-4 border-yellow-400 shadow-sm transition hover:bg-white" :class="msg.sender_id === auth_id ? 'text-gray-800' : ''">
                                                <p class="font-bold text-[10px] text-gray-500 uppercase">Booking #{{ msg.booking.id }}</p>
                                                <p class="text-xs font-bold truncate">{{ msg.booking.service?.title || msg.service?.title || 'Info tidak tersedia' }}</p>
                                            </div>
                                            <div v-else-if="msg.service" @click="router.visit(route('service.show', msg.service.id))" class="bg-white/90 p-2 mb-2 rounded text-gray-800 cursor-pointer border-l-4 border-blue-400 shadow-sm transition hover:bg-white">
                                                <p class="font-bold text-[10px] text-gray-500 uppercase">Jasa</p>
                                                <p class="text-xs font-bold truncate">{{ msg.service.title }}</p>
                                            </div>

                                            <p class="leading-relaxed whitespace-pre-wrap">{{ msg.message }}</p>
                                        </div>
                                        
                                        <div class="text-[10px] mt-0.5 text-right opacity-70 flex justify-end items-center gap-1">
                                            {{ formatTime(msg.created_at) }}
                                            <i v-if="msg.sender_id === auth_id" class="fas fa-check-double text-[10px]" :class="msg.is_read ? 'text-blue-200' : 'opacity-50'"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white border-t border-gray-100 flex-shrink-0">
                            <div v-if="replyingTo" class="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center animate-slide-up">
                                <div class="flex-1 border-l-2 border-blue-500 pl-2">
                                    <p class="text-[10px] font-bold text-blue-600 mb-0.5">Membalas {{ replyingTo.sender_id === auth_id ? 'Diri Sendiri' : activeChat.name }}</p>
                                    <p class="text-xs text-gray-600 line-clamp-1">{{ replyingTo.message }}</p>
                                </div>
                                <button @click="cancelReply" class="text-gray-400 hover:text-red-500 p-1"><i class="fas fa-times"></i></button>
                            </div>
                            <div class="p-3">
                                <form @submit.prevent="sendMessage" class="flex items-center space-x-2 bg-gray-50 rounded-full border border-gray-200 px-2 py-1">
                                    <button type="button" class="text-gray-400 hover:text-blue-600 p-2 rounded-full hover:bg-gray-100 transition"><i class="fas fa-image text-lg"></i></button>
                                    <input type="text" v-model="form.message" ref="messageInput" placeholder="Ketik pesan..." class="flex-1 bg-transparent border-none text-sm focus:ring-0 px-2 py-2 placeholder-gray-400">
                                    <button type="submit" :disabled="form.processing || !form.message" class="bg-blue-600 text-white rounded-full h-8 w-8 flex items-center justify-center hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-sm">
                                        <i class="fas fa-paper-plane text-xs ml-0.5"></i>
                                    </button>
                                </form>
                            </div>
                        </div>

                    </div>

                    <div v-else class="hidden md:flex flex-1 flex-col items-center justify-center bg-white rounded-xl shadow-sm border border-gray-200 text-center p-8">
                        <div class="h-24 w-24 bg-blue-50 rounded-full flex items-center justify-center mb-4 animate-pulse"><i class="fas fa-comments text-4xl text-blue-200"></i></div>
                        <h3 class="text-lg font-bold text-gray-800">Mulai Percakapan</h3>
                        <p class="text-gray-500 text-sm mt-1 max-w-xs">Pilih kontak di sebelah kiri untuk melihat riwayat chat atau memulai pesan baru.</p>
                    </div>

                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 20px; }
.animate-slide-up { animation: slideUp 0.2s ease-out; }
@keyframes slideUp { from { transform: translateY(10px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>