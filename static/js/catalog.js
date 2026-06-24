// catalog.js - Исправленный каталог

// Глобальные переменные
let catalog = {};
const categoryIcons = {
    "Парогенераторы": "vape.png",
    "Жидкости": "juice.png",
    "Жидкости для вейпа": "juice.png",
    "Запчасти и комплектующие": "spanner.png",
    "Кальяны и комплектующие": "hookah.png",
    "Самозамес": "test.png",
    "Уценённый товар": "sale.png",
    "Уценённые Парогенераторы": "sale.png"
};

// Кэш для подкатегорий и текущие данные
const subCache = [];
let productViewData = [];
let selectedOptionName = '';
let selectedOptionImage = '';

/**
 * Точка входа: инициализация страницы каталога
 */
window.initCatalogPage = function() {
    window.currentFooterSection = 'catalog';
    if (window.setActiveFooter) window.setActiveFooter('catalog');
    
    // Создаем структуру, если её нет
    const contentEl = document.getElementById('content');
    if (contentEl) {
        contentEl.innerHTML = `
            <div class="header">
                <img src="/static/logo22.png" alt="Логотип" class="logo">
            </div>
            <div id="loader" class="loader" style="display: none;">
                <img src="/static/Eicon.png" alt="Загрузка...">
            </div>
            <div id="catalog-container"></div>
        `;
    }
    
    loadCatalog();
};

/**
 * Загрузка данных с сервера
 */
async function loadCatalog() {
    showLoader(true);
    try {
        const response = await fetch("/api/catalog");
        if (!response.ok) throw new Error('Network error');
        catalog = await response.json();
        showLoader(false);
        renderMainCategories();
    } catch (error) {
        console.error("Ошибка загрузки каталога:", error);
        showLoader(false);
        showToast("Ошибка загрузки каталога");
    }
}

function showLoader(state) {
    const loader = document.getElementById("loader");
    if (loader) loader.style.display = state ? 'flex' : 'none';
}

/**
 * Отрисовка главных категорий (Корень)
 */
function renderMainCategories() {
    const top = Object.values(catalog).filter(c => c.parent_id === "0");
    
    const html = `
        <form onsubmit="window.search(event)" style="padding: 10px;">
            <input id="search-bar" placeholder="Поиск товаров..." style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 20px;">
        </form>
        <div class="grid" style="padding: 10px;">
            ${top.map(c => `
                <div class="category-button" onclick="window.openCategory('${c.id}')">
                    <img class="category-icon" src="/static/${categoryIcons[c.name] || 'vape.png'}">
                    <div>${c.name}</div>
                </
            `).join('')}
        </div>
    `;
    
    setContent(html);
}

/**
 * Открытие категории (Управляет навигацией)
 */
window.openCategory = function(id) {
    const cat = catalog[id];
    if (!cat) return;
    
    // 1. Сначала добавляем в стек
    window.pushScreen(`Category:${id}`, 'catalog');
    
    // 2. Потом рисуем
    if (cat.subcategories && Object.keys(cat.subcategories).length) {
        renderSubcategories(cat.subcategories);
    } else if (cat.products?.length) {
        renderProducts(cat.products);
    }
};

/**
 * Отрисовка подкатегорий
 */
function renderSubcategories(subs) {
    const values = Object.values(subs);
    
    const html = `
        <form onsubmit="window.search(event)" style="padding: 10px;">
            <input id="search-bar" placeholder="Поиск..." style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 20px;">
        </form>
        <div class="grid" style="padding: 10px;">
            ${values.map((s, i) => `
                <div class="category-button" onclick="window.openSubSub(${cache(s)})">
                    <img class="category-icon" src="${fixImg(s.icon)}">
                    <div>${s.name}</div>
                </div>
            `).join('')}
        </div>
    `;
    setContent(html);
}

function cache(obj) {
    subCache.push(obj);
    return subCache.length - 1;
}

/**
 * Открытие подкатегории
 */
window.openSubSub = function(index) {
    const s = subCache[index];
    if (!s) return;
    
    window.pushScreen(`SubSub:${s.id}`, 'catalog');
    
    if (s.subcategories && Object.keys(s.subcategories).length) {
        renderSubcategories(s.subcategories);
    } else {
        renderProducts(s.products || []);
    }
};

/**
 * Отрисовка списка товаров
 */
