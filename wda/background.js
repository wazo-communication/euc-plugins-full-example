import app from 'https://cdn.jsdelivr.net/npm/@wazo/euc-plugins-sdk@latest/lib/esm/app.js';
import ReconnectingWebSocket from 'https://cdn.jsdelivr.net/npm/reconnecting-websocket@4.4.0/dist/reconnecting-websocket-mjs.js';

//const url = window.location.origin.replace('http', 'ws');
const url = 'ws://localhost:8088';
let currentCall;


const websocketHello = (token) => {
  const ws = new ReconnectingWebSocket(`${url}/ws`);
  ws.addEventListener('open', (event) => {
    console.log('hello background - websocket connected');
    ws.send(JSON.stringify({
      "X-Auth-Token": token
    }));
  });
  ws.addEventListener('close', (event) => {
    console.log('hello background - websocket disconnected');
  });
  ws.addEventListener('message', notificationParticipants);
}

const notificationParticipants = (e) => {
  const data = JSON.parse(e.data);
  if (['call_created', 'call_answered', 'call_ended'].includes(data.name)) {
    app.sendMessageToIframe({ event: data.name, data: data.data });
    if (data.name === "call_created") {
      if (data.data.conversation_id != currentCall) {
        currentCall = data.data.conversation_id;
        sendNotificationUser(data.data.caller_id_name);
      }
    }
  }
}

const sendNotificationUser = (name) => {
  const textAlert = `New call! Hello ${name} :)`;
  app.displayNotification("Hello!", textAlert);
}

app.onAppUnLoaded = (tabId) => {
  app.openLeftPanel();
}

(async () => {
  await app.initialize();
  const context = app.getContext();
  const token = context.user.token;

  websocketHello(token);
})();
