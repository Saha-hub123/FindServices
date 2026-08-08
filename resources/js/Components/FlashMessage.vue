<script setup>
import { usePage } from '@inertiajs/vue3';
import { ref, watch, computed } from 'vue';

const page = usePage();
const show = ref(false);
const message = ref('');
const type = ref('success');

// Simpan timestamp terakhir agar tidak memunculkan pesan yang sama berulang kali
const lastTimestamp = ref(null);

let timeout = null;

// --- PERBAIKAN: PINDAHKAN FUNGSI INI KE ATAS (SEBELUM WATCH) ---
const triggerToast = (msg, msgType) => {
    // Hapus timer lama jika ada (reset durasi)
    if (timeout) clearTimeout(timeout);

    message.value = msg;
    type.value = msgType || 'success';
    show.value = true;

    // Hilang otomatis setelah 4 detik
    timeout = setTimeout(() => {
        show.value = false;
    }, 4000);
};

// Watcher memantau prop 'flash' dari HandleInertiaRequests
watch(() => page.props.flash, (newFlash) => {
    // 1. Cek Validitas Data
    if (!newFlash || !newFlash.message || !newFlash.timestamp) {
        return;
    }

    // 2. LOGIKA ANTI-LOOPING
    if (newFlash.timestamp === lastTimestamp.value) {
        return;
    }

    // 3. Update timestamp terakhir
    lastTimestamp.value = newFlash.timestamp;

    // 4. Tampilkan Pesan
    triggerToast(newFlash.message, newFlash.type);

}, { deep: true, immediate: true }); 
// ^ immediate: true inilah yang memaksa fungsi harus ada sebelumnya

// Styling (Tetap sama)
const classes = computed(() => {
    switch (type.value) {
        case 'error': return 'bg-red-50 border-red-200 text-red-800';
        case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
        default: return 'bg-green-50 border-green-200 text-green-800';
    }
});

const iconClass = computed(() => {
    switch (type.value) {
        case 'error': return 'fas fa-times-circle text-red-500';
        case 'warning': return 'fas fa-exclamation-triangle text-yellow-500';
        default: return 'fas fa-check-circle text-green-500';
    }
});
</script>

<template>
    <Transition
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-100"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
    >
        <div v-if="show" class="fixed top-20 right-5 z-[10000] max-w-sm w-full shadow-lg rounded-lg pointer-events-auto border overflow-hidden backdrop-blur-sm bg-white" :class="classes">
            <div class="p-4">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <i class="text-xl" :class="iconClass"></i>
                    </div>
                    <div class="ml-3 w-0 flex-1 pt-0.5">
                        <p class="text-sm font-medium leading-tight">
                            {{ message }}
                        </p>
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button @click="show = false" class="inline-flex text-gray-400 hover:text-gray-500 focus:outline-none transition">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
            <div class="h-1 bg-current opacity-20 w-full animate-shrink"></div>
        </div>
    </Transition>
</template>

<style scoped>
.animate-shrink {
    animation: shrink 4s linear forwards;
}
@keyframes shrink {
    from { width: 100%; }
    to { width: 0%; }
}
</style>