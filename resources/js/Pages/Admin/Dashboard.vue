<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head } from '@inertiajs/vue3';
import LineChart from '@/Components/Charts/LineChart.vue';
import DoughnutChart from '@/Components/Charts/DoughnutChart.vue';

const props = defineProps({
    stats: Object,
    charts: Object
});
</script>

<template>
    <Head title="Admin Dashboard" />

    <AuthenticatedLayout>
        <AdminLayout>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div class="p-3 rounded-full bg-blue-50 text-blue-600 mr-4">
                        <i class="fas fa-users text-xl"></i>
                    </div>
                    <div>
                        <p class="text-xs text-gray-500 font-bold uppercase">Total User</p>
                        <p class="text-xl font-bold text-gray-800">{{ stats.users }}</p>
                    </div>
                </div>
                
                <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div class="p-3 rounded-full bg-green-50 text-green-600 mr-4">
                        <i class="fas fa-shopping-bag text-xl"></i>
                    </div>
                    <div>
                        <p class="text-xs text-gray-500 font-bold uppercase">Total Pesanan</p>
                        <p class="text-xl font-bold text-gray-800">{{ stats.bookings }}</p>
                    </div>
                </div>

                <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div class="p-3 rounded-full bg-purple-50 text-purple-600 mr-4">
                        <i class="fas fa-briefcase text-xl"></i>
                    </div>
                    <div>
                        <p class="text-xs text-gray-500 font-bold uppercase">Jasa Aktif</p>
                        <p class="text-xl font-bold text-gray-800">{{ stats.services }}</p>
                    </div>
                </div>

                <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div class="p-3 rounded-full bg-red-50 text-red-600 mr-4">
                        <i class="fas fa-exclamation-triangle text-xl"></i>
                    </div>
                    <div>
                        <p class="text-xs text-gray-500 font-bold uppercase">Aduan Pending</p>
                        <p class="text-xl font-bold text-gray-800">{{ stats.reports }}</p>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                
                <div class="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 class="font-bold text-gray-800 mb-4">Tren Pesanan (6 Bulan Terakhir)</h3>
                    <div class="h-64">
                        <LineChart 
                            :labels="charts.bookings.labels" 
                            :data="charts.bookings.data" 
                        />
                    </div>
                </div>

                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 class="font-bold text-gray-800 mb-4">Top 5 Kategori Jasa</h3>
                    <div class="h-64 relative">
                        <DoughnutChart 
                            :labels="charts.categories.labels" 
                            :data="charts.categories.data" 
                        />
                    </div>
                </div>
            </div>

            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 class="font-bold text-gray-800 mb-4">Distribusi Status Laporan</h3>
                <div class="flex items-end gap-4 h-32 border-b border-gray-200 pb-2">
                    <div class="w-1/3 flex flex-col justify-end group">
                        <div class="bg-yellow-400 rounded-t-lg w-full transition-all duration-500 group-hover:bg-yellow-500 relative flex justify-center"
                             :style="`height: ${Math.max(15, (charts.reports.data[0] / (charts.reports.data.reduce((a, b) => a + b, 0) || 1)) * 100)}%`">
                             <span class="text-xs font-bold text-white mt-2">{{ charts.reports.data[0] }}</span>
                        </div>
                        <p class="text-center text-xs mt-2 font-semibold text-gray-600">Pending</p>
                    </div>
                    
                    <div class="w-1/3 flex flex-col justify-end group">
                        <div class="bg-green-500 rounded-t-lg w-full transition-all duration-500 group-hover:bg-green-600 relative flex justify-center"
                             :style="`height: ${Math.max(15, (charts.reports.data[1] / (charts.reports.data.reduce((a, b) => a + b, 0) || 1)) * 100)}%`">
                             <span class="text-xs font-bold text-white mt-2">{{ charts.reports.data[1] }}</span>
                        </div>
                        <p class="text-center text-xs mt-2 font-semibold text-gray-600">Selesai</p>
                    </div>

                    <div class="w-1/3 flex flex-col justify-end group">
                        <div class="bg-red-500 rounded-t-lg w-full transition-all duration-500 group-hover:bg-red-600 relative flex justify-center"
                             :style="`height: ${Math.max(15, (charts.reports.data[2] / (charts.reports.data.reduce((a, b) => a + b, 0) || 1)) * 100)}%`">
                             <span class="text-xs font-bold text-white mt-2">{{ charts.reports.data[2] }}</span>
                        </div>
                        <p class="text-center text-xs mt-2 font-semibold text-gray-600">Ditolak</p>
                    </div>
                </div>
            </div>

        </AdminLayout>
    </AuthenticatedLayout>
</template>