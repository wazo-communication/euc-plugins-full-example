import app from 'https://cdn.jsdelivr.net/npm/@wazo/euc-plugins-sdk@latest/lib/esm/app.js';

let session;

const url = 'quintana.wazo.community';
const appColor = '#8e6a3a';

app.onIframeMessage = (msg) => {
  if (['conference_participant_left', 'conference_participant_joined'].includes(msg.event)) {
    updateParticipants();
  }
}

const getHello = async () => {
  const options = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Token': session.token
    }
  }

  return fetch(`https://${url}/hackathon/api/coffee`, options).then(response => response.json());
}

const appLoaded = () => {
  const data = { type: 'coffee/APP_LOADED' };
  window.top.postMessage(data, '*')
}

(async () => {
  await app.initialize();
  const context = app.getContext();
  session = context.user;

  app.closeLeftPanel();
  app.changeNavBarColor(appColor);

  getHello();
  appLoaded();
})();
