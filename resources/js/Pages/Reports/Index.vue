<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import Pagination from '@/Components/Pagination.vue'; // <--- Import ini
import { Head, useForm, router, Link } from '@inertiajs/vue3';
import { ref } from 'vue';
import Modal from '@/Components/Modal.vue';
import InputLabel from '@/Components/InputLabel.vue';
import TextInput from '@/Components/TextInput.vue';
import InputError from '@/Components/InputError.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import DangerButton from '@/Components/DangerButton.vue';

const props = defineProps({
    reports: Object
});

// --- STATE ---
const showFormModal = ref(false);
const isEditing = ref(false);
const editReportId = ref(null);

// Lightbox State
const lightboxOpen = ref(false);
const lightboxImages = ref([]);
const activeImageIndex = ref(0);

// Tambahkan ref untuk element input dan preview
const fileInputRef = ref(null);
const previewImages = ref([]); // Menyimpan URL blob untuk preview visual

// Form Inertia
const form = useForm({
    subject: '',
    description: '',
    proof_images: [], // Array file
    _method: 'POST', // Default POST
});

// --- ACTIONS CRUD ---

const openCreateModal = () => {
    isEditing.value = false;
    form.reset();
    form.proof_images = []; // Pastikan array kosong
    previewImages.value = []; // Reset preview
    form._method = 'POST';
    showFormModal.value = true;
};

const openEditModal = (report) => {
    isEditing.value = true;
    editReportId.value = report.id;
    
    form.subject = report.subject;
    form.description = report.description;
    form.proof_images = []; // Kita mulai kosong untuk upload baru
    previewImages.value = []; // Reset preview upload baru
    form._method = 'POST';
    
    showFormModal.value = true;
};

// --- LOGIC UPLOAD GAMBAR BARU ---

// 1. Trigger klik input file yang tersembunyi
const triggerFileInput = () => {
    fileInputRef.value.click();
};

// 2. Handle saat file dipilih (Akumulatif)
const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    // Masukkan ke form.proof_images (gabungkan dengan yang sudah ada)
    // Kita gunakan spread operator [...] agar file lama tidak hilang
    form.proof_images = [...form.proof_images, ...files];

    // Buat URL preview untuk file baru
    files.forEach(file => {
        previewImages.value.push(URL.createObjectURL(file));
    });

    // Reset value input agar bisa memilih file yang sama lagi jika perlu
    // dan agar event @change bisa tertrigger lagi
    event.target.value = null;
};

// 3. Hapus file tertentu dari daftar upload
const removeFile = (index) => {
    // Hapus dari array form data
    form.proof_images.splice(index, 1);
    
    // Hapus visual preview dan bersihkan memori URL
    URL.revokeObjectURL(previewImages.value[index]);
    previewImages.value.splice(index, 1);
};

const submit = () => {
    if (isEditing.value) {
        // Khusus upload file saat edit di Laravel/Inertia, gunakan POST dengan _method: PUT/PATCH tidak selalu mulus
        // Cara paling aman: Gunakan route POST biasa, logic update di controller
        router.post(route('user.reports.update', editReportId.value), {
            _method: 'POST', // Pakai POST biasa ke route update
            subject: form.subject,
            description: form.description,
            proof_images: form.proof_images,
        }, {
            onSuccess: () => { showFormModal.value = false; form.reset(); },
            forceFormData: true, // Wajib untuk file
        });
    } else {
        form.post(route('user.reports.store'), {
            onSuccess: () => { showFormModal.value = false; form.reset(); },
            forceFormData: true,
        });
    }
};

const deleteReport = (report) => {
    if (confirm('Yakin ingin menghapus laporan ini?')) {
        router.delete(route('user.reports.destroy', report.id));
    }
};

// --- LIGHTBOX ACTIONS ---
const openLightbox = (images, index = 0) => {
    if (!images || images.length === 0) return;
    lightboxImages.value = images;
    activeImageIndex.value = index;
    lightboxOpen.value = true;
};

const closeLightbox = () => {
    lightboxOpen.value = false;
    lightboxImages.value = [];
};

const nextImage = () => {
    if (activeImageIndex.value < lightboxImages.value.length - 1) {
        activeImageIndex.value++;
    } else {
        activeImageIndex.value = 0; // Loop ke awal
    }
};