function renderProducts(arr) {
    productViewData = arr;
    
    const html = `
        <div class="sort-buttons" style="display: flex; gap: 10px; padding: 10px;">
            <button onclick="window.sortBy('price')" class="auth-fill-button" style="flex:1;">По цене</button>
            <button onclick="window.sortBy('availability')" class="auth-fill-button" style="flex:1;">В наличии</button>
        </div>
        <div class="grid" style="padding: 10px;">
            ${arr.map((p, i) => `
                <div class="product-card" onclick="window.viewProduct(${i})">
                    <img src="${fixImg(p.image)}">
                    ${p.special_price ? '<img src="/static/sale.png" class="sale-icon">' : ''}
                    <div class="content">
                        <h4>${p.title}</h4>
                        <p class="price">
                            ${p.special_price 
                                ? `<span class="old-price">${parseFloat(p.regular_price).toFixed(2)} BYN</span><span class="new-price">${parseFloat(p.special_price).toFixed(2)} BYN</span>`
                                : `${parseFloat(p.price).toFixed(2)} BYN`
                            }
                        </p>
                        <div class="${p.available === 'out_of_stock' ? 'map-button' : 'add-button'}"
                             onclick="event.stopPropagation(); window.handleBuyClick(${i})">
                            ${p.available === 'out_of_stock' ? 'Недоступен' : 'Купить'}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    setContent(html);
}

/**
 * Обработка клика "Купить" (чтобы не срабатывал клик по карточке)
 */
window.handleBuyClick = function(index) {
    const p = productViewData[index];
    if (p.available === 'out_of_stock') {
        showToast('К сожалению, товар недоступен');
        return;
    }
    window.addProductToCart(p);
};

/**
 * Сортировка
 */
window.sortBy = function(type) {
    const sorted = [...productViewData];
    if (type === 'price') sorted.sort((a,b) => a.price - b.price);
    else if (type === 'availability') sorted.sort((a,b) => (a.available === 'out_of_stock') - (b.available === 'out_of_stock'));
    renderProducts(sorted);
};

/**
 * Просмотр товара (Детали)
 */
window.viewProduct = function(i) {
    const p = productViewData[i];
    if (!p) return;
    
    selectedOptionImage = p.image;
    selectedOptionName = '';
    
    window.pushScreen(`Product:${p.id}`, 'catalog');
    renderDetailView(i);
};

function renderDetailView(i) {
    const p = productViewData[i];
    if (!p) return;
    
    const attributesTable = p.attributes?.length 
        ? `<table style="width:100%; border-collapse: collapse;">${p.attributes.map(attr => `
            <tr>
                <td style="padding: 5px; border-bottom: 1px solid #eee;"><strong>${attr.name}</strong></td>
                <td style="padding: 5px; border-bottom: 1px solid #eee;">${attr.value.replace(/,\s*/g, ', ')}</td>
            </tr>
        `).join('')}</table>`
        : `<p>${p.description || ''}</p>`;
    
    const optionsBlock = p.options?.length 
        ? p.options.map(opt => `
            <div style="margin-bottom: 10px;"><strong>${opt.name}:</strong></div>
            <div class="option-values" style="display: flex; gap: 10px; overflow-x: auto; padding-bottom: 10px;">
                ${opt.values.map((val, idx) => `
                    <div onclick="window.selectOption(${i}, '${opt.name}', ${idx})" 
                         class="option-value ${selectedOptionName === val.name ? 'selected' : ''} ${val.available ? '' : 'unavailable'}"
                         style="min-width: 60px; border: 1px solid #ddd; border-radius: 8px; padding: 5px; text-align: center; cursor: pointer;">
                        ${val.image ? `<img src="${fixImg(val.image)}" style="max-height: 40px;">` : ''}
                        <div style="font-size: 10px; margin-top: 4px;">${val.name}</div>
                    </div>
                `).join('')}
            </div>
        `).join('')
        : '';
    
    const isUnavailable = p.available === 'out_of_stock';
    
    const html = `
        <div class="product-detail" style="padding: 15px;">
            <img id="product-main-img" src="${fixImg(selectedOptionImage)}" 
                 style="max-width: 100%; height: auto; max-height: 250px; object-fit: contain; margin: 0 auto 16px; display: block; border-radius: 10px;">
            <h3>${p.title}</h3>
            ${attributesTable}
            ${optionsBlock}
            
            <p class="price" style="font-size: 20px; font-weight: bold; margin: 15px 0;">
                ${p.special_price
                    ? `<span style="text-decoration: line-through; color: #999; font-size: 16px;">${parseFloat(p.regular_price).toFixed(2)} BYN</span>
                       <span style="color: #a30000;">${parseFloat(p.special_price).toFixed(2)} BYN</span>`
                    : `${parseFloat(p.price).toFixed(2)} BYN`}
            </p>
            
            <div class="${isUnavailable ? 'map-button' : 'add-button'}"
                 onclick="${p.options?.length 
                    ? `if (!selectedOptionName && !p.options[0].values.find(v=>v.available)) { showToast('Выберите вариант'); return; } window.addProductToCart(productViewData[${i}], selectedOptionName)`
                    : `window.addProductToCart(productViewData[${i}])`}"
                 style="width: 100%; height: 45px; border-radius: 20px; font-size: 16px; display: flex; align-items: center; justify-content: center; margin-top: 20px;">
                ${isUnavailable ? 'Недоступен' : 'Купить'}
            </div>
        </div>
    `;
    
    setContent(html);
}

