<script setup>
import { Link, usePage } from '@inertiajs/vue3';
import FlashMessage from '@/Components/FlashMessage.vue';
import { ref } from 'vue';

const page = usePage();
const showingSidebar = ref(false); // Untuk mobile
</script>

<template>
    <div class="py-6 bg-gray-100 min-h-screen">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 lg:mb-0 mb-12">
            <div class="flex flex-col md:flex-row gap-6">
        
                <div class="lg:hidden mb-2 sticky top-16 z-30 bg-gray-100/95 backdrop-blur-sm py-2 -mx-4 px-4 overflow-hidden">
                    <div class="flex overflow-x-auto gap-3 pb-2 hide-scrollbar">

                        <Link :href="route('admin.dashboard')"
                            class="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-full border text-sm font-medium transition-all shadow-sm"
                            :class="route().current('admin.dashboard')
                                ? 'bg-blue-800 text-white border-blue-800'
                                : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'">
                            <i class="fas fa-chart-line text-xs"></i>
                            <span>Dashboard</span>
                        </Link>

                        <Link :href="route('admin.categories.index')"
                            class="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-full border text-sm font-medium transition-all shadow-sm"
                            :class="route().current('admin.categories.*')
                                ? 'bg-blue-800 text-white border-blue-800'
                                : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'">
                            <i class="fas fa-tags text-xs"></i>
                            <span>Kategori</span>
                        </Link>

                        <Link :href="route('admin.reports.index')"
                            class="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-full border text-sm font-medium transition-all shadow-sm"
                            :class="route().current('admin.reports.*')
                                ? 'bg-blue-800 text-white border-blue-800'
                                : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'">
                            <i class="fas fa-exclamation-circle text-xs"></i>
                            <span>Laporan</span>

                            <span v-if="$page.props.pending_reports_count > 0"
                                class="ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full animate-pulse"
                                :class="route().current('admin.reports.*') ? 'bg-white text-blue-800' : 'bg-red-500 text-white'">
                                {{ $page.props.pending_reports_count }}
                            </span>
                        </Link>

                    </div>
                </div>

                <aside class="hidden lg:block w-1/4">
                    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden sticky top-24">

                        <div class="p-5 border-b border-gray-100 bg-gray-50">
                            <h2 class="font-bold text-lg text-gray-800 flex items-center gap-2">
                                <i class="fas fa-user-shield text-blue-600"></i> Admin Panel
                            </h2>
                        </div>

                        <nav class="flex flex-col p-3 space-y-1">

                            <Link :href="route('admin.dashboard')"
                                class="flex items-center w-full px-4 py-3 text-left rounded-lg transition-colors duration-200 group"
                                :class="route().current('admin.dashboard') ? 'bg-blue-50 text-blue-700 font-bold' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'">
                                <div class="w-8 flex justify-center mr-2">
                                    <i class="fas fa-chart-line text-lg"
                                        :class="route().current('admin.dashboard') ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-600'"></i>
                                </div>
                                Dashboard
                            </Link>

                            <Link :href="route('admin.categories.index')"
                                class="flex items-center w-full px-4 py-3 text-left rounded-lg transition-colors duration-200 group"
                                :class="route().current('admin.categories.*') ? 'bg-blue-50 text-blue-700 font-bold' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'">
                                <div class="w-8 flex justify-center mr-2">
                                    <i class="fas fa-tags text-lg"
                                        :class="route().current('admin.categories.*') ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-600'"></i>
                                </div>
                                Kategori Jasa
                            </Link>

                            <Link :href="route('admin.reports.index')"
                                class="flex items-center justify-between w-full px-4 py-3 text-left rounded-lg transition-colors duration-200 group"
                                :class="route().current('admin.reports.*') ? 'bg-blue-50 text-blue-700 font-bold' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'">

                                <div class="flex items-center">
                                    <div class="w-8 flex justify-center mr-2">
                                        <i class="fas fa-exclamation-circle text-lg"
                                            :class="route().current('admin.reports.*') ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-600'"></i>
                                    </div>
                                    <span>Laporan & Aduan</span>
                                </div>

                                <span v-if="$page.props.pending_reports_count > 0"
                                    class="text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm"
                                    :class="route().current('admin.reports.*') ? 'bg-blue-200 text-blue-800' : 'bg-red-500 text-white'">
                                    {{ $page.props.pending_reports_count }}
                                </span>
                            </Link>

                        </nav>
                    </div>
                </aside>

                <div class="w-full md:w-3/4">
                    <header class="h-10 flex items-center justify-between">
                        <h1 class="text-2xl font-bold text-gray-800">
                            {{ route().current('admin.dashboard') ? 'Dashboard Overview' : '' }}
                            {{ route().current('admin.categories.*') ? 'Manajemen Kategori' : '' }}
                            {{ route().current('admin.reports.*') ? 'Pusat Aduan' : '' }}
                        </h1>
                    </header>

                    <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 py-4">
                        <slot />
                    </main>
                </div>
            </div>
        </div>
    </div>
</template>
<style scoped>
/* Sembunyikan Scrollbar tapi tetap bisa di-scroll */
.hide-scrollbar::-webkit-scrollbar {
    display: none;
}
.hide-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
}
</style>