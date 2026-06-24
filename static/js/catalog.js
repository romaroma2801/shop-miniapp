// catalog.js - Каталог без конфликтов навигации

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

const subCache = [];
let productViewData = [];
let selectedOptionName = '';
let selectedOptionImage = '';

/**
 * Инициализация страницы каталога
 */
window.initCatalogPage = function() {
    window.currentFooterSection = 'catalog';
    if (window.setActiveFooter) window.setActiveFooter('catalog');
    
    const catalogHTML = `
        <div class="header">
            <img src="/static/logo22.png" alt="Логотип" class="logo">
        </div>
        <div id="loader" class="loader">
            <img src="/static/Eicon.png" alt="Загрузка...">
        </div>
        <div id="content" class="catalog-content"></div>
    `;
    
    showContent(catalogHTML);
    loadCatalog();
};

/**
 * Загрузить каталог с сервера
 */
async function loadCatalog() {
    showLoader(true);
    try {
        const response = await fetch("/api/catalog");
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
 * Отрисовать главные категории
 */
function renderMainCategories() {
    const top = Object.values(catalog).filter(c => c.parent_id === "0");
    
    const html = `
        <form onsubmit="search(event)">
            <input id="search-bar" placeholder="Поиск">
        </form>
        <div class="grid">
            ${top.map(c => `
                <div class="category-button" onclick="openCategory('${c.id}')">
                    <img class="category-icon" src="/static/${categoryIcons[c.name] || 'vape.png'}">
                    <div>${c.name}</div>
                </div>
            `).join('')}
        </div>
    `;
    
    setContent(html);
}

/**
 * Открыть категорию
 */
window.openCategory = function(id) {
    const cat = catalog[id];
    if (!cat) return;
    
    window.pushScreen(`Category:${id}`, 'catalog');
    
    if (cat.subcategories && Object.keys(cat.subcategories).length) {
        renderSubcategories(cat.subcategories);
    } else if (cat.products?.length) {
        renderProducts(cat.products);
    }
};

/**
 * Отрисовать подкатегории
 */
function renderSubcategories(subs) {
    const values = Object.values(subs);
    
    const html = `
        <form onsubmit="search(event)">
            <input id="search-bar" placeholder="Поиск">
        </form>
        <div class="grid">
            ${values.map((s, i) => `
                <div class="category-button" onclick="openSubSub(${cache(s)})">
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
 * Открыть подподкатегорию
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
 * Отрисовать продукты
 */
function renderProducts(arr) {
    productViewData = arr;
    
    const html = `
        <form onsubmit="search(event)">
            <input id="search-bar" placeholder="Поиск">
        </form>
        <div class="sort-buttons">
            <button onclick="sortBy('price')">По цене</button>
            <button onclick="sortBy('availability')">В наличии</button>
        </div>
        <div class="grid">
            ${arr.map((p, i) => `
                <div class="product-card" onclick="viewProduct(${i})">
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
                             onclick="event.stopPropagation(); ${p.available === 'out_of_stock' 
                                ? "showToast('К сожалению, товар недоступен')" 
                                : `addProductToCart(productViewData[${i}])`}">
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
 * Сортировка продуктов
 */
window.sortBy = function(type) {
    const sorted = [...productViewData];
    if (type === 'price') sorted.sort((a,b) => a.price - b.price);
    else if (type === 'availability') sorted.sort((a,b) => (a.available === 'out_of_stock') - (b.available === 'out_of_stock'));
    renderProducts(sorted);
};

/**
 * Просмотр детальной информации о продукте
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
        ? `<table>${p.attributes.map(attr => `
            <tr>
                <td><strong>${attr.name}</strong></td>
                <td>${attr.value.replace(/,\s*/g, ', ')}</td>
            </tr>
        `).join('')}</table>`
        : `<p>${p.description || ''}</p>`;
    
    const optionsBlock = p.options?.length 
        ? p.options.map(opt => `
            <div><strong>${opt.name}:</strong></div>
            <div class="option-values">
                ${opt.values.map((val, idx) => `
                    <div onclick="selectOption(${i}, '${opt.name}', ${idx})" 
                         class="option-value ${selectedOptionName === val.name ? 'selected' : ''} ${val.available ? '' : 'unavailable'}">
                        ${val.image ? `<img src="${fixImg(val.image)}">` : ''}
                        <div>${val.name}</div>
                    </div>
                `).join('')}
            </div>
        `).join('')
        : '';
    
    const html = `
        <div class="product-detail">
            <img id="product-main-img" src="${fixImg(selectedOptionImage)}" 
                 style="max-width: 100%; height: auto; max-height: 250px; object-fit: contain; margin: 0 auto 16px; display: block;">
            <h4>${p.title}</h4>
            ${attributesTable}
            ${optionsBlock}
            
            <p class="price">
                ${p.special_price
                    ? `<span style="text-decoration: line-through; color: #999; margin-right: 8px;">${parseFloat(p.regular_price).toFixed(2)} BYN</span>
                       <span style="color: #a30000;">${parseFloat(p.special_price).toFixed(2)} BYN</span>`
                    : `${parseFloat(p.price).toFixed(2)} BYN`}
            </p>
            
            <div class="${p.available === 'out_of_stock' ? 'map-button' : 'add-button'}"
                 onclick="${p.options?.length 
                    ? `if (!selectedOptionName) { showToast('Пожалуйста, выберите вариант товара'); return; } else { addProductToCart(productViewData[${i}], selectedOptionName); }`
                    : `addProductToCart(productViewData[${i}])`}"
                 style="width: 100%; height: 40px; border-radius: 20px; font-size: 16px; display: flex; align-items: center; justify-content: center;">
                ${p.available === 'out_of_stock' ? 'Недоступен' : 'Купить'}
            </div>
        </div>
    `;
    
    setContent(html);
}

