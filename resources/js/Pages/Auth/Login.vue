<script setup>
import Checkbox from '@/Components/Checkbox.vue';
import InputError from '@/Components/InputError.vue';
import InputLabel from '@/Components/InputLabel.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import TextInput from '@/Components/TextInput.vue';
import { Head, Link, useForm } from '@inertiajs/vue3';

defineProps({
    canResetPassword: {
        type: Boolean,
    },
    status: {
        type: String,
    },
});

const form = useForm({
    email: '',
    password: '',
    remember: false,
});

const submit = () => {
    form.post(route('login'), {
        onFinish: () => form.reset('password'),
    });
};
</script>

<template>
    <Head title="Masuk Akun" />

    <div class="min-h-screen flex items-center justify-center bg-gray-50 py-16 px-4 sm:px-6 lg:px-8">
        <div class="absolute top-20 text-center lg:hidden">
            <Link :href="route('welcome')" class="flex items-center gap-2">
                <div
                    class="h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-2xl">
                    F
                </div>
                <span class="font-bold text-2xl text-blue-600 tracking-tight">FindServices</span>
            </Link>
        </div>

        <div class="flex w-full max-w-5xl bg-gray-50 rounded-2xl overflow-hidden min-h-[600px]">
            
            <div class="hidden lg:flex w-1/2 bg-gray-50 relative items-center justify-center p-12">
                
                <div class="absolute top-8 left-8">
                    <Link :href="route('welcome')" class="flex items-center gap-2">
                        <div class="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-sm">
                            F
                        </div>
                        <span class="font-bold text-xl text-blue-600 tracking-tight">FindServices</span>
                    </Link>
                </div>

                <div class="text-center">
                    <img src="Gemini_Generated_Image_v1a139v1a139v1a123.png" 
                         alt="Ilustrasi Jasa" 
                         class="w-full h-auto max-h-[300px] object-contain mx-auto mb-8 drop-shadow-md animate-fade-in-up">
                    
                    <h2 class="text-2xl font-extrabold text-gray-800 mb-3 leading-tight">
                        Jual Beli Jasa <br>Jadi Lebih Mudah
                    </h2>
                    
                    <p class="text-gray-500 text-base leading-relaxed max-w-xs mx-auto">
                        Temukan penyedia jasa profesional untuk segala kebutuhan rumah dan bisnis Anda.
                    </p>
                </div>
            </div>

            <div class="w-full lg:w-1/2 flex items-center justify-center p-8 relative bg-white shadow-xl shadow-gray-200/60 overflow-hidden sm:rounded-2xl border border-gray-100y">
                
                <div class="absolute top-10 right-6 lg:hidden">
                    <Link :href="route('welcome')" class="text-gray-400 hover:text-gray-600 transition flex items-center gap-2 text-sm font-medium">
                        <i class="fas fa-arrow-left"></i> Kembali
                    </Link>
                </div>

                <div class="w-full max-w-sm space-y-6">
                    
                    <div class="text-left mb-8">
                        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Masuk</h2>
                        <p class="mt-2 text-sm text-gray-500">
                            Silakan masuk dengan akun yang terdaftar.
                        </p>
                    </div>

                    <form @submit.prevent="submit" class="space-y-5">

                        <div v-if="status" class="p-4 mb-4 text-sm text-green-700 bg-green-100 rounded-lg border border-green-200" role="alert">
                            {{ status }}
                        </div>

                        <div>
                            <InputLabel for="email" value="Email Address" class="text-gray-700 font-semibold mb-1" />
                            <TextInput
                                id="email"
                                type="email"
                                class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition shadow-sm placeholder-gray-400 sm:text-sm"
                                v-model="form.email"
                                required
                                autofocus
                                autocomplete="username"
                                placeholder="nama@email.com"
                            />
                            <InputError class="mt-1" :message="form.errors.email" />
                        </div>

                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <InputLabel for="password" value="Kata Sandi" class="text-gray-700 font-semibold" />
                            </div>
                            <TextInput
                                id="password"
                                type="password"
                                class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition shadow-sm placeholder-gray-400 sm:text-sm"
                                v-model="form.password"
                                required
                                autocomplete="current-password"
                                placeholder="••••••••"
                            />
                            <InputError class="mt-1" :message="form.errors.password" />
                        </div>

                        <div class="flex items-center justify-between">
                            <div class="flex items-center">
                                <Checkbox name="remember" v-model:checked="form.remember" />
                                <span class="ml-2 text-sm text-gray-600">Ingat saya</span>
                            </div>

                            <Link
                                v-if="canResetPassword"
                                :href="route('password.request')"
                                class="text-sm font-bold text-blue-600 hover:text-blue-500 hover:underline"
                            >
                                Lupa Kata Sandi?
                            </Link>
                        </div>

                        <PrimaryButton
                            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200 transition-all"
                            :class="{ 'opacity-70 cursor-not-allowed': form.processing }"
                            :disabled="form.processing"
                        >
                            Masuk Akun
                        </PrimaryButton>
                        
                        <div class="relative py-2">
                            <div class="absolute inset-0 flex items-center">
                                <div class="w-full border-t border-gray-200"></div>
                            </div>
                            <div class="relative flex justify-center text-xs uppercase">
                                <span class="px-2 bg-white text-gray-400">Atau masuk dengan</span>
                            </div>
                        </div>

                        <button type="button" class="w-full flex items-center justify-center px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-bold text-gray-700 hover:bg-gray-50 transition">
                            <img src="https://www.svgrepo.com/show/475656/google-color.svg" class="h-5 w-5 mr-2" alt="Google Logo">
                            Google
                        </button>

                        <p class="text-center text-sm text-gray-600 mt-6 pt-4 border-t border-gray-100">
                            Belum punya akun? 
                            <Link :href="route('register')" class="font-bold text-blue-600 hover:text-blue-500 hover:underline transition">
                                Daftar Sekarang
                            </Link>
                        </p>

                    </form>
                </div>
            </div>
        </div>
    </div>
    <div class="my-6 text-center text-xs text-gray-400">
        &copy; {{ new Date().getFullYear() }} FindServices Marketplace. All rights reserved.
    </div>
</template>

<style scoped>
/* Animasi halus saat gambar muncul */
.animate-fade-in-up {
    animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>