// navigation.js

const navigationStack = [];

function pushScreen(name, callback) {
  navigationStack.push({ name, callback });
  updateBackButton();
}

function popScreen() {
  return navigationStack.pop();
}

function updateBackButton() {
    const backButton = document.getElementById('back-button');
    if (!backButton) return;
    backButton.style.display = navigationStack.length > 1 ? 'block' : 'none';
}

window.goBack = function () {
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
