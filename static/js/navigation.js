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

  if (navigationStack.length > 1) {
    backButton.style.display = 'block';
  } else {
    backButton.style.display = 'none';
  }
}

window.goBack = function () {
  const previousScreen = popScreen();

  if (previousScreen && typeof window[`show${previousScreen}`] === 'function') {
    window[`show${previousScreen}`]();
  } else {
    // Если нет куда вернуться — закрываем приложение
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.close();
    } else {
      window.location.href = '/';
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  // Telegram WebApp BackButton
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.BackButton.onClick(goBack);

    window.addEventListener('beforeunload', () => {
      window.Telegram.WebApp.BackButton.offClick(goBack);
    });
  }

  // Обработчик клика на нашу кнопку "Назад"
  const backButton = document.getElementById('back-button');
  if (backButton) {
    backButton.addEventListener('click', goBack);
  }
});
