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


window.isRestoring = false;

window.goBack = function () {
  const previous = popScreen();
  console.log("goBack вызван, стек:", navigationStack.map(s => s.name));

  if (previous && typeof previous.callback === 'function') {
    try {
      window.isRestoring = true;
      previous.callback();
    } catch (e) {
      console.error("Ошибка при возврате к экрану:", previous.name, e);
      // только при ошибке: showHome()
    } finally {
      window.isRestoring = false;
    }
  } else {
    console.warn("goBack: стек пуст, вызываем showHome");
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
