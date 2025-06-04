// catalog.js

let catalog = {};
let historyStack = [];
let loadPromises = [];
let currentData = null;
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

function initCatalogPage() {
  window.currentState = "catalog";
  const catalogHTML = `
    <div class="header">
      <img src="/static/logo22.png" alt="Логотип" class="logo">
    </div>
    <button id="back-button" onclick="goBack()" style="display:none;">
      <img src="/static/back.svg" alt="Назад">
    </button>
    <div id="loader" class="loader">
      <img src="/static/Eicon.png" alt="Загрузка...">
    </div>
    <div id="content" class="catalog-content"></div>
  `;

  showContent(catalogHTML);
  loadCatalog();
}

async function loadCatalog() {
  showLoader(true);
  try {
    const response = await fetch("/api/catalog");
    catalog = await response.json();
    loadPromises = [];
    showLoader(false);
    openView(renderMainCategories);
  } catch (error) {
    console.error("Ошибка загрузки каталога:", error);
    showLoader(false);
  }
}

function showLoader(state) {
  document.getElementById("loader").style.display = state ? 'flex' : 'none';
}

function toggleBackButton() {
  document.getElementById("back-button").style.display = historyStack.length ? 'block' : 'none';
}

function openView(viewFn) {
  if (loadPromises.length) {
    loadPromises.forEach(p => p.cancel?.());
    loadPromises = [];
  }
  if (currentData) historyStack.push(currentData);
  currentData = viewFn;
  toggleBackButton();
  viewFn();
}

function goBack() {
  if (historyStack.length) {
    currentData = historyStack.pop();
    toggleBackButton();
    currentData();
  }
}

function renderMainCategories() {
  const top = Object.values(catalog).filter(c => c.parent_id === "0");
  setContent(`
    <form onsubmit="search(event)"><input id="search-bar" placeholder="Поиск"></form>
    <div class="grid">
      ${top.map(c => `
        <div class="category-button" onclick="openCategory('${c.id}')">
          <img class="category-icon" src="/static/${categoryIcons[c.name] || 'vape.png'}">
          <div>${c.name}</div>
        </div>`).join('')}
    </div>`);
}

function openCategory(id) {
  const cat = catalog[id];
  if (!cat) return;
  if (cat.subcategories && Object.keys(cat.subcategories).length) {
    openView(() => renderSubcategories(cat.subcategories));
  } else if (cat.products?.length) {
    openView(() => renderProducts(cat.products));
  }
}

function renderSubcategories(subs) {
  const values = Object.values(subs);
  setContent(`<form onsubmit="search(event)"><input id="search-bar" placeholder="Поиск"></form>
    <div class="grid">
    ${values.map((s, i) => `
      <div class="category-button" onclick="openSubSub(${cache(s)})">
        <img class="category-icon" src="${fixImg(s.icon)}">
        <div>${s.name}</div>
      </div>`).join('')}</div>`);
}

const subCache = [];
function cache(obj) { subCache.push(obj); return subCache.length - 1; }

function openSubSub(index) {
  const s = subCache[index];
  if (!s) return;
  if (s.subcategories && Object.keys(s.subcategories).length) {
    openView(() => renderSubcategories(s.subcategories));
  } else {
    openView(() => renderProducts(s.products || []));
  }
}

let productViewData = [];
let selectedOptionName = '';
let selectedOptionImage = '';

