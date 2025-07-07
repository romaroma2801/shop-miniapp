// navigation.js

const navigationStack = [];

function pushScreen(name, callback) {
  console.log("→ push:", name, "callback is", typeof callback);
  navigationStack.push({ name, callback });
  updateBackButton();
}


function popScreen() {
  return navigationStack.pop();
}

function updateBackButton() {
    const backButton = document.getElementById('back-button');
    if (!backButton) return;

    const visible = navigationStack.length > 1;
    console.log("Кнопка назад:", visible ? "показана" : "скрыта");

    backButton.style.display = visible ? 'block' : 'none';
}


window.goBack = function () {
  console.log("goBack вызван, стек:", navigationStack.map(s => s.name));
  const previous = popScreen();
  if (previous && typeof previous.callback === 'function') {
    try {
      previous.callback();
    } catch (e) {
      console.error("Ошибка при возврате к экрану:", previous.name, e);
      showHome();
    }
  } else {
    showHome();
  }
};


document.addEventListener('DOMContentLoaded', () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.BackButton.onClick(goBack);

    window.addEventListener('beforeunload', () => {
      window.Telegram.WebApp.BackButton.offClick(goBack);
    });
  }

  const backButton = document.getElementById('back-button');
  if (backButton) {
    backButton.addEventListener('click', goBack);
  }
});
