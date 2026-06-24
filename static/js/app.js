// ===== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ =====
let currentUser = null;
let cart = JSON.parse(localStorage.getItem('cart') || '[]');
let catalog = {};
let currentScreen = 'catalog';

// ===== ИНИЦИАЛИЗАЦИЯ =====
document.addEventListener('DOMContentLoaded', async () => {

    if (window.Telegram?.WebApp) {
        Telegram.WebApp.ready();
        Telegram.WebApp.expand();
    }

    await initUser();

    initNavigation();

    await loadCatalog();

    updateCartBadge();

});


// ===== ПОЛЬЗОВАТЕЛЬ =====
async function initUser() {

    const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;

    if (!tgUser) {
        showToast('Откройте приложение через Telegram');
        return;
    }

    currentUser = {
        id: tgUser.id,
        username: tgUser.username || `id${tgUser.id}`,
        first_name: tgUser.first_name || '',
        phone: tgUser.phone_number || ''
    };

    try {

        const response = await fetch(`/api/get-user?username=${currentUser.username}`);
        const result = await response.json();

        if (result.exists) {

            currentUser.name = result.user.Name || currentUser.first_name;
            currentUser.phone = result.user.Phone || currentUser.phone;

        } else {

            await fetch('/api/save-user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: currentUser.username,
                    name: currentUser.first_name,
                    phone: currentUser.phone
                })
            });

        }

    } catch (error) {

        console.error(error);

    }

}


// ===== НАВИГАЦИЯ =====
function initNavigation() {

    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {

        item.addEventListener('click', () => {

            const screen = item.dataset.screen;

            if (!screen) return;

            showScreen(screen);

            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

        });

    });

    document.getElementById('close-cart-btn')
        ?.addEventListener('click', toggleCart);

    document.getElementById('btn-checkout')
        ?.addEventListener('click', openCheckout);

    document.getElementById('btn-back-to-cart')
        ?.addEventListener('click', closeCheckout);

    document.getElementById('checkout-form')
        ?.addEventListener('submit', submitOrder);

}


function showScreen(screenName) {

    currentScreen = screenName;

    if (screenName === 'catalog') {
        renderCatalog();
    }

    if (screenName === 'profile') {
        renderProfile();
    }

    if (screenName === 'cart') {
        toggleCart();
    }

}


// ===== КАТАЛОГ =====
async function loadCatalog() {

    try {

        const response = await fetch('/api/catalog');

        catalog = await response.json();

        renderCatalog();

    } catch (error) {

        console.error(error);
        showToast('Ошибка загрузки каталога');

    }

}


function renderCatalog() {

    const mainContent = document.getElementById('main-content');

    const categories = Object.values(catalog)
        .filter(c => c.parent_id === '0');

    let html = `
        <div class="search-container">
            <input
                type="text"
                class="search-input"
                placeholder="Поиск товаров..."
                oninput="searchProducts(this.value)">
        </div>

        <div class="categories-container">
    `;

    categories.forEach(category => {

        html += `
            <div class="category-card"
                 onclick="openCategory('${category.id}')">

                <div class="category-icon">
                    ${getCategoryIcon(category.name)}
                </div>

                <div class="category-name">
                    ${category.name}
                </div>

            </div>
        `;

    });

    html += `
        </div>

        <div id="products-container"
             class="products-container">
        </div>
    `;

    mainContent.innerHTML = html;

}


// ===== ИКОНКИ =====
function getCategoryIcon(name) {

    const icons = {
        'Парогенераторы': '💨',
        'Жидкости': '💧',
        'Жидкости для вейпа': '💧',
        'Запчасти': '🔧',
        'Кальяны': '🔥',
        'Самозамес': '🧪',
        'Уценённый': '🏷️'
    };

    return icons[name] || '📦';

}


// ===== ОТКРЫТИЕ КАТЕГОРИИ =====
function openCategory(categoryId) {

    const category = catalog[categoryId];

    if (!category) return;

    if (
        category.subcategories &&
        Object.keys(category.subcategories).length > 0
    ) {

        renderSubcategories(category.subcategories);

    } else if (
        category.products &&
        category.products.length > 0
    ) {

        renderProducts(category.products);

    }

}


