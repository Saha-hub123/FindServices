<script setup>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps({
  labels: Array,
  data: Array
})

const chartData = {
  labels: props.labels,
  datasets: [
    {
      label: 'Jumlah Pesanan',
      backgroundColor: 'rgba(59, 130, 246, 0.2)', // Biru transparan
      borderColor: '#3b82f6', // Biru Solid
      pointBackgroundColor: '#fff',
      pointBorderColor: '#3b82f6',
      borderWidth: 2,
      fill: true,
      data: props.data,
      tension: 0.4 // Membuat garis melengkung (smooth)
    }
  ]
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false } // Sembunyikan legend jika cuma 1 data
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { borderDash: [2, 2] }
    },
    x: {
      grid: { display: false }
    }
  }
}
</script>

<template>
  <Line :data="chartData" :options="chartOptions" />
</template>