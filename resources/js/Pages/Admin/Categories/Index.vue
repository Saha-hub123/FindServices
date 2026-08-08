<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, useForm, router, Link } from '@inertiajs/vue3'; // <--- Link DIIMPORT DISINI
import { ref, watch } from 'vue';
import Modal from '@/Components/Modal.vue';
import InputLabel from '@/Components/InputLabel.vue';
import TextInput from '@/Components/TextInput.vue';
import InputError from '@/Components/InputError.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';

const props = defineProps({
    categories: Object,
    filters: Object
});

// --- STATE ---
const showModal = ref(false);
const isEditing = ref(false);
const editId = ref(null);

// --- SEARCH & RESET ---
const search = ref(props.filters.q || '');

// Fungsi Reset Search
const resetSearch = () => {
    search.value = ''; // Ini akan men-trigger watcher di bawah
};

watch(search, (value) => {
    router.get(route('admin.categories.index'), { q: value }, {
        preserveState: true,
        replace: true,
    });
});

// --- FORM ---
const form = useForm({
    name: '',
    icon_class: 'fas fa-tag',
});

// --- ACTIONS ---
const openCreateModal = () => {
    isEditing.value = false;
    form.reset();
    form.icon_class = 'fas fa-tag';
    form.clearErrors();
    showModal.value = true;
};

const openEditModal = (category) => {
    isEditing.value = true;
    editId.value = category.id;
    form.name = category.name;
    form.icon_class = category.icon_class;
    form.clearErrors();
    showModal.value = true;
};

const closeModal = () => {
    showModal.value = false;
    form.reset();
};

const submit = () => {
    if (isEditing.value) {
        form.put(route('admin.categories.update', editId.value), {
            onSuccess: () => closeModal(),
        });
    } else {
        form.post(route('admin.categories.store'), {
            onSuccess: () => closeModal(),
        });
    }
};

const deleteCategory = (category) => {
    if (confirm(`Pindahkan kategori "${category.name}" ke sampah?`)) {
        router.delete(route('admin.categories.destroy', category.id));
    }
};

const restoreCategory = (category) => {
    if (confirm(`Pulihkan kategori "${category.name}"?`)) {
        // Ganti ke POST agar error hilang
        router.post(route('admin.categories.restore', category.id));
    }
};
</script>