// ===== ПОДКАТЕГОРИИ =====
function renderSubcategories(subcategories) {

    const productsContainer =
        document.getElementById('products-container');

    if (!productsContainer) return;

    let html = '<div class="categories-container">';

    Object.values(subcategories).forEach(sub => {

        html += `
            <div class="category-card"
                 onclick="openSubcategory('${sub.id}')">

                <div class="category-icon">📁</div>

                <div class="category-name">
                    ${sub.name}
                </div>

            </div>
        `;

    });

    html += '</div>';

    productsContainer.innerHTML = html;

}
// ===== ОТКРЫТИЕ ПОДКАТЕГОРИИ =====
function openSubcategory(subcategoryId) {

    const subcategory = findSubcategory(subcategoryId);

    if (!subcategory) return;

    if (
        subcategory.subcategories &&
        Object.keys(subcategory.subcategories).length > 0
    ) {

        renderSubcategories(subcategory.subcategories);

    } else if (
        subcategory.products &&
        subcategory.products.length > 0
    ) {

        renderProducts(subcategory.products);

    }

}


// ===== ПОИСК ПОДКАТЕГОРИИ =====
function findSubcategory(id) {

    for (const category of Object.values(catalog)) {

        if (!category.subcategories) continue;

        for (const sub of Object.values(category.subcategories)) {

            if (sub.id == id) {
                return sub;
            }

            if (sub.subcategories) {

                const found =
                    findSubcategoryIn(sub.subcategories, id);

                if (found) {
                    return found;
                }

            }

        }

    }

    return null;

}


function findSubcategoryIn(subcategories, id) {

    for (const sub of Object.values(subcategories)) {

        if (sub.id == id) {
            return sub;
        }

        if (sub.subcategories) {

            const found =
                findSubcategoryIn(sub.subcategories, id);

            if (found) {
                return found;
            }

        }

    }

    return null;

}


// ===== ТОВАРЫ =====
function renderProducts(products) {

    const productsContainer =
        document.getElementById('products-container');

    if (!productsContainer) return;

    let html = '';

    products.forEach(product => {

        const price =
            product.special_price || product.price;

        const oldPrice =
            product.special_price
                ? product.regular_price
                : null;

        html += `
            <div class="product-card">

                ${product.special_price
                    ? '<div class="sale-badge">SALE</div>'
                    : ''}

                <img
                    src="${fixImageUrl(product.image)}"
                    alt="${product.title}"
                    class="product-image">

                <div class="product-info">

                    <div class="product-title">
                        ${product.title}
                    </div>

                    <div class="product-price">

                        <span class="price-current">
                            ${parseFloat(price).toFixed(2)} BYN
                        </span>

                        ${
                            oldPrice
                                ? `
                                <span class="price-old">
                                    ${parseFloat(oldPrice).toFixed(2)} BYN
                                </span>
                                `
                                : ''
                        }

                    </div>

                    <button
                        class="btn-add ${product.available === 'out_of_stock' ? 'disabled' : ''}"
                        onclick="addToCartById('${product.id}')"
                        ${product.available === 'out_of_stock' ? 'disabled' : ''}>

                        ${
                            product.available === 'out_of_stock'
                                ? 'Нет в наличии'
                                : 'В корзину'
                        }

                    </button>

                </div>

            </div>
        `;

    });

    productsContainer.innerHTML = html;

}


// ===== КАРТИНКИ =====
function fixImageUrl(url) {

    if (!url) {

        return 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"></svg>';

    }

    if (url.startsWith('http')) {
        return url;
    }

    return 'https://nekuri.by' + url.replace(/ /g, '%20');

}


// ===== ПОИСК ТОВАРА ПО ID =====
function addToCartById(productId) {

    let foundProduct = null;

    function search(categories) {

        for (const category of Object.values(categories)) {

            if (category.products) {

                const product =
                    category.products.find(
                        p => p.id == productId
                    );

                if (product) {

                    foundProduct = product;
                    return;

                }

            }

            if (category.subcategories) {
                search(category.subcategories);
            }

        }

    }

    search(catalog);

    if (foundProduct) {
        addToCart(null, foundProduct);
    }

}


// ===== ДОБАВИТЬ В КОРЗИНУ =====
function addToCart(productIndex, productData = null) {

    const product = productData;

    if (!product) return;

    const existingItem =
        cart.find(item => item.id == product.id);

    if (existingItem) {

        existingItem.quantity++;

    } else {

        cart.push({
            id: product.id,
            title: product.title,
            price: parseFloat(product.special_price || product.price),
            image: fixImageUrl(product.image),
            quantity: 1
        });

    }

    saveCart();
    updateCartBadge();

    showToast('Товар добавлен в корзину');

}


