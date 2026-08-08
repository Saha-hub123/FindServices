<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, router, useForm, Link } from '@inertiajs/vue3';
import { ref, watch } from 'vue';
import Modal from '@/Components/Modal.vue'; 
import SecondaryButton from '@/Components/SecondaryButton.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import DangerButton from '@/Components/DangerButton.vue';

const props = defineProps({
    reports: Object,
    filters: Object
});

// --- STATE ---
const activeTab = ref(props.filters.status || 'all');
const showDetailModal = ref(false);
const selectedReport = ref(null);

// Lightbox State
const lightboxOpen = ref(false);
const lightboxImages = ref([]);
const activeImageIndex = ref(0);

// --- TAB FILTER ---
// Mengganti URL saat tab berubah tanpa reload
watch(activeTab, (val) => {
    router.get(route('admin.reports.index'), { status: val }, {
        preserveState: true,
        replace: true
    });
});

// --- ACTIONS ---
const openDetail = (report) => {
    selectedReport.value = report;
    showDetailModal.value = true;
};

const closeDetail = () => {
    showDetailModal.value = false;
    setTimeout(() => selectedReport.value = null, 300);
};

// Update Status (Resolved / Rejected)
const updateStatus = (status) => {
    if(!selectedReport.value) return;

    router.patch(route('admin.reports.update', selectedReport.value.id), {
        status: status
    }, {
        onSuccess: () => closeDetail()
    });
};

// Helper Warna Badge
const getStatusClass = (status, isDeleted = false) => {
    if (isDeleted) return 'bg-gray-800 text-white border-gray-600'; // Warna Gelap untuk sampah

    switch(status) {
        case 'pending': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
        case 'resolved': return 'bg-green-100 text-green-700 border-green-200';
        case 'rejected': return 'bg-red-100 text-red-700 border-red-200';
        default: return 'bg-gray-100 text-gray-700';
    }
};

// Helper Label
const getStatusLabel = (status, isDeleted = false) => {
    if (isDeleted) return 'Terhapus';
    
    switch(status) {
        case 'pending': return 'Menunggu';
        case 'resolved': return 'Selesai';
        case 'rejected': return 'Ditolak';
        default: return status;
    }
};

// Action Restore
const restoreReport = () => {
    if(!selectedReport.value) return;
    
    if(confirm('Kembalikan laporan ini agar aktif kembali?')) {
        router.post(route('admin.reports.restore', selectedReport.value.id), {}, {
            onSuccess: () => closeDetail()
        });
    }
};

// --- LIGHTBOX ACTIONS ---
const openLightbox = (images, index) => {
    lightboxImages.value = images;
    activeImageIndex.value = index;
    lightboxOpen.value = true;
};

const closeLightbox = () => {
    lightboxOpen.value = false;
    lightboxImages.value = [];
};

const nextImage = () => {
    activeImageIndex.value = (activeImageIndex.value + 1) % lightboxImages.value.length;
};

const prevImage = () => {
    activeImageIndex.value = (activeImageIndex.value - 1 + lightboxImages.value.length) % lightboxImages.value.length;
};
</script>