/**
 * Выбор опции продукта
 */
window.selectOption = function(productIndex, optionName, valueIndex) {
    const opt = productViewData[productIndex].options.find(o => o.name === optionName);
    const val = opt.values[valueIndex];
    if (val.available) {
        selectedOptionImage = val.image || productViewData[productIndex].image;
        selectedOptionName = val.name;
        renderDetailView(productIndex);
    }
};

/**
 * Исправить URL изображения
 */
function fixImg(url) {
    if (!url || typeof url !== 'string') return '/static/placeholder.png';
    return 'https://nekuri.by' + url.replace(/ /g, '%20').replace(/\/g, '');
}

/**
 * Поиск по каталогу
 */
window.search = function(e) {
    e.preventDefault();
    const val = document.getElementById('search-bar').value.toLowerCase();
    const arr = Object.values(catalog).flatMap(c => c.products || []);
    const found = arr.filter(p => p.title.toLowerCase().includes(val));
    
    window.pushScreen(`Search:${val}`, 'catalog');
    renderProducts(found);
};

/**
 * Установить контент с анимацией
 */
function setContent(html) {
    const el = document.getElementById("content");
    if (!el) return;
    
    el.style.opacity = 0;
    setTimeout(() => {
        el.innerHTML = html;
        el.style.opacity = 1;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
}

/**
 * Добавить продукт в корзину
 */
window.addProductToCart = function(product, selectedOption = null) {
    const price = parseFloat(product.special_price || product.price || product.regular_price || 0);
    if (window.cart) {
        window.cart.add({
            id: product.id,
            title: product.title,
            price,
            option: selectedOption
        }, selectedOption);
        showToast("Товар добавлен в корзину");
    }
};

/**
 * Восстановить экран при нажатии "Назад"
 */
window.restoreScreen = function(name) {
    if (name.startsWith('Category:')) {
        const id = name.split(':')[1];
        openCategory(id);
    } else if (name.startsWith('SubSub:')) {
        const id = name.split(':')[1];
        renderMainCategories();
    } else if (name === 'catalog-main') {
        renderMainCategories();
    } else if (name.startsWith('Search:')) {
        const query = name.split(':')[1];
        document.getElementById('search-bar').value = query;
        search({ preventDefault: () => {} });
    } else {
        renderMainCategories();
    }
};

function showToast(message, duration = 2000) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.7); color: white; padding: 12px 24px; border-radius: 4px; z-index: 1000; opacity: 0; transition: opacity 0.3s;`;
    document.body.appendChild(toast);
    setTimeout(() => toast.style.opacity = 1, 10);
    setTimeout(() => {
        toast.style.opacity = 0;
        setTimeout(() => toast.remove(), 300);
    }, duration);
}
