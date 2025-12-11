<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, useForm, usePage } from '@inertiajs/vue3';
import { ref } from 'vue';

const user = usePage().props.auth.user;

const form = useForm({
    name: user.name,
    bio: user.bio || '',
    address: user.address || '',
    avatar: null, // Untuk file upload
    _method: 'PATCH' // Trik untuk upload file di Laravel via Inertia
});

const avatarPreview = ref(
    user.avatar 
    ? '/storage/' + user.avatar 
    : `https://ui-avatars.com/api/?name=${user.name}&background=random`
);

const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
        form.avatar = file;
        avatarPreview.value = URL.createObjectURL(file); // Preview instant
    }
};

const submit = () => {
    form.post(route('profile.update'), {
        preserveScroll: true,
        forceFormData: true, // Wajib untuk upload file
    });
};
</script>

<template>
    <Head title="Edit Profil Publik" />

    <AuthenticatedLayout>
        <div class="py-6 bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex flex-col md:flex-row gap-6">
                    
                    <div class="w-full md:w-1/4">
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden sticky top-24">
                            <div class="p-4 border-b border-gray-100">
                                <h2 class="font-bold text-gray-800">Pengaturan</h2>
                            </div>
                            <nav class="flex flex-col p-2 space-y-1">
                                <Link :href="route('profile.edit')" class="flex items-center px-4 py-2.5 text-sm font-bold bg-blue-50 text-blue-700 rounded-lg">
                                    <i class="fas fa-user-circle mr-3 w-5"></i> Profil Publik
                                </Link>
                                <Link :href="route('profile.settings')" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition">
                                    <i class="fas fa-shield-alt mr-3 w-5"></i> Akun & Keamanan
                                </Link>
                                <Link :href="route('profile.index')" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition border-t border-gray-100 mt-1">
                                    <i class="fas fa-external-link-alt mr-3 w-5"></i> Lihat Profil Saya
                                </Link>
                            </nav>
                        </div>
                    </div>

                    <div class="w-full md:w-3/4">
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
                            <h2 class="text-xl font-bold text-gray-900 mb-6">Edit Profil Publik</h2>
                            
                            <form @submit.prevent="submit" class="space-y-6">
                                
                                <div class="flex items-center gap-6">
                                    <div class="shrink-0 relative group cursor-pointer">
                                        <img :src="avatarPreview" class="h-24 w-24 rounded-full object-cover border-2 border-gray-200">
                                        <div class="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition" onclick="document.getElementById('avatarInput').click()">
                                            <i class="fas fa-camera text-white"></i>
                                        </div>
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Foto Profil</label>
                                        <p class="text-xs text-gray-500 mb-3">Format JPG/PNG, maks 2MB.</p>
                                        <input type="file" id="avatarInput" @change="handleAvatarChange" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition"/>
                                        <div v-if="form.errors.avatar" class="text-red-500 text-xs mt-1">{{ form.errors.avatar }}</div>
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Nama Lengkap / Bisnis</label>
                                    <input v-model="form.name" type="text" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                    <div v-if="form.errors.name" class="text-red-500 text-xs mt-1">{{ form.errors.name }}</div>
                                </div>

                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Bio / Deskripsi Singkat</label>
                                    <textarea v-model="form.bio" rows="3" placeholder="Ceritakan sedikit tentang diri Anda atau jasa Anda..." class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"></textarea>
                                    <div v-if="form.errors.bio" class="text-red-500 text-xs mt-1">{{ form.errors.bio }}</div>
                                </div>

                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Alamat Utama</label>
                                    <input v-model="form.address" type="text" placeholder="Kota, Provinsi" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                    <div v-if="form.errors.address" class="text-red-500 text-xs mt-1">{{ form.errors.address }}</div>
                                </div>

                                <div class="pt-4 border-t border-gray-100 flex justify-end">
                                    <button type="submit" :disabled="form.processing" class="px-6 py-2.5 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition disabled:opacity-50">
                                        Simpan Perubahan
                                    </button>
                                </div>

                            </form>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>