<template>
    <Head title="Pusat Aduan" />

    <AuthenticatedLayout>
        <AdminLayout>
            
            <div class="mb-6">
                <div class="w-full md:w-fit bg-white p-1 rounded-xl shadow-sm border border-gray-200">

                    <div class="overflow-x-auto hide-scrollbar">

                        <div class="flex space-x-1 min-w-max">

                            <button @click="activeTab = 'all'"
                                class="px-4 py-2 text-xs md:text-sm font-medium rounded-lg transition whitespace-nowrap"
                                :class="activeTab === 'all' ? 'bg-blue-100 text-blue-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'">
                                Semua
                            </button>

                            <button @click="activeTab = 'pending'"
                                class="px-4 py-2 text-xs md:text-sm font-medium rounded-lg transition whitespace-nowrap"
                                :class="activeTab === 'pending' ? 'bg-yellow-100 text-yellow-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'">
                                Menunggu
                            </button>

                            <button @click="activeTab = 'resolved'"
                                class="px-4 py-2 text-xs md:text-sm font-medium rounded-lg transition whitespace-nowrap"
                                :class="activeTab === 'resolved' ? 'bg-green-100 text-green-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'">
                                Selesai
                            </button>

                            <button @click="activeTab = 'rejected'"
                                class="px-4 py-2 text-xs md:text-sm font-medium rounded-lg transition whitespace-nowrap"
                                :class="activeTab === 'rejected' ? 'bg-red-100 text-red-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'">
                                Ditolak
                            </button>

                            <button @click="activeTab = 'trash'"
                                class="px-4 py-2 text-xs md:text-sm font-medium rounded-lg transition flex items-center gap-2 whitespace-nowrap"
                                :class="activeTab === 'trash' ? 'bg-gray-800 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'">
                                <i class="fas fa-trash-alt text-xs"></i> Sampah
                            </button>

                        </div>
                    </div>
                </div>
            </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

                <div class="hidden md:block overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th
                                    class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    Tanggal</th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    Pelapor</th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    Subjek Masalah</th>
                                <th
                                    class="px-6 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    Status</th>
                                <th
                                    class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    Aksi</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            <tr v-for="report in reports.data" :key="report.id" class="hover:bg-gray-50 transition">
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {{ new Date(report.created_at).toLocaleDateString('id-ID') }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="flex items-center">
                                        <img :src="'https://ui-avatars.com/api/?name=' + report.user.name"
                                            class="h-6 w-6 rounded-full mr-2">
                                        <span class="text-sm font-medium text-gray-900">{{ report.user.name }}</span>
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="text-sm text-gray-800 font-semibold">{{ report.subject }}</span>
                                    <p class="text-xs text-gray-500 truncate max-w-xs">{{ report.description }}</p>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-center">
                                    <span class="px-2.5 py-1 text-xs font-bold rounded-full border capitalize"
                                        :class="getStatusClass(report.status, report.deleted_at)">
                                        {{ getStatusLabel(report.status, report.deleted_at) }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button @click="openDetail(report)"
                                        class="text-blue-600 hover:text-blue-900 bg-blue-50 px-3 py-1.5 rounded-lg transition text-xs font-bold">
                                        Lihat Detail
                                    </button>
                                </td>
                            </tr>
                            <tr v-if="reports.data.length === 0">
                                <td colspan="5" class="px-6 py-10 text-center text-gray-500 text-sm">
                                    <i class="fas fa-inbox text-3xl mb-3 text-gray-300 block mx-auto"></i>
                                    Tidak ada laporan ditemukan.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="md:hidden space-y-4 p-4 bg-gray-50">
                    <div v-for="report in reports.data" :key="report.id"
                        class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 relative overflow-hidden">

                        <div class="flex items-start justify-between mb-3">
                            <div class="flex items-center gap-2">
                                <img :src="'https://ui-avatars.com/api/?name=' + report.user.name"
                                    class="h-8 w-8 rounded-full border border-gray-100">
                                <div>
                                    <h3 class="text-xs font-bold text-gray-900">{{ report.user.name }}</h3>
                                    <p class="text-[10px] text-gray-500">{{ new
                                        Date(report.created_at).toLocaleDateString('id-ID') }}</p>
                                </div>
                            </div>

                            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full border capitalize"
                                :class="getStatusClass(report.status, report.deleted_at)">
                                {{ getStatusLabel(report.status, report.deleted_at) }}
                            </span>
                        </div>

                        <div class="mb-3">
                            <h4 class="text-sm font-bold text-gray-800 mb-1">{{ report.subject }}</h4>
                            <p class="text-xs text-gray-500 line-clamp-2 leading-relaxed">
                                {{ report.description }}
                            </p>
                        </div>

                        <div class="border-t border-gray-100 pt-3 mt-3">
                            <button @click="openDetail(report)"
                                class="w-full py-2.5 bg-blue-50 text-blue-700 font-bold text-xs rounded-lg hover:bg-blue-100 transition flex items-center justify-center gap-2">
                                <i class="fas fa-eye"></i> Lihat Detail Laporan
                            </button>
                        </div>

                    </div>

                    <div v-if="reports.data.length === 0" class="text-center py-10">
                        <i class="fas fa-inbox text-4xl text-gray-300 mb-2"></i>
                        <p class="text-gray-500 text-sm">Tidak ada laporan.</p>
                    </div>
                </div>

            </div>
             <div v-if="reports.links.length > 3" class="mt-4 flex justify-end">
                <div class="flex gap-1">
                    <template v-for="(link, k) in reports.links" :key="k">
                        <Link 
                            v-if="link.url"
                            :href="link.url"
                            v-html="link.label"
                            class="px-3 py-1 border rounded text-xs font-medium transition"
                            :class="link.active ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 hover:bg-gray-50'"
                        />
                        <span v-else v-html="link.label" class="px-3 py-1 text-gray-400 text-xs border rounded"></span>
                    </template>
                </div>
            </div>

            <Modal :show="showDetailModal" @close="closeDetail">
                <div class="p-6" v-if="selectedReport">
                    
                    <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100">
                        <h2 class="text-xl font-bold text-gray-900">Detail Laporan</h2>
                        <span class="px-3 py-1 text-xs font-bold rounded-full border capitalize tracking-wide shadow-sm" 
                              :class="getStatusClass(selectedReport.status)">
                            {{ getStatusLabel(selectedReport.status) }}
                        </span>
                    </div>

                    <div class="space-y-5">
                        <div class="flex items-center p-4 bg-blue-50/50 rounded-xl border border-blue-100">
                            <img :src="'https://ui-avatars.com/api/?name=' + selectedReport.user.name" class="h-12 w-12 rounded-full mr-4 shadow-sm">
                            <div>
                                <p class="text-sm font-bold text-gray-800">{{ selectedReport.user.name }}</p>
                                <p class="text-xs text-gray-500 font-medium">{{ selectedReport.user.email }}</p>
                            </div>
                        </div>

                        <div>
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">Subjek Masalah</label>
                            <p class="text-gray-900 font-bold text-lg leading-tight">{{ selectedReport.subject }}</p>
                        </div>
                        
                        <div>
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">Kronologi / Deskripsi</label>
                            <div class="bg-gray-50 p-4 rounded-xl border border-gray-200 text-gray-700 text-sm leading-relaxed max-h-48 overflow-y-auto custom-scrollbar">
                                {{ selectedReport.description }}
                            </div>
                        </div>

                        <div v-if="selectedReport.proof_images && selectedReport.proof_images.length > 0">
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">
                                Bukti Lampiran ({{ selectedReport.proof_images.length }})
                            </label>
                            
                            <div class="grid grid-cols-4 gap-2">
                                <div v-for="(img, idx) in selectedReport.proof_images.slice(0, 4)" :key="idx" 
                                     class="relative aspect-square rounded-lg overflow-hidden border border-gray-300 cursor-pointer group shadow-sm transition"
                                     @click="openLightbox(selectedReport.proof_images, idx)">
                                    
                                    <img :src="'/storage/' + img" class="w-full h-full object-cover transition duration-300 group-hover:scale-110">
                                    
                                    <div v-if="idx === 3 && selectedReport.proof_images.length > 4" 
                                         class="absolute inset-0 bg-black/60 flex items-center justify-center text-white font-bold text-lg backdrop-blur-[2px]">
                                        +{{ selectedReport.proof_images.length - 4 }}
                                    </div>

                                    <div v-else class="absolute inset-0 bg-black/0 group-hover:bg-black/20 flex items-center justify-center transition duration-300">
                                        <i class="fas fa-search-plus text-white opacity-0 group-hover:opacity-100 text-lg drop-shadow-md transform scale-75 group-hover:scale-100 transition"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else>
                            <div class="p-4 border border-dashed border-gray-300 rounded-lg text-center bg-gray-50">
                                <p class="text-sm text-gray-400 italic">Tidak ada bukti lampiran.</p>
                            </div>
                        </div>
                    </div>

                    <div class="mt-8 pt-5 border-t border-gray-100 flex flex-col-reverse sm:flex-row sm:justify-end gap-3">
                        <SecondaryButton @click="closeDetail" class="w-full sm:w-auto justify-center">
                            Tutup
                        </SecondaryButton>
                        <template v-if="selectedReport.deleted_at">
                            <button @click="restoreReport"
                                class="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 bg-gray-800 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 transition shadow-md gap-2">
                                <i class="fas fa-trash-restore"></i> Pulihkan Laporan
                            </button>
                        </template>
                        <template v-if="selectedReport.status === 'pending'">
                            <DangerButton @click="updateStatus('rejected')" class="w-full sm:w-auto justify-center flex items-center gap-2">
                                <i class="fas fa-times-circle"></i> Tolak
                            </DangerButton>
                            <button @click="updateStatus('resolved')" 
                                class="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 bg-green-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-green-500 active:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 transition shadow-md gap-2">
                                <i class="fas fa-check-circle"></i> Selesai
                            </button>
                        </template>
                    </div>
                </div>
            </Modal>

            <Teleport to="body">
                <div v-if="lightboxOpen" 
                     class="fixed inset-0 z-[9999] bg-black/95 flex items-center justify-center backdrop-blur-md transition-opacity duration-300" 
                     @click.self="closeLightbox">
                    
                    <button @click="closeLightbox" class="absolute top-6 right-6 text-white/60 hover:text-white text-5xl z-[2147483647] focus:outline-none transition transform hover:rotate-90">
                        &times;
                    </button>

                    <button v-if="lightboxImages.length > 1" @click="prevImage" class="absolute left-4 sm:left-10 text-white/60 hover:text-white text-4xl sm:text-6xl p-4 transition focus:outline-none z-[2147483647]">
                        &#10094;
                    </button>

                    <div class="relative w-full h-full flex items-center justify-center p-4 sm:p-12 pointer-events-none">
                        <img :src="'/storage/' + lightboxImages[activeImageIndex]" 
                             class="max-w-full max-h-[90vh] object-contain shadow-2xl rounded pointer-events-auto select-none">
                        
                        <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-white/10 text-white/90 px-4 py-1.5 rounded-full text-sm font-medium border border-white/10 backdrop-blur pointer-events-auto">
                            {{ activeImageIndex + 1 }} / {{ lightboxImages.length }}
                        </div>
                    </div>

                    <button v-if="lightboxImages.length > 1" @click="nextImage" class="absolute right-4 sm:right-10 text-white/60 hover:text-white text-4xl sm:text-6xl p-4 transition focus:outline-none z-[2147483647]">
                        &#10095;
                    </button>
                </div>
            </Teleport>

        </AdminLayout>
    </AuthenticatedLayout>
</template>
<style scoped>
.animate-zoom-in {
    animation: zoomIn 0.3s ease-out;
}
@keyframes zoomIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}
.hide-scrollbar::-webkit-scrollbar {
    display: none;
}
.hide-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
}
</style>