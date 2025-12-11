<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import DeleteUserForm from './Partials/DeleteUserForm.vue'; // Bawaan Breeze
import UpdatePasswordForm from './Partials/UpdatePasswordForm.vue'; // Bawaan Breeze
import { Head, Link, useForm, usePage } from '@inertiajs/vue3';

const user = usePage().props.auth.user;

const form = useForm({
    email: user.email,
    phone: user.phone || '',
});

const submitInfo = () => {
    form.patch(route('profile.update'));
};
</script>

<template>
    <Head title="Pengaturan Akun" />

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
                                <Link :href="route('profile.edit')" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition">
                                    <i class="fas fa-user-circle mr-3 w-5"></i> Profil Publik
                                </Link>
                                <Link :href="route('profile.settings')" class="flex items-center px-4 py-2.5 text-sm font-bold bg-blue-50 text-blue-700 rounded-lg">
                                    <i class="fas fa-shield-alt mr-3 w-5"></i> Akun & Keamanan
                                </Link>
                                <Link :href="route('profile.index')" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition border-t border-gray-100 mt-1">
                                    <i class="fas fa-external-link-alt mr-3 w-5"></i> Lihat Profil Saya
                                </Link>
                            </nav>
                        </div>
                    </div>

                    <div class="w-full md:w-3/4 space-y-6">
                        
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
                            <h2 class="text-lg font-bold text-gray-900 mb-4">Informasi Kontak</h2>
                            <form @submit.prevent="submitInfo" class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                    <input v-model="form.email" type="email" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                    <div v-if="form.errors.email" class="text-red-500 text-xs mt-1">{{ form.errors.email }}</div>
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Nomor Telepon / WhatsApp</label>
                                    <input v-model="form.phone" type="text" placeholder="08xxxxxxxx" class="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                    <div v-if="form.errors.phone" class="text-red-500 text-xs mt-1">{{ form.errors.phone }}</div>
                                </div>
                                <div class="flex justify-end">
                                    <button type="submit" :disabled="form.processing" class="px-4 py-2 bg-gray-800 text-white rounded-lg text-sm font-bold hover:bg-gray-900 transition">
                                        Simpan Kontak
                                    </button>
                                </div>
                            </form>
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
                            <UpdatePasswordForm />
                        </div>

                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
                            <DeleteUserForm />
                        </div>

                    </div>

                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template>