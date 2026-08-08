import ws from 'k6/ws';
import http from 'k6/http';
import { check } from 'k6';
import execution from 'k6/execution'; // Import modul execution

export const options = {
  vus: 1,         // 1 User (Serial)
  iterations: 3,  // 3 Kali putaran (Untuk tes Simple, Review, Booking)
};

// --- CONFIG ---
const APP_KEY = 'icocmarononizhhl5c3r'; // App Key Anda (dari log sebelumnya)
const WS_HOST = 'localhost';
const WS_PORT = '8080';
const API_URL = 'http://127.0.0.1:8000/api/test-latency';

const SCENARIOS = ['simple', 'review', 'booking'];

export default function () {
  // LOGIC BARU: Pilih skenario berdasarkan urutan iterasi (0, 1, 2)
  const iterIndex = execution.scenario.iterationInTest;
  const currentScenario = SCENARIOS[iterIndex % SCENARIOS.length];
  
  const url = `ws://${WS_HOST}:${WS_PORT}/app/${APP_KEY}?protocol=7&client=js&version=8.4.0&flash=false`;

  console.log(`[Iterasi ${iterIndex + 1}] Menjalankan Skenario: ${currentScenario.toUpperCase()}`);

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
        // Kirim payload tipe skenario ke API
        const payload = JSON.stringify({ type: currentScenario });
        const params = { headers: { 'Content-Type': 'application/json' } };
        
        http.post(API_URL, payload, params);
      }

      if (msg.event.includes('TestLatency')) {
        const data = JSON.parse(msg.data);
        
        // Pastikan tipe datanya cocok
        if (data.type === currentScenario) {
            const latency = Date.now() - data.sent_at;
            const size = message.length; // Ukuran data dalam bytes
            
            console.log(`✅ [${currentScenario.toUpperCase()}] Latency: ${latency.toFixed(2)} ms | Size: ${size} bytes`);
            
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

    // Timeout safety
    socket.setTimeout(function () {
        console.log('Timeout..');
        socket.close();
    }, 10000); // Saya naikkan jadi 10 detik jaga-jaga API lambat
  });
}