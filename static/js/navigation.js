// navigation.js

const navigationStack = [];

function pushScreen(screenName) {
  navigationStack.push(screenName);
  updateBackButton();
}

function popScreen() {
  if (navigationStack.length > 1) {
    navigationStack.pop(); // Удаляем текущий экран
    return navigationStack[navigationStack.length - 1]; // Возвращаем предыдущий
  }
  return null;
}

function updateBackButton() {
    const backButton = document.getElementById('back-button');
    if (!backButton) return;
    backButton.style.display = navigationStack.length > 1 ? 'block' : 'none';
}

window.goBack = function () {
    const previousScreen = popScreen();

    if (previousScreen && typeof window[`show${previousScreen}`] === 'function') {
        try {
            window[`show${previousScreen}`]();
        } catch (e) {
            console.error("Ошибка при возврате к экрану:", previousScreen, e);
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
