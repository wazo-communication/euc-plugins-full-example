import app from 'https://cdn.jsdelivr.net/npm/@wazo/euc-plugins-sdk@latest/lib/esm/app.js';

const url = '';

app.onLoaded = async () => {
  console.log('Example loaded', stack);

  if (stack) {
    const hello = await getHello(url);
    console.log(conference);

    const saveButton = document.getElementById("save");
    saveButton.addEventListener('click', async (e) => {
      e.preventDefault();
      console.log(e);
      const string = document.getElementById("hello").value;
      console.log(string);
      await saveHello(url, string);
    });
  }
};

const getHello = async (url) => {
  const options = {
    method: 'GET',
  }

  return fetch(`https://${url}/example/api/hello`, options).then(response => response.json());
}

const saveHello = async (url, string) => {
  const data = {
    hello: string
  }

  const options = {
    method: 'POST',
    body: JSON.stringify(data)
  }

  return fetch(`https://${url}/example/api/hello`, options).then(response => response.json());
}

(async () => {
  await app.initialize();
  const context = app.getContext();
  session = context.user;
  console.log(session);
})();
