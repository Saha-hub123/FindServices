<script setup>
import ApplicationLogo from '@/Components/ApplicationLogo.vue';
import { Link } from '@inertiajs/vue3';
</script>

<template>
    <div
        class="flex min-h-screen flex-col items-center bg-gray-50 pt-6 sm:justify-center sm:pt-0 dark:bg-gray-900"
    >
        <div>
            <Link :href="route('welcome')" class="flex items-center gap-2">
                <div
                    class="h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-2xl">
                    F
                </div>
                <span class="font-bold text-2xl text-blue-600 tracking-tight">FindServices</span>
            </Link>
        </div>

        <div
            class="mt-6 w-full overflow-hidden bg-white px-6 py-4 shadow-md sm:max-w-md sm:rounded-lg dark:bg-gray-800"
        >
            <slot />
        </div>
    </div>
</template>
