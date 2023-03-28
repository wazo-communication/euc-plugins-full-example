import app from 'https://cdn.jsdelivr.net/npm/@wazo/euc-plugins-sdk@latest/lib/esm/app.js';

let session;

const url = 'http://localhost:8088';

const onLoaded = async () => {
  const string = document.getElementById("hello");
  const hello = await getHello(url);
  string.value = hello.name;

  const saveButton = document.getElementById("save");
  saveButton.addEventListener('click', async (e) => {
    e.preventDefault();
    await saveHello(url, string.value);
    alert('saved');
  });
}

const getHello = async (url) => {
  const options = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Token': session.token,
      'X-Auth-Origin': 'admin'
    }
  }

  return fetch(`${url}/hello`, options).then(response => response.json());
}

const saveHello = async (url, string) => {
  const data = {
    name: string
  }

  const options = {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Token': session.token,
      'X-Auth-Origin': 'admin'
    }
  }

  return fetch(`${url}/hello`, options).then(response => response.json());
}

(async () => {
  await app.initialize();
  const context = app.getContext();
  session = context.user;
  await onLoaded();
})();