<template>
    <Head title="Manajemen Kategori" />

    <AuthenticatedLayout>
        <AdminLayout>
            
            <div class="mb-6 flex flex-row justify-between items-center gap-4">
               <!-- Search Bar (Kiri) -->
                <div class="relative w-64 sm:w-72">
                    <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-search text-gray-400"></i>
                    </span>
                    <input v-model="search" type="text" placeholder="Cari kategori..."
                        class="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm transition shadow-sm">
                    <button v-if="search" @click="resetSearch"
                        class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition">
                        <i class="fas fa-times-circle"></i>
                    </button>
                </div>

                <!-- Tombol Tambah (Kanan) -->
                <button @click="openCreateModal"
                    class="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2 text-sm font-bold shadow-md active:scale-95 transform whitespace-nowrap">
                    <i class="fas fa-plus"></i>
                    <span>Tambah Kategori</span>
                </button>
            </div>


         <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

                <div class="hidden md:block overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th
                                    class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider w-16">
                                    No</th>
                                <th
                                    class="px-6 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider w-16">
                                    Icon</th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    Nama Kategori</th>
                                <th
                                    class="px-6 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    Status</th>
                                <th
                                    class="px-6 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    Jumlah Jasa</th>
                                <th
                                    class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    Aksi</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            <tr v-for="(category, index) in categories.data" :key="category.id"
                                class="hover:bg-gray-50 transition" :class="{ 'bg-red-50/50': category.deleted_at }">

                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {{ (categories.current_page - 1) * categories.per_page + index + 1 }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-center text-gray-600">
                                    <i :class="category.icon_class" class="text-lg"></i>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="flex flex-col">
                                        <span class="text-sm font-bold text-gray-800"
                                            :class="{ 'line-through text-gray-400': category.deleted_at }">
                                            {{ category.name }}
                                        </span>
                                        <span class="text-xs text-gray-400 italic">{{ category.slug }}</span>
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-center">
                                    <span v-if="category.deleted_at"
                                        class="px-2 py-1 text-[10px] font-bold rounded-full bg-red-100 text-red-600 border border-red-200 uppercase">Terhapus</span>
                                    <span v-else
                                        class="px-2 py-1 text-[10px] font-bold rounded-full bg-green-100 text-green-600 border border-green-200 uppercase">Aktif</span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-center">
                                    <span class="px-2 py-1 text-xs font-bold rounded-full bg-blue-50 text-blue-600">
                                        {{ category.services_count }} Jasa
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                                    <template v-if="!category.deleted_at">
                                        <button @click="openEditModal(category)"
                                            class="text-blue-600 hover:text-blue-900 bg-blue-50 p-2 rounded-lg transition"
                                            title="Edit">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button @click="deleteCategory(category)"
                                            class="text-red-600 hover:text-red-900 bg-red-50 p-2 rounded-lg transition"
                                            title="Hapus">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </template>
                                    <template v-else>
                                        <button @click="restoreCategory(category)"
                                            class="text-green-600 hover:text-green-900 bg-green-50 p-2 rounded-lg transition"
                                            title="Pulihkan">
                                            <i class="fas fa-trash-restore"></i>
                                        </button>
                                    </template>
                                </td>
                            </tr>
                            <tr v-if="categories.data.length === 0">
                                <td colspan="6" class="px-6 py-10 text-center text-gray-500 text-sm">
                                    <i class="fas fa-folder-open text-3xl mb-3 text-gray-300 block mx-auto"></i>
                                    Belum ada kategori ditemukan.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="md:hidden space-y-4 p-4 bg-gray-50">
                    <div v-for="(category, index) in categories.data" :key="category.id"
                        class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 relative overflow-hidden"
                        :class="{ 'border-red-200 bg-red-50': category.deleted_at }">

                        <div class="flex items-start gap-3 mb-3">
                            <div
                                class="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center text-gray-600 shrink-0">
                                <i :class="category.icon_class" class="text-lg"></i>
                            </div>
                            <div class="flex-1 min-w-0">
                                <h3 class="text-sm font-bold text-gray-900 truncate"
                                    :class="{ 'line-through text-gray-500': category.deleted_at }">
                                    {{ category.name }}
                                </h3>
                                <p class="text-xs text-gray-500 truncate">{{ category.slug }}</p>
                            </div>
                            <span v-if="category.deleted_at"
                                class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-600 border border-red-200 uppercase">
                                Terhapus
                            </span>
                            <span v-else
                                class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-green-100 text-green-600 border border-green-200 uppercase">
                                Aktif
                            </span>
                        </div>

                        <div
                            class="flex justify-between items-center text-xs text-gray-500 border-t border-gray-100 pt-3 mb-3">
                            <span>No. {{ (categories.current_page - 1) * categories.per_page + index + 1 }}</span>
                            <span class="font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                                {{ category.services_count }} Jasa Terdaftar
                            </span>
                        </div>

                        <div class="flex gap-2">
                            <template v-if="!category.deleted_at">
                                <button @click="openEditModal(category)"
                                    class="flex-1 py-2 bg-blue-50 text-blue-700 font-bold text-xs rounded-lg hover:bg-blue-100 transition flex items-center justify-center gap-2">
                                    <i class="fas fa-edit"></i> Edit
                                </button>
                                <button @click="deleteCategory(category)"
                                    class="flex-1 py-2 bg-red-50 text-red-700 font-bold text-xs rounded-lg hover:bg-red-100 transition flex items-center justify-center gap-2">
                                    <i class="fas fa-trash"></i> Hapus
                                </button>
                            </template>
                            <template v-else>
                                <button @click="restoreCategory(category)"
                                    class="w-full py-2 bg-green-50 text-green-700 font-bold text-xs rounded-lg hover:bg-green-100 transition flex items-center justify-center gap-2">
                                    <i class="fas fa-trash-restore"></i> Pulihkan Kategori
                                </button>
                            </template>
                        </div>
                    </div>

                    <div v-if="categories.data.length === 0" class="text-center py-10">
                        <i class="fas fa-folder-open text-4xl text-gray-300 mb-2"></i>
                        <p class="text-gray-500 text-sm">Belum ada kategori.</p>
                    </div>
                </div>

            </div>

            <div v-if="categories.links.length > 3" class="mt-4 flex justify-end">
                <div class="flex gap-1">
                    <template v-for="(link, k) in categories.links" :key="k">
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

            <Modal :show="showModal" @close="closeModal">
                <div class="p-6">
                    <h2 class="text-lg font-bold text-gray-900 mb-4">
                        {{ isEditing ? 'Edit Kategori' : 'Tambah Kategori Baru' }}
                    </h2>

                    <form @submit.prevent="submit">
                        <div class="mb-4">
                            <InputLabel for="name" value="Nama Kategori" />
                            <TextInput
                                id="name"
                                type="text"
                                class="mt-1 block w-full"
                                v-model="form.name"
                                required
                                autofocus
                                placeholder="Contoh: Elektronik"
                            />
                            <InputError class="mt-2" :message="form.errors.name" />
                        </div>

                        <div class="mb-4">
                            <InputLabel for="icon_class" value="Icon Class (FontAwesome)" />
                            <div class="flex items-center gap-3">
                                <TextInput
                                    id="icon_class"
                                    type="text"
                                    class="mt-1 block w-full"
                                    v-model="form.icon_class"
                                    required
                                    placeholder="Contoh: fas fa-bolt"
                                />
                                <div class="mt-1 h-10 w-12 bg-gray-100 border border-gray-300 rounded flex items-center justify-center text-gray-700">
                                    <i :class="form.icon_class"></i>
                                </div>
                            </div>
                            <p class="text-xs text-gray-500 mt-1">
                                Gunakan class dari FontAwesome Free.
                            </p>
                            <InputError class="mt-2" :message="form.errors.icon_class" />
                        </div>

                        <div class="mt-6 flex justify-end gap-3">
                            <SecondaryButton @click="closeModal"> Batal </SecondaryButton>
                            <PrimaryButton :class="{ 'opacity-25': form.processing }" :disabled="form.processing">
                                {{ isEditing ? 'Simpan Perubahan' : 'Simpan' }}
                            </PrimaryButton>
                        </div>
                    </form>
                </div>
            </Modal>

        </AdminLayout>
    </AuthenticatedLayout>
</template>