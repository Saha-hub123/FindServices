import ws from 'k6/ws';
import http from 'k6/http';
import { check, sleep } from 'k6';

// Kita tes 3 user masing-masing menjalankan skenario berbeda
export const options = {
  vus: 1, 
  iterations: 3, 
};

// --- CONFIG ---
const APP_KEY = 'icocmarononizhhl5c3r'; // <--- JANGAN LUPA
const WS_HOST = 'localhost';
const WS_PORT = '8080';
const API_URL = 'http://127.0.0.1:8000/api/test-latency';

// Daftar Skenario yang mau dites
const SCENARIOS = ['simple', 'review', 'booking'];

export default function () {
  // Pilih skenario berdasarkan urutan user (VU)
  // VU 1 -> simple, VU 2 -> review, VU 3 -> booking
  const currentScenario = SCENARIOS[(__VU - 1) % SCENARIOS.length];
  
  const url = `ws://${WS_HOST}:${WS_PORT}/app/${APP_KEY}?protocol=7&client=js&version=8.4.0&flash=false`;

  console.log(`[VU ${__VU}] Menjalankan Skenario: ${currentScenario}`);

  const response = ws.connect(url, {}, function (socket) {
    
    socket.on('open', function open() {
      // Subscribe
      socket.send(JSON.stringify({
        event: 'pusher:subscribe',
        data: { channel: 'test-channel' }
      }));
    });

    socket.on('message', function (message) {
      const msg = JSON.parse(message);

      // 1. Setelah Subscribe Sukses -> Tembak API sesuai Tipe
      if (msg.event === 'pusher_internal:subscription_succeeded') {
        
        // Payload API request
        const payload = JSON.stringify({ type: currentScenario });
        const params = { headers: { 'Content-Type': 'application/json' } };
        
        http.post(API_URL, payload, params);
      }

      // 2. Tangkap Event
      if (msg.event.includes('TestLatency')) {
        const data = JSON.parse(msg.data);
        
        // Filter: Pastikan kita menangkap event milik kita sendiri (sesuai tipe)
        if (data.type === currentScenario) {
            const latency = Date.now() - data.sent_at;
            
            console.log(`✅ [${currentScenario.toUpperCase()}] Latency: ${latency.toFixed(2)} ms | Size: ${message.length} bytes`);
            
            check(latency, {
                'Latency Aman (< 500ms)': (l) => l < 500,
            });

            socket.close();
        }
      }
    });

    socket.on('error', function (e) {
      console.error('Error:', e);
      socket.close();
    });

    socket.setTimeout(function () {
        console.log(`[VU ${__VU}] Timeout..`);
        socket.close();
    }, 5000);
  });
}