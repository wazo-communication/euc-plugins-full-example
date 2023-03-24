import app from 'https://cdn.jsdelivr.net/npm/@wazo/euc-plugins-sdk@latest/lib/esm/app.js';
import 'https://cdn.jsdelivr.net/npm/@wazo/sdk';

let session;

const url = window.location.origin;

const hello = document.getElementById('hello');
const caller = document.getElementById('caller');

app.onIframeMessage = async (msg) => {
  if (msg.event === 'call_answered') {
    changeCaller(`${msg.data.peer_caller_id_name} (${msg.data.peer_caller_id_number})`);
  }
  if (msg.event === 'call_ended') {
    const data = await getHello();
    if (data.items.length === 0) {
      changeCaller();
    }
  }
}

const changeCaller = (data) => {
    if (!data) {
      data = 'Nobody';
    }
    caller.textContent = `In call with: ${data}`;
}

const changeHello = (data) => {
    hello.textContent = data;
}

const getHello = async () => {
  const options = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Token': session.token
    }
  }

  return fetch(`${url}/calls`, options).then(response => response.json());
}

const appLoaded = () => {
  const data = { type: 'hello/APP_LOADED' };
  window.top.postMessage(data, '*')
}

(async () => {
  await app.initialize();
  const context = app.getContext();
  session = context.user;

  Wazo.Auth.setHost(session.host);
  Wazo.Auth.setApiToken(session.token);

  const me = await Wazo.api.confd.getUser(session.uuid);
  changeHello(`Hello, ${me.firstName} ${me.lastName}!`);

  const data = await getHello();
  const firstCaller = data?.items[0];
  if (firstCaller) {
      const displayCaller = `${firstCaller.peer_caller_id_name} (${firstCaller.peer_caller_id_number})`;
      changeCaller(displayCaller);
  } else {
      changeCaller();
  }

  appLoaded();
  app.closeLeftPanel();
})();