// ===== ПОИСК =====
function searchProducts(query) {

    if (!query) {

        renderCatalog();
        return;

    }

    const allProducts = [];

    function search(categories) {

        for (const category of Object.values(categories)) {

            if (category.products) {

                allProducts.push(
                    ...category.products.filter(product =>
                        product.title
                            .toLowerCase()
                            .includes(query.toLowerCase())
                    )
                );

            }

            if (category.subcategories) {
                search(category.subcategories);
            }

        }

    }

    search(catalog);

    renderProducts(allProducts);

}
// ===== ОТКРЫТИЕ ПОДКАТЕГОРИИ =====
function openSubcategory(subcategoryId) {

    const subcategory = findSubcategory(subcategoryId);

    if (!subcategory) return;

    if (
        subcategory.subcategories &&
        Object.keys(subcategory.subcategories).length > 0
    ) {

        renderSubcategories(subcategory.subcategories);

    } else if (
        subcategory.products &&
        subcategory.products.length > 0
    ) {

        renderProducts(subcategory.products);

    }

}


// ===== ПОИСК ПОДКАТЕГОРИИ =====
function findSubcategory(id) {

    for (const category of Object.values(catalog)) {

        if (!category.subcategories) continue;

        for (const sub of Object.values(category.subcategories)) {

            if (sub.id == id) {
                return sub;
            }

            if (sub.subcategories) {

                const found =
                    findSubcategoryIn(sub.subcategories, id);

                if (found) {
                    return found;
                }

            }

        }

    }

    return null;

}


function findSubcategoryIn(subcategories, id) {

    for (const sub of Object.values(subcategories)) {

        if (sub.id == id) {
            return sub;
        }

        if (sub.subcategories) {

            const found =
                findSubcategoryIn(sub.subcategories, id);

            if (found) {
                return found;
            }

        }

    }

    return null;

}


// ===== ТОВАРЫ =====
function renderProducts(products) {

    const productsContainer =
        document.getElementById('products-container');

    if (!productsContainer) return;

    let html = '';

    products.forEach(product => {

        const price =
            product.special_price || product.price;

        const oldPrice =
            product.special_price
                ? product.regular_price
                : null;

        html += `
            <div class="product-card">

                ${product.special_price
                    ? '<div class="sale-badge">SALE</div>'
                    : ''}

                <img
                    src="${fixImageUrl(product.image)}"
                    alt="${product.title}"
                    class="product-image">

                <div class="product-info">

                    <div class="product-title">
                        ${product.title}
                    </div>

                    <div class="product-price">

                        <span class="price-current">
                            ${parseFloat(price).toFixed(2)} BYN
                        </span>

                        ${
                            oldPrice
                                ? `
                                <span class="price-old">
                                    ${parseFloat(oldPrice).toFixed(2)} BYN
                                </span>
                                `
                                : ''
                        }

                    </div>

                    <button
                        class="btn-add ${product.available === 'out_of_stock' ? 'disabled' : ''}"
                        onclick="addToCartById('${product.id}')"
                        ${product.available === 'out_of_stock' ? 'disabled' : ''}>

                        ${
                            product.available === 'out_of_stock'
                                ? 'Нет в наличии'
                                : 'В корзину'
                        }

                    </button>

                </div>

            </div>
        `;

    });

    productsContainer.innerHTML = html;

}


// ===== КАРТИНКИ =====
function fixImageUrl(url) {

    if (!url) {

        return 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"></svg>';

    }

    if (url.startsWith('http')) {
        return url;
    }

    return 'https://nekuri.by' + url.replace(/ /g, '%20');

}


// ===== ПОИСК ТОВАРА ПО ID =====
function addToCartById(productId) {

    let foundProduct = null;

    function search(categories) {

        for (const category of Object.values(categories)) {

            if (category.products) {

                const product =
                    category.products.find(
                        p => p.id == productId
                    );

                if (product) {

                    foundProduct = product;
                    return;

                }

            }

            if (category.subcategories) {
                search(category.subcategories);
            }

        }

    }

    search(catalog);

    if (foundProduct) {
        addToCart(null, foundProduct);
    }

}


