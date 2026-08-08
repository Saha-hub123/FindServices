import ws from 'k6/ws';
import http from 'k6/http';
import { check } from 'k6';
import execution from 'k6/execution';
import { Trend } from 'k6/metrics'; // Import Trend

// --- MEMBUAT METRIK KHUSUS ---
// Ini akan mencatat statistik terpisah untuk setiap skenario
const trendSimple = new Trend('latency_simple');
const trendReview = new Trend('latency_review');
const trendBooking = new Trend('latency_booking');

export const options = {
  vus: 1,
  // Kita jalankan 30 kali (10 Simple, 10 Review, 10 Booking)
  // Agar mendapatkan rata-rata yang valid
  iterations: 30, 
};

// --- CONFIG ---
const APP_KEY = 'icocmarononizhhl5c3r'; // Sesuaikan App Key
const WS_HOST = 'localhost';
const WS_PORT = '8080';
const API_URL = 'http://127.0.0.1:8000/api/test-latency';

const SCENARIOS = ['simple', 'review', 'booking'];

export default function () {
  const iterIndex = execution.scenario.iterationInTest;
  const currentScenario = SCENARIOS[iterIndex % SCENARIOS.length];
  
  const url = `ws://${WS_HOST}:${WS_PORT}/app/${APP_KEY}?protocol=7&client=js&version=8.4.0&flash=false`;

  const response = ws.connect(url, {}, function (socket) {
    socket.on('open', function open() {
      socket.send(JSON.stringify({
        event: 'pusher:subscribe',
        data: { channel: 'test-channel' }
      }));
    });

    socket.on('message', function (message) {
      const msg = JSON.parse(message);

      if (msg.event === 'pusher_internal:subscription_succeeded') {
        const payload = JSON.stringify({ type: currentScenario });
        const params = { headers: { 'Content-Type': 'application/json' } };
        http.post(API_URL, payload, params);
      }

      if (msg.event.includes('TestLatency')) {
        const data = JSON.parse(msg.data);
        
        if (data.type === currentScenario) {
            const latency = Date.now() - data.sent_at;
            
            // --- INPUT DATA KE METRIK STATISTIK ---
            if (currentScenario === 'simple') trendSimple.add(latency);
            if (currentScenario === 'review') trendReview.add(latency);
            if (currentScenario === 'booking') trendBooking.add(latency);
            
            check(latency, { 'Latency < 500ms': (l) => l < 500 });
            socket.close();
        }
      }
    });

    socket.on('error', (e) => socket.close());
    socket.setTimeout(() => socket.close(), 10000);
  });
}