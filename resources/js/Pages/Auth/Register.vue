<script setup>
import InputError from '@/Components/InputError.vue';
import InputLabel from '@/Components/InputLabel.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import TextInput from '@/Components/TextInput.vue';
import { Head, Link, useForm } from '@inertiajs/vue3';

const form = useForm({
    name: '',
    email: '',
    password: '',
    password_confirmation: '',
});

const submit = () => {
    form.post(route('register'), {
        onFinish: () => form.reset('password', 'password_confirmation'),
    });
};
</script>

<template>
    <Head title="Daftar Akun Baru" />

    <div class="min-h-screen flex flex-col sm:justify-center items-center pt-6 sm:pt-0 bg-gray-50">
        
        <div class="my-6 text-center">
            <Link :href="route('welcome')" class="flex items-center gap-2">
                <div
                    class="h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-2xl">
                    F
                </div>
                <span class="font-bold text-2xl text-blue-600 tracking-tight">FindServices</span>
            </Link>
        </div>

        <div class="w-full sm:max-w-lg mt-2 p-12 bg-white shadow-xl shadow-gray-200/60 overflow-hidden sm:rounded-2xl border border-gray-100y">
                
                <div class="text-center">
                    <h2 class="text-3xl font-extrabold text-gray-900">Buat Akun Baru</h2>
                    <p class="mt-2 text-sm text-gray-600">
                        Sudah memiliki akun? 
                        <Link :href="route('login')" class="font-medium text-blue-600 hover:text-blue-500 hover:underline transition">
                            Masuk disini
                        </Link>
                    </p>
                </div>

                <form @submit.prevent="submit" class="mt-8 space-y-6">
                    
                    <div class="space-y-4">
                        <div>
                            <InputLabel for="name" value="Nama Lengkap" class="text-gray-700" />
                            <div class="mt-1 relative rounded-md shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <i class="fas fa-user text-gray-400"></i>
                                </div>
                                <TextInput
                                    id="name"
                                    type="text"
                                    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition"
                                    v-model="form.name"
                                    required
                                    autofocus
                                    autocomplete="name"
                                    placeholder="Nama Anda"
                                />
                            </div>
                            <InputError class="mt-2" :message="form.errors.name" />
                        </div>

                        <div>
                            <InputLabel for="email" value="Email Address" class="text-gray-700" />
                            <div class="mt-1 relative rounded-md shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <i class="fas fa-envelope text-gray-400"></i>
                                </div>
                                <TextInput
                                    id="email"
                                    type="email"
                                    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition"
                                    v-model="form.email"
                                    required
                                    autocomplete="username"
                                    placeholder="nama@email.com"
                                />
                            </div>
                            <InputError class="mt-2" :message="form.errors.email" />
                        </div>

                        <div>
                            <InputLabel for="password" value="Password" class="text-gray-700" />
                            <div class="mt-1 relative rounded-md shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <i class="fas fa-lock text-gray-400"></i>
                                </div>
                                <TextInput
                                    id="password"
                                    type="password"
                                    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition"
                                    v-model="form.password"
                                    required
                                    autocomplete="new-password"
                                    placeholder="Minimal 8 karakter"
                                />
                            </div>
                            <InputError class="mt-2" :message="form.errors.password" />
                        </div>

                        <div>
                            <InputLabel for="password_confirmation" value="Konfirmasi Password" class="text-gray-700" />
                            <div class="mt-1 relative rounded-md shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <i class="fas fa-check-circle text-gray-400"></i>
                                </div>
                                <TextInput
                                    id="password_confirmation"
                                    type="password"
                                    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition"
                                    v-model="form.password_confirmation"
                                    required
                                    autocomplete="new-password"
                                    placeholder="Ulangi password"
                                />
                            </div>
                            <InputError class="mt-2" :message="form.errors.password_confirmation" />
                        </div>
                    </div>

                    <div class="text-xs text-gray-500 text-center">
                        Dengan mendaftar, Anda menyetujui <a href="#" class="text-blue-600 hover:underline">Syarat & Ketentuan</a> serta <a href="#" class="text-blue-600 hover:underline">Kebijakan Privasi</a> kami.
                    </div>

                    <div>
                        <PrimaryButton
                            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all transform hover:-translate-y-0.5"
                            :class="{ 'opacity-25': form.processing }"
                            :disabled="form.processing"
                        >
                            Daftar Akun Baru
                        </PrimaryButton>
                    </div>

                </form>
            </div>

        <div class="my-6 text-center text-xs text-gray-400">
            &copy; {{ new Date().getFullYear() }} FindServices Marketplace. All rights reserved.
        </div>
    </div>
</template>