// ===== ДОБАВИТЬ В КОРЗИНУ =====
function addToCart(productIndex, productData = null) {

    const product = productData;

    if (!product) return;

    const existingItem =
        cart.find(item => item.id == product.id);

    if (existingItem) {

        existingItem.quantity++;

    } else {

        cart.push({
            id: product.id,
            title: product.title,
            price: parseFloat(product.special_price || product.price),
            image: fixImageUrl(product.image),
            quantity: 1
        });

    }

    saveCart();
    updateCartBadge();

    showToast('Товар добавлен в корзину');

}


// ===== ПОИСК =====
function searchProducts(query) {

    if (!query) {

        renderCatalog();
        return;

    }

    const allProducts = [];

    function search(categories) {

        for (const category of Object.values(categories)) {

            if (category.products) {

                allProducts.push(
                    ...category.products.filter(product =>
                        product.title
                            .toLowerCase()
                            .includes(query.toLowerCase())
                    )
                );

            }

            if (category.subcategories) {
                search(category.subcategories);
            }

        }

    }

    search(catalog);

    renderProducts(allProducts);

}
// ===== КОРЗИНА =====
function toggleCart() {

    const cartPanel = document.getElementById('cart-panel');

    if (!cartPanel) return;

    cartPanel.classList.toggle('active');

    if (cartPanel.classList.contains('active')) {
        renderCart();
    }

}


// ===== ОТРИСОВКА КОРЗИНЫ =====
function renderCart() {

    const cartItems = document.getElementById('cart-items');

    if (!cartItems) return;

    if (cart.length === 0) {

        cartItems.innerHTML = `
            <div class="empty-cart">
                <div class="empty-cart-icon">🛒</div>
                <div class="empty-cart-text">
                    Корзина пуста
                </div>
            </div>
        `;

        updateCartTotals();
        return;

    }

    let html = '';

    cart.forEach((item, index) => {

        html += `
            <div class="cart-item">

                <img
                    src="${item.image}"
                    class="cart-item-image"
                    alt="${item.title}">

                <div class="cart-item-info">

                    <div class="cart-item-title">
                        ${item.title}
                    </div>

                    <div class="cart-item-controls">

                        <div class="quantity-controls">

                            <button
                                class="quantity-btn"
                                onclick="updateQuantity(${index}, -1)">
                                −
                            </button>

                            <span class="quantity-value">
                                ${item.quantity}
                            </span>

                            <button
                                class="quantity-btn"
                                onclick="updateQuantity(${index}, 1)">
                                +
                            </button>

                        </div>

                        <div class="cart-item-price">
                            ${(item.price * item.quantity).toFixed(2)} BYN
                        </div>

                    </div>

                </div>

                <button
                    class="remove-btn"
                    onclick="removeFromCart(${index})">
                    ✕
                </button>

            </div>
        `;

    });

    cartItems.innerHTML = html;

    updateCartTotals();

}


// ===== ИЗМЕНЕНИЕ КОЛИЧЕСТВА =====
function updateQuantity(index, change) {

    if (!cart[index]) return;

    cart[index].quantity += change;

    if (cart[index].quantity <= 0) {
        cart.splice(index, 1);
    }

    saveCart();
    renderCart();
    updateCartBadge();

}


// ===== УДАЛЕНИЕ =====
function removeFromCart(index) {

    cart.splice(index, 1);

    saveCart();
    renderCart();
    updateCartBadge();

}


// ===== ИТОГИ КОРЗИНЫ =====
function updateCartTotals() {

    const subtotal = cart.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
    );

    const discount = subtotal * 0.03;
    const delivery = subtotal >= 100 ? 0 : 4;
    const total = subtotal - discount + delivery;

    const discountEl = document.getElementById('cart-discount');
    const deliveryEl = document.getElementById('cart-delivery');
    const totalEl = document.getElementById('cart-total');

    if (discountEl) {
        discountEl.textContent =
            `-${discount.toFixed(2)} BYN`;
    }

    if (deliveryEl) {
        deliveryEl.textContent =
            `${delivery.toFixed(2)} BYN`;
    }

    if (totalEl) {
        totalEl.textContent =
            `${total.toFixed(2)} BYN`;
    }

}