/**
 * Выбор опции
 */
window.selectOption = function(productIndex, optionName, valueIndex) {
    const opt = productViewData[productIndex].options.find(o => o.name === optionName);
    const val = opt.values[valueIndex];
    if (val.available) {
        selectedOptionImage = val.image || productViewData[productIndex].image;
        selectedOptionName = val.name;
        renderDetailView(productIndex);
    } else {
        showToast('Этот вариант недоступен');
    }
};

/**
 * Исправление URL картинок
 */
function fixImg(url) {
    if (!url || typeof url !== 'string') return '/static/placeholder.png';
    return 'https://nekuri.by' + url.replace(/ /g, '%20').replace(/\/g, '');
}

/**
 * Поиск
 */
window.search = function(e) {
    e.preventDefault();
    const query = document.getElementById('search-bar').value.toLowerCase();
    if (!query) return;
    
    const allProducts = Object.values(catalog).flatMap(c => c.products || []);
    const found = allProducts.filter(p => p.title.toLowerCase().includes(query));
    
    window.pushScreen(`Search:${query}`, 'catalog');
    renderProducts(found);
};

/**
 * Вспомогательная: установка контента с анимацией
 */
function setContent(html) {
    const container = document.getElementById('catalog-container');
    const contentEl = document.getElementById('content');
    const target = container || contentEl;
    
    if (!target) return;
    
    target.style.opacity = 0;
    setTimeout(() => {
        target.innerHTML = html;
        target.style.opacity = 1;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
}

/**
 * Добавление в корзину
 */
window.addProductToCart = function(product, selectedOption = null) {
    const price = parseFloat(product.special_price || product.price || product.regular_price || 0);
    if (window.cart) {
        window.cart.add({
            id: product.id,
            title: product.title,
            price,
            option: selectedOption,
            image: product.image
        }, selectedOption);
        showToast("Товар добавлен в корзину");
    }
};

/**
 * ВОССТАНОВЛЕНИЕ ЭКРАНА (Вызывается при нажатии "Назад")
 * Эта функция нужна, чтобы navigation.js знал, что рисовать
 */
window.restoreScreen = function(name) {
    console.log("Restoring screen:", name);
    
    if (name.startsWith('Category:')) {
        const id = name.split(':')[1];
        // Мы не пушим в стек, а сразу рисуем
        const cat = catalog[id];
        if (cat) {
            if (cat.subcategories && Object.keys(cat.subcategories).length) {
                renderSubcategories(cat.subcategories);
            } else if (cat.products?.length) {
                renderProducts(cat.products);
            }
        }
    } else if (name.startsWith('SubSub:')) {
        // Для простоты возвращаемся на уровень выше или в главную
        renderMainCategories();
    } else if (name === 'catalog-main') {
        renderMainCategories();
    } else if (name.startsWith('Search:')) {
        const query = name.split(':')[1];
        // Повторяем поиск
        const allProducts = Object.values(catalog).flatMap(c => c.products || []);
        const found = allProducts.filter(p => p.title.toLowerCase().includes(query));
        renderProducts(found);
    } else {
        // По умолчанию - главная каталога
        renderMainCategories();
    }
};

function showToast(message, duration = 2000) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 12px 24px; border-radius: 25px; z-index: 1000; font-size: 14px; transition: opacity 0.3s;`;
    document.body.appendChild(toast);
    setTimeout(() => toast.style.opacity = 1, 10);
    setTimeout(() => {
        toast.style.opacity = 0;
        setTimeout(() => toast.remove(), 300);
    }, duration);
}
