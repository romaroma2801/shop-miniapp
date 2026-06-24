// navigation.js - Умная навигация с синхронизацией футера

const navigationStack = [];
let isNavigating = false;

// Глобальное состояние
window.currentFooterSection = 'home';
window.isRestoring = false;

/**
 * Добавить экран в стек навигации
 * @param {string} name - Имя экрана
 * @param {string} footerSection - Какая вкладка футера должна быть активна
 */
window.pushScreen = function(name, footerSection = null) {
    if (window.isRestoring) return; // Не добавляем в стек при восстановлении
    
    const section = footerSection || window.currentFooterSection;
    navigationStack.push({ name, footerSection: section });
    
    console.log(`→ push: ${name}, стек: [${navigationStack.map(s => s.name).join(', ')}]`);
    updateBackButton();
};

/**
 * Удалить последний экран из стека
 */
function popScreen() {
    if (navigationStack.length > 1) {
        return navigationStack.pop();
    }
    return null;
}

/**
 * Обновить видимость кнопки "Назад"
 */
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

/**
 * Вернуться на предыдущий экран
 */
window.goBack = function() {
    if (isNavigating) return;
    isNavigating = true;
    
    console.log(`goBack вызван, стек: [${navigationStack.map(s => s.name).join(', ')}]`);
    
    const previous = popScreen();
    
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
            
            // Вызываем глобальную функцию восстановления экрана
            if (window.restoreScreen && typeof window.restoreScreen === 'function') {
                window.restoreScreen(target.name);
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
window.popScreen = popScreen;
window.updateBackButton = updateBackButton;