function renderProducts(arr) {
  productViewData = arr;
  setContent(`<form onsubmit="search(event)"><input id="search-bar" placeholder="Поиск"></form>
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
            ${p.special_price ? `<span class="old-price">${parseFloat(p.regular_price).toFixed(2)} BYN</span> <span class="new-price">${parseFloat(p.special_price).toFixed(2)} BYN</span>` : `${parseFloat(p.price).toFixed(2)} BYN`}
          </p>
          <div class="${p.available === 'out_of_stock' ? 'map-button' : 'add-button'}"
               onclick="event.stopPropagation(); ${p.available === 'out_of_stock'
                 ? "alert('К сожалению, товар недоступен')"
                 : `addProductToCart(productViewData[${i}])`}">
            ${p.available === 'out_of_stock' ? 'Недоступен' : 'Купить'}
          </div>
        </div>
      </div>`).join('')}</div>`);
}

function sortBy(type) {
  const sorted = [...productViewData];
  if (type === 'price') sorted.sort((a,b)=>a.price-b.price);
  else if (type === 'availability') sorted.sort((a,b)=>(a.available==='out_of_stock')-(b.available==='out_of_stock'));
  openView(() => renderProducts(sorted));
}

function viewProduct(i) {
  const p = productViewData[i];
  selectedOptionImage = p.image;
  selectedOptionName = '';
  const returnData = { products: productViewData, view: currentData };

  function renderDetailView() {
    const attributesTable = p.attributes?.length ? `
      <table>${p.attributes.map(attr => `
        <tr>
          <td><strong>${attr.name}</strong></td>
          <td>${attr.value.replace(/,\s*/g, ', ')}</td>
        </tr>`).join('')}</table>` : `<p>${p.description}</p>`;

    const optionsBlock = p.options?.length ? `
      ${p.options.map(opt => `
        <div><strong>${opt.name}:</strong></div>
        <div class="option-values">
          ${opt.values.map((val, idx) => `
            <div onclick="selectOption(${i}, '${opt.name}', ${idx})" class="option-value ${selectedOptionName === val.name ? 'selected' : ''} ${val.available ? '' : 'unavailable'}">
              ${val.image ? `<img src="${fixImg(val.image)}">` : ''} ${val.name}
            </div>`).join('')}
        </div>`).join('')}` : '';

    setContent(`
      <div class="product-detail">
        <img id="product-main-img" src="${fixImg(selectedOptionImage)}" style="max-width: 100%; height: auto; max-height: 250px; object-fit: contain; margin: 0 auto 16px; display: block;">
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
               ? `if (!selectedOptionName) { alert('Пожалуйста, выберите вариант товара'); return; } else { addProductToCart(productViewData[${i}], selectedOptionName); }` 
               : `addProductToCart(productViewData[${i}])`}"
             style="width: 100%; height: 40px; border-radius: 20px; font-size: 16px; display: flex; align-items: center; justify-content: center;
                    ${p.available === 'out_of_stock' 
                      ? 'background: #fff; color: #ff0000; border: 1px solid #ff0000;' 
                      : 'background: #ff0000; color: #fff; border: none;'}">
          ${p.available === 'out_of_stock' ? 'Недоступен' : 'Купить'}
        </div>
      </div>
    `);

  }

  window.selectOption = function(productIndex, optionName, valueIndex) {
    const opt = productViewData[productIndex].options.find(o => o.name === optionName);
    const val = opt.values[valueIndex];
    if (val.available) {
      selectedOptionImage = val.image || p.image;
      selectedOptionName = val.name;
      renderDetailView();
    }
  }

  const originalGoBack = window.goBack;

  openView(renderDetailView);
}

function fixImg(url) {
  if (!url || typeof url !== 'string') return '/static/placeholder.png';
  return 'https://nekuri.by' + url.replace(/ /g, '%20').replace(/\\/g, '');
}

function search(e) {
  e.preventDefault();
  const val = document.getElementById('search-bar').value.toLowerCase();
  const arr = Object.values(catalog).flatMap(c => c.products || []);
  const found = arr.filter(p => p.title.toLowerCase().includes(val));
  openView(() => renderProducts(found));
}

function setContent(html) {
  const el = document.getElementById("content");
  el.style.opacity = 0;
  setTimeout(() => {
    el.innerHTML = html;
    el.style.opacity = 1;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, 100);
}

function addProductToCart(product, selectedOption = null) {
  const price = parseFloat(product.special_price || product.price || product.regular_price || 0);
  cart.add({
    id: product.id,
    title: product.title,
    price,
    option: selectedOption
  }, selectedOption);
}

window.initCatalogPage = initCatalogPage;