const prevImage = () => {
    if (activeImageIndex.value > 0) {
        activeImageIndex.value--;
    } else {
        activeImageIndex.value = lightboxImages.value.length - 1; // Loop ke akhir
    }
};

// --- HELPER ---
const getStatusClass = (status) => {
    switch(status) {
        case 'pending': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
        case 'resolved': return 'bg-green-100 text-green-700 border-green-200';
        case 'rejected': return 'bg-red-100 text-red-700 border-red-200';
        default: return 'bg-gray-100 text-gray-700';
    }
};

const getStatusLabel = (status) => {
    switch(status) {
        case 'pending': return 'Menunggu Tinjauan';
        case 'resolved': return 'Selesai';
        case 'rejected': return 'Ditolak';
        default: return status;
    }
};
</script>

<template>
    <Head title="Pusat Bantuan" />

    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                Pusat Bantuan & Laporan
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                
                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6 p-6 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div>
                        <h3 class="text-lg font-bold text-gray-900">Punya Kendala?</h3>
                        <p class="text-gray-600 text-sm mt-1">Kami siap membantu menyelesaikan masalah transaksi atau layanan Anda.</p>
                    </div>
                    <PrimaryButton @click="openCreateModal" class="px-6 py-3">
                        <i class="fas fa-plus mr-2"></i> Buat Laporan Baru
                    </PrimaryButton>
                </div>

                <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6 border-b border-gray-200">
                        <h3 class="text-lg font-bold text-gray-800 mb-4">Riwayat Laporan Saya</h3>
                        
                        <div v-if="reports.data.length > 0" class="space-y-6">
                            <div v-for="report in reports.data" :key="report.id" 
                                class="border border-gray-200 rounded-xl p-5 hover:bg-gray-50 transition relative group">
                                
                                <div class="flex justify-between items-start mb-2">
                                    <div class="flex items-center gap-3">
                                        <div class="h-10 w-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                                            <i class="fas fa-file-alt text-xl"></i>
                                        </div>
                                        <div>
                                            <h4 class="font-bold text-gray-900">{{ report.subject }}</h4>
                                            <span class="text-xs text-gray-500">
                                                {{ new Date(report.created_at).toLocaleDateString('id-ID', { dateStyle: 'full' }) }}
                                            </span>
                                        </div>
                                    </div>
                                    <span class="px-3 py-1 text-xs font-bold rounded-full border text-center" :class="getStatusClass(report.status)">
                                        {{ getStatusLabel(report.status) }}
                                    </span>
                                </div>
                                
                                <p class="text-gray-700 text-sm mt-3 ml-13 pl-1">{{ report.description }}</p>

                                <div v-if="report.proof_images && report.proof_images.length > 0"
                                    class="mt-4 flex gap-2 overflow-hidden pb-2 ml-1">

                                    <div v-for="(img, idx) in report.proof_images.slice(0, 3)" :key="idx"
                                        class="relative h-20 w-20 rounded-lg overflow-hidden border border-gray-300 cursor-pointer hover:opacity-80 transition shrink-0 group"
                                        @click="openLightbox(report.proof_images, idx)">

                                        <img :src="'/storage/' + img" class="h-full w-full object-cover">

                                        <div v-if="idx === 2 && report.proof_images.length > 3"
                                            class="absolute inset-0 bg-black/60 flex items-center justify-center text-white font-bold text-xs backdrop-blur-[1px]">
                                            +{{ report.proof_images.length - 3 }}
                                        </div>
                                    </div>

                                </div>

                                <div v-if="report.status === 'pending'" class="mt-4 flex gap-3 justify-end border-t border-gray-100 pt-3">
                                    <button @click="openEditModal(report)" class="text-xs font-bold text-blue-600 hover:underline">
                                        <i class="fas fa-edit mr-1"></i> Edit
                                    </button>
                                    <button @click="deleteReport(report)" class="text-xs font-bold text-red-600 hover:underline">
                                        <i class="fas fa-trash mr-1"></i> Hapus
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div v-else class="text-center py-12 text-gray-400">
                            <i class="far fa-folder-open text-4xl mb-2"></i>
                            <p>Belum ada laporan.</p>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <div class="flex justify-center pb-10 lg:mb-0 mb-12">
            <Pagination :links="reports.links" />
        </div>

        <Modal :show="showFormModal" @close="showFormModal = false">
            <div class="p-6">
                <h2 class="text-lg font-bold text-gray-900 mb-4">
                    {{ isEditing ? 'Edit Laporan' : 'Buat Laporan Baru' }}
                </h2>
                
                <form @submit.prevent="submit">
                    <div class="mb-4">
                        <InputLabel for="subject" value="Judul Masalah" />
                        <TextInput id="subject" v-model="form.subject" type="text" class="mt-1 w-full" required />
                        <InputError class="mt-2" :message="form.errors.subject" />
                    </div>

                    <div class="mb-4">
                        <InputLabel for="desc" value="Deskripsi Detail" />
                        <textarea id="desc" v-model="form.description" rows="4" class="w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500" required></textarea>
                        <InputError class="mt-2" :message="form.errors.description" />
                    </div>

                    <div class="mb-6">
                        <InputLabel value="Bukti Foto" class="mb-2" />

                        <div class="space-y-3">

                            <div v-if="previewImages.length > 0" class="grid grid-cols-3 sm:grid-cols-4 gap-3">
                                <div v-for="(img, index) in previewImages" :key="index"
                                    class="relative aspect-square group">
                                    <img :src="img"
                                        class="w-full h-full object-cover rounded-lg border border-gray-200">

                                    <button type="button" @click="removeFile(index)"
                                        class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center shadow-md hover:bg-red-600 transition transform hover:scale-110">
                                        <i class="fas fa-times text-xs"></i>
                                    </button>
                                </div>
                            </div>

                            <div @click="triggerFileInput"
                                class="border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors group">

                                <div class="bg-gray-100 p-3 rounded-full mb-2 group-hover:bg-white transition">
                                    <i class="fas fa-camera text-gray-400 text-xl group-hover:text-blue-500"></i>
                                </div>

                                <p class="text-sm font-medium text-gray-700">
                                    <span class="text-blue-600">Klik untuk upload</span> atau drag foto
                                </p>
                                <p class="text-xs text-gray-400 mt-1">PNG, JPG up to 5MB</p>
                            </div>

                            <input type="file" ref="fileInputRef" class="hidden" multiple accept="image/*"
                                @change="handleFileChange" />

                            <p class="text-xs text-gray-500 italic bg-yellow-50 p-2 rounded border border-yellow-100"
                                v-if="isEditing">
                                <i class="fas fa-info-circle mr-1"></i>
                                Mengupload gambar baru di sini akan <b>menambahkan/mengganti</b> gambar lama sesuai
                                kebijakan sistem.
                            </p>

                            <InputError class="mt-2" :message="form.errors.proof_images" />
                        </div>
                    </div>

                    <div class="flex justify-end gap-3">
                        <SecondaryButton @click="showFormModal = false"> Batal </SecondaryButton>
                        <PrimaryButton :disabled="form.processing"> {{ isEditing ? 'Simpan Perubahan' : 'Kirim Laporan' }} </PrimaryButton>
                    </div>
                </form>
            </div>
        </Modal>

        <div v-if="lightboxOpen" class="fixed inset-0 z-[99999] bg-black/90 flex items-center justify-center backdrop-blur-sm" @click.self="closeLightbox">
            
            <button @click="closeLightbox" class="absolute top-5 right-5 text-white text-3xl hover:text-gray-300 z-50">
                <i class="fas fa-times"></i>
            </button>

            <button v-if="lightboxImages.length > 1" @click="prevImage" class="absolute left-5 text-white text-3xl hover:bg-white/10 p-2 rounded-full transition">
                <i class="fas fa-chevron-left"></i>
            </button>

            <div class="relative max-w-4xl max-h-screen p-4">
                <img :src="'/storage/' + lightboxImages[activeImageIndex]" class="max-w-full max-h-[85vh] object-contain rounded-md shadow-2xl animate-fade-in">
                
                <div class="absolute bottom-[-30px] left-0 right-0 text-center text-white text-sm">
                    Gambar {{ activeImageIndex + 1 }} dari {{ lightboxImages.length }}
                </div>
            </div>

            <button v-if="lightboxImages.length > 1" @click="nextImage" class="absolute right-5 text-white text-3xl hover:bg-white/10 p-2 rounded-full transition">
                <i class="fas fa-chevron-right"></i>
            </button>
        </div>

    </AuthenticatedLayout>
</template>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
</style>