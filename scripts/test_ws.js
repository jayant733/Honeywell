const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

ws.on('open', function open() {
  console.log('Connected to ws://localhost:8000/ws/telemetry');
});

ws.on('message', function incoming(data) {
  console.log('Received data: ', data.toString());
  process.exit(0);
});

ws.on('error', function error(err) {
  console.log('WebSocket Error: ', err);
  process.exit(1);
});

setTimeout(() => {
  console.log('Timeout waiting for message');
  process.exit(1);
}, 5000);