// ===== БЕЙДЖ КОРЗИНЫ =====
function updateCartBadge() {

    const badge = document.getElementById('cart-badge');

    if (!badge) return;

    const totalItems = cart.reduce(
        (sum, item) => sum + item.quantity,
        0
    );

    badge.textContent = totalItems;

    badge.classList.toggle(
        'show',
        totalItems > 0
    );

}


// ===== СОХРАНЕНИЕ =====
function saveCart() {

    localStorage.setItem(
        'cart',
        JSON.stringify(cart)
    );

}
// ===== ОФОРМЛЕНИЕ ЗАКАЗА =====
function openCheckout() {

    if (cart.length === 0) {
        showToast('Корзина пуста');
        return;
    }

    toggleCart();

    const checkoutScreen =
        document.getElementById('checkout-screen');

    if (!checkoutScreen) return;

    checkoutScreen.classList.add('active');

    renderCheckoutItems();
    prefillCheckoutForm();

}


// ===== ЗАКРЫТЬ ОФОРМЛЕНИЕ =====
function closeCheckout() {

    const checkoutScreen =
        document.getElementById('checkout-screen');

    if (checkoutScreen) {
        checkoutScreen.classList.remove('active');
    }

}


// ===== СОСТАВ ЗАКАЗА =====
function renderCheckoutItems() {

    const container =
        document.getElementById('checkout-summary');

    if (!container) return;

    let html = '<h3>Ваш заказ</h3>';

    cart.forEach(item => {

        html += `
            <div class="checkout-item">

                <div class="checkout-item-info">

                    <div class="checkout-item-title">
                        ${item.title}
                    </div>

                    <div class="checkout-item-option">
                        Количество: ${item.quantity}
                    </div>

                </div>

                <div class="checkout-item-price">
                    ${(item.price * item.quantity).toFixed(2)} BYN
                </div>

            </div>
        `;

    });

    const subtotal = cart.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
    );

    const discount = subtotal * 0.03;
    const delivery = subtotal >= 100 ? 0 : 4;
    const total = subtotal - discount + delivery;

    html += `
        <div class="checkout-totals">

            <div class="summary-row">
                <span>Товары:</span>
                <span>${subtotal.toFixed(2)} BYN</span>
            </div>

            <div class="summary-row">
                <span>Скидка 3%:</span>
                <span>-${discount.toFixed(2)} BYN</span>
            </div>

            <div class="summary-row">
                <span>Доставка:</span>
                <span>${delivery.toFixed(2)} BYN</span>
            </div>

            <div class="summary-row total">
                <span>Итого:</span>
                <span>${total.toFixed(2)} BYN</span>
            </div>

        </div>
    `;

    container.innerHTML = html;

}


// ===== АВТОЗАПОЛНЕНИЕ =====
function prefillCheckoutForm() {

    if (!currentUser) return;

    const nameInput =
        document.getElementById('inp-name');

    const phoneInput =
        document.getElementById('inp-phone');

    const cityInput =
        document.getElementById('inp-city');

    const addressInput =
        document.getElementById('inp-address');

    if (nameInput) {
        nameInput.value = currentUser.name || '';
    }

    if (phoneInput) {
        phoneInput.value = currentUser.phone || '';
    }

    const savedAddress =
        localStorage.getItem('lastAddress');

    if (savedAddress) {

        const address =
            JSON.parse(savedAddress);

        if (cityInput) {
            cityInput.value = address.city || '';
        }

        if (addressInput) {
            addressInput.value = address.address || '';
        }

    }

}


