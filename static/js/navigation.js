// navigation.js
const navigationStack = [];
let isNavigating = false;

function pushScreen(name, callback, footerSection = null) {
    console.log("→ push:", name, "callback is", typeof callback);
    
    // Если это не восстановление состояния, добавляем в стек
    if (!window.isRestoring) {
        navigationStack.push({ 
            name, 
            callback,
            footerSection: footerSection || window.currentFooterSection || 'catalog'
        });
    }
    
    updateBackButton();
}

function popScreen() {
    if (navigationStack.length > 1) {
        return navigationStack.pop();
    }
    return null;
}

function updateBackButton() {
    const backButton = document.getElementById('back-button');
    if (!backButton) return;
    
    const visible = navigationStack.length > 1;
    backButton.style.display = visible ? 'block' : 'none';
    
    // Синхронизируем с Telegram WebApp
    if (window.Telegram?.WebApp) {
        if (visible) {
            window.Telegram.WebApp.BackButton.show();
        } else {
            window.Telegram.WebApp.BackButton.hide();
        }
    }
}

window.isRestoring = false;
window.currentFooterSection = 'home';

window.goBack = function() {
    if (isNavigating) return;
    isNavigating = true;
    
    const previous = popScreen();
    console.log("goBack вызван, стек:", navigationStack.map(s => s.name));
    
    if (previous && navigationStack.length > 0) {
        const target = navigationStack[navigationStack.length - 1];
        
        try {
            window.isRestoring = true;
            
            // Восстанавливаем футер
            if (target.footerSection) {
                window.currentFooterSection = target.footerSection;
                if (window.setActiveFooter) {
                    window.setActiveFooter(target.footerSection);
                }
            }
            
            // Вызываем callback предыдущего экрана
            if (typeof target.callback === 'function') {
                target.callback();
            }
            
        } catch (e) {
            console.error("Ошибка при возврате к экрану:", target.name, e);
        } finally {
            window.isRestoring = false;
            isNavigating = false;
        }
    } else {
        // Если стек пуст, возвращаемся на главную
        console.warn("goBack: стек пуст, вызываем showHome");
        if (window.showHome) {
            window.showHome();
        }
        isNavigating = false;
    }
};

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    // Telegram WebApp
    if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.ready();
        
        // Обработчик кнопки "Назад" из Telegram
        window.Telegram.WebApp.BackButton.onClick(() => {
            window.goBack();
        });
        
        // Очистка при закрытии
        window.addEventListener('beforeunload', () => {
            window.Telegram.WebApp.BackButton.offClick(window.goBack);
        });
    }
    
    // HTML кнопка "Назад"
    const backButton = document.getElementById('back-button');
    if (backButton) {
        backButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.goBack();
        });
    }
});

// Делаем функции доступными глобально
window.pushScreen = pushScreen;
window.popScreen = popScreen;
window.updateBackButton = updateBackButton;