// ===== ОТПРАВКА ЗАКАЗА =====
async function submitOrder(e) {

    e.preventDefault();

    const subtotal = cart.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
    );

    const discount = subtotal * 0.03;
    const delivery = subtotal >= 100 ? 0 : 4;
    const finalTotal = subtotal - discount + delivery;

    const orderData = {

        items: cart,

        total: subtotal,

        discount: discount,

        delivery: delivery,

        final_total: finalTotal,

        customer_name:
            document.getElementById('inp-name')?.value || '',

        city:
            document.getElementById('inp-city')?.value || '',

        address:
            document.getElementById('inp-address')?.value || '',

        phone:
            document.getElementById('inp-phone')?.value || '',

        username:
            currentUser?.username || ''

    };

    try {

        const response = await fetch(
            '/api/create-order',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(orderData)
            }
        );

        const result = await response.json();

        if (result.status === 'success') {

            localStorage.setItem(
                'lastAddress',
                JSON.stringify({
                    city: orderData.city,
                    address: orderData.address
                })
            );

            cart = [];

            saveCart();
            updateCartBadge();

            closeCheckout();

            showToast(
                'Заказ успешно оформлен ✅'
            );

            showScreen('catalog');

        } else {

            showToast(
                'Ошибка оформления заказа'
            );

        }

    } catch (error) {

        console.error(error);

        showToast(
            'Ошибка оформления заказа'
        );

    }

}
// ===== ПРОФИЛЬ =====
function renderProfile() {

    const mainContent =
        document.getElementById('main-content');

    if (!mainContent) return;

    let html = `
        <div class="profile-container">

            <div class="user-info">

                <div class="user-avatar">👤</div>

                <div class="user-details">

                    <div class="user-name">
                        ${currentUser?.name || 'Пользователь'}
                    </div>

                    <div class="user-username">
                        @${currentUser?.username || ''}
                    </div>

                </div>

            </div>

            <div class="profile-form">

                <div class="form-group">
                    <label>Имя</label>

                    <input
                        type="text"
                        id="profile-name"
                        value="${currentUser?.name || ''}">
                </div>

                <div class="form-group">
                    <label>Телефон</label>

                    <input
                        type="tel"
                        id="profile-phone"
                        value="${currentUser?.phone || ''}">
                </div>

                <button
                    class="btn-primary"
                    onclick="saveProfile()">

                    Сохранить

                </button>

            </div>

            <div class="orders-section">

                <h3>Мои заказы</h3>

                <div
                    id="orders-list"
                    class="orders-list">

                </div>

            </div>

        </div>
    `;

    mainContent.innerHTML = html;

    loadUserOrders();

}


// ===== СОХРАНИТЬ ПРОФИЛЬ =====
async function saveProfile() {

    const name =
        document.getElementById('profile-name')
        ?.value.trim();

    const phone =
        document.getElementById('profile-phone')
        ?.value.trim();

    if (!name) {

        showToast('Введите имя');

        return;

    }

    try {

        const response = await fetch(
            '/api/save-user',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: currentUser.username,
                    name: name,
                    phone: phone
                })
            }
        );

        const result = await response.json();

        if (result.status === 'success') {

            currentUser.name = name;
            currentUser.phone = phone;

            showToast('Данные сохранены ✅');

            renderProfile();

        } else {

            showToast('Ошибка сохранения');

        }

    } catch (error) {

        console.error(error);

        showToast('Ошибка сохранения');

    }

}


// ===== ИСТОРИЯ ЗАКАЗОВ =====
async function loadUserOrders() {

    if (!currentUser) return;

    const ordersList =
        document.getElementById('orders-list');

    if (!ordersList) return;

    try {

        const response = await fetch(
            `/api/get-orders?username=${currentUser.username}`
        );

        const orders = await response.json();

        if (!orders || orders.length === 0) {

            ordersList.innerHTML =
                '<div class="empty-orders">У вас пока нет заказов</div>';

            return;

        }

        let html = '';

        orders.forEach(order => {

            html += `
                <div class="order-card">

                    <div class="order-header">

                        <div class="order-id">
                            Заказ №${order.order_id}
                        </div>

                        <div class="order-status">
                            ${order.status}
                        </div>

                    </div>

                    <div class="order-date">
                        ${formatDate(order.order_date)}
                    </div>

                    <div class="order-total">
                        ${parseFloat(order.final_total).toFixed(2)} BYN
                    </div>

                </div>
            `;

        });

        ordersList.innerHTML = html;

    } catch (error) {

        console.error(error);

        ordersList.innerHTML =
            '<div class="empty-orders">Ошибка загрузки</div>';

    }

}


// ===== ФОРМАТ ДАТЫ =====
function formatDate(dateString) {

    const date = new Date(dateString);

    return date.toLocaleDateString(
        'ru-RU',
        {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }
    );

}


// ===== TOAST =====
function showToast(message, duration = 2000) {

    const toast =
        document.getElementById('toast');

    if (!toast) return;

    toast.textContent = message;

    toast.classList.add('show');

    setTimeout(() => {

        toast.classList.remove('show');

    }, duration);

}
