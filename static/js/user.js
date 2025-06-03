function initUserPage() {
  let userData = null;

  (async () => {
    if (!window.Telegram?.WebApp?.initDataUnsafe?.user) {
      showToast("Вы не авторизованы");
      goHome();
      return;
    }

    const tgUser = Telegram.WebApp.initDataUnsafe.user;
    const userKey = `user_${tgUser.id}`;
    userData = JSON.parse(localStorage.getItem(userKey)) || {
      id: tgUser.id,
      username: tgUser.username || `id${tgUser.id}`,
      first_name: tgUser.first_name || '',
      phone: tgUser.phone_number || '',
      photo_url: tgUser.photo_url || '/static/user-avatar.png'
    };

    const welcomeAvatar = document.getElementById('welcome-avatar');
    const welcomeMsg = document.getElementById('welcome-message');
    if (welcomeAvatar) welcomeAvatar.src = userData.photo_url;
    if (welcomeMsg) welcomeMsg.textContent = `Привет, ${userData.first_name || 'Пользователь'}!`;

    try {
      const response = await fetch(`/api/get-user?username=${encodeURIComponent(userData.username)}`);
      const result = await response.json();

      if (result.exists) {
        userData.first_name = result.user.Name || userData.first_name;
        userData.phone = result.user.Phone || userData.phone;
        localStorage.setItem(userKey, JSON.stringify(userData));
      } else {
        await fetch('/api/save-user', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            username: userData.username,
            name: userData.first_name,
            phone: userData.phone
          })
        });
      }

      showPersonalCabinet(userData);
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      showToast("Используются сохранённые данные");
      showPersonalCabinet(userData);
    }
    // Отладочный код - проверяем наличие кнопок в DOM
    console.log('Проверка кнопок "Назад":');
    console.log('Кнопка в orders-screen:', document.querySelector('#orders-screen #back-button'));
    console.log('Кнопка в order-detail-screen:', document.querySelector('#order-detail-screen #back-button'));
    
    // Проверяем computed styles
    const checkButtonStyles = (button) => {
      if (!button) return;
      const styles = window.getComputedStyle(button);
      console.log('Стили кнопки:', {
        display: styles.display,
        visibility: styles.visibility,
        opacity: styles.opacity,
        zIndex: styles.zIndex,
        position: styles.position
      });
    };
    
    checkButtonStyles(document.querySelector('#orders-screen #back-button'));
    checkButtonStyles(document.querySelector('#order-detail-screen #back-button'));
    
    document.getElementById('edit-profile-btn')?.addEventListener('click', () => {
      showEditForm(userData);
    });
    document.getElementById('cancel-edit-btn')?.addEventListener('click', () => {
      cancelEdit();
    });

    document.getElementById('save-profile-btn')?.addEventListener('click', async () => {
      await saveProfile(userData);
    });

    document.getElementById('my-orders-btn')?.addEventListener('click', () => {
      showOrdersScreen();
      loadUserOrders(userData);
    });
  })();
}

window.initUserPage = initUserPage;

// --------------------------------
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// --------------------------------

function showOrdersScreen() {
  document.getElementById('personal-cabinet').style.display = 'none';
  document.getElementById('orders-screen').style.display = 'block';
  document.getElementById('orders-list').style.paddingTop = '0';
  console.log('Кнопка в DOM:', document.querySelector('#back-button'));
  console.log('Видимость:', document.querySelector('#back-button').offsetParent !== null);
  const backBtn = document.getElementById('back-button');
  if (backBtn) {
    backBtn.style.display = 'block'; // Убедитесь, что это выполняется
    backBtn.style.visibility = 'visible';
    backBtn.style.opacity = '1';
    backBtn.onclick = goBackToProfile; // Явно устанавливаем обработчик
  }
  setTimeout(() => {
    document.getElementById('orders-screen').style.opacity = '1';
  }, 50);
}

function goBackToProfile() {
  document.getElementById('orders-screen').style.opacity = '0';
  setTimeout(() => {
    document.getElementById('orders-screen').style.display = 'none';
    document.getElementById('personal-cabinet').style.display = 'block';
    document.getElementById('personal-cabinet').style.opacity = '1';
  }, 300);
}

function goBackToOrders() {
  document.getElementById('order-detail-screen').style.opacity = '0';
  setTimeout(() => {
    document.getElementById('order-detail-screen').style.display = 'none';
    document.getElementById('orders-screen').style.display = 'block';
    document.getElementById('orders-screen').style.opacity = '1';
  }, 300);
}
function cancelEdit() {
  document.getElementById('edit-form').style.opacity = '0';
  setTimeout(() => {
    document.getElementById('edit-form').style.display = 'none';
    document.getElementById('personal-cabinet').style.display = 'block';
    document.getElementById('personal-cabinet').style.opacity = '1';
  }, 300);
}
function formatPrice(price) {
  if (price == null) return '0.00';
  let num = parseFloat(price.toString().replace(',', '.'));
  if (isNaN(num)) return '0.00';
  if (num > 100000 || (num % 1 === 0 && num > 100)) num /= 100;
  return num.toFixed(2);
}

async function viewOrderDetail(orderId) {
  document.getElementById('orders-screen').style.opacity = '0';
  setTimeout(() => {
    document.getElementById('orders-screen').style.display = 'none';
    document.getElementById('order-detail-screen').style.display = 'block';
    setTimeout(async () => {
      document.getElementById('order-detail-screen').style.opacity = '1';

      try {
        const response = await fetch(`/api/get-order/${orderId}`);
        const result = await response.json();

        if (result.status !== 'success') {
          document.getElementById('order-detail-content').innerHTML =
            `<p style="text-align: center; color: red;">${result.message || 'Ошибка загрузки заказа'}</p>`;
          return;
        }
        console.log('Кнопка в DOM:', document.querySelector('#back-button'));
        console.log('Видимость:', document.querySelector('#back-button').offsetParent !== null);
        const backBtn = document.getElementById('back-button');
        if (backBtn) {
          backBtn.style.display = 'block';
          backBtn.style.visibility = 'visible';
          backBtn.style.opacity = '1';
        }
        
        document.getElementById('order-detail-screen').style.display = 'block';
        setTimeout(async () => {
          document.getElementById('order-detail-screen').style.opacity = '1';
        }, 50);
        const order = result.order;
        const items = order.items || [];

        let content = `
          <div style="margin-bottom: 15px;">
            <div><strong>Номер заказа:</strong> ${order.order_id}</div>
            <div><strong>Дата:</strong> ${new Date(order.order_date).toLocaleString('ru-RU')}</div>
            <div><strong>Статус:</strong> <span style="color: ${getStatusColor(order.status)}">${order.status}</span></div>
          </div>
          <h3>Товары:</h3>
          <div style="margin-bottom: 15px;">`;

        items.forEach(item => {
          content += `
            <div style="padding: 10px 0; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between;">
              <div>
                <div>${item.title}</div>
                ${item.option ? `<div style="font-size: 12px; color: #666;">${item.option}</div>` : ''}
                <div style="font-size: 12px;">Количество: ${item.quantity}</div>
              </div>
              <div style="font-weight: bold;">${formatPrice(item.price * item.quantity)} BYN</div>
            </div>`;
        });

        content += `</div>
          <h3>Доставка:</h3>
          <div style="margin-bottom: 15px;">
            <p><strong>Получатель:</strong> ${order.customer_name || '—'}</p>
            <p><strong>Телефон:</strong> ${order.phone || '—'}</p>
            <p><strong>Адрес:</strong> ${order.city || ''} ${order.postcode || ''} ${order.address || ''}</p>
          </div>
          <h3>Суммы:</h3>
          <div style="background: #f9f9f9; padding: 15px; border-radius: 8px;">
            <div style="margin-bottom: 5px;">Сумма заказа: ${formatPrice(order.total)} BYN</div>
            <div style="margin-bottom: 5px;">Скидка 3%: -${formatPrice(order.discount)} BYN</div>
            <div style="margin-bottom: 5px;">Доставка: ${formatPrice(order.delivery)} BYN</div>
            <div style="font-weight: bold; margin-top: 10px;">Итого: ${formatPrice(order.final_total)} BYN</div>
          </div>`;

        document.getElementById('order-detail-content').innerHTML = content;
      } catch (error) {
        console.error('Ошибка загрузки деталей заказа:', error);
        document.getElementById('order-detail-content').innerHTML =
          '<p style="text-align: center; color: red;">Ошибка загрузки деталей заказа</p>';
      }
    }, 50);
  }, 300);
}

async function loadUserOrders(user) {
  try {
    const response = await fetch(`/api/get-orders?username=${encodeURIComponent(user.username)}`);
    const orders = await response.json();

    const ordersList = document.getElementById('orders-list');
    if (!ordersList) return;

    if (!orders.length) {
      ordersList.innerHTML = '<p style="text-align: center; padding: 20px;">У вас пока нет заказов</p>';
      return;
    }

    ordersList.innerHTML = orders.map(order => `
      <div class="order-item" onclick="viewOrderDetail('${order.order_id}')">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
          <span style="font-weight: bold;">Заказ №${order.order_id}</span>
          <span style="color: ${getStatusColor(order.status)}">${order.status}</span>
        </div>
        <div style="margin-bottom: 8px;">${new Date(order.order_date).toLocaleDateString('ru-RU')}</div>
        <div style="font-weight: bold;">${formatPrice(order.final_total)} BYN</div>
      </div>
    `).join('');
  } catch (error) {
    console.error('Ошибка загрузки заказов:', error);
    document.getElementById('orders-list').innerHTML =
      '<p style="text-align: center; color: red; padding: 20px;">Ошибка загрузки заказов</p>';
  }
}

function getStatusColor(status) {
  switch (status.toLowerCase()) {
    case 'в обработке': return '#ff9900';
    case 'отправлен': return '#009900';
    case 'отменён': return '#ff0000';
    default: return '#333';
  }
}

function showPersonalCabinet(user) {
  const welcomeScreen = document.getElementById('welcome-screen');
  const personalCabinet = document.getElementById('personal-cabinet');

  if (!user) return;

  document.getElementById('user-avatar-img').src = user.photo_url || '/static/user-avatar.png';
  document.getElementById('user-username').textContent = `@${user.username || 'неизвестно'}`;
  document.getElementById('user-name').textContent = user.first_name || 'Не указано';
  document.getElementById('user-phone').textContent = user.phone || 'Не указан';

  welcomeScreen.classList.add('fade-out');
  setTimeout(() => {
    welcomeScreen.style.display = 'none';
    personalCabinet.style.display = 'block';
    setTimeout(() => {
      personalCabinet.style.opacity = '1';
    }, 50);
  }, 500);
}

function showEditForm(user) {
  document.getElementById('edit-name').value = user.first_name || '';
  document.getElementById('edit-phone').value = user.phone || '';

  const personalCabinet = document.getElementById('personal-cabinet');
  const editForm = document.getElementById('edit-form');

  personalCabinet.style.opacity = '0';
  setTimeout(() => {
    personalCabinet.style.display = 'none';
    editForm.style.display = 'block';
    setTimeout(() => {
      editForm.style.opacity = '1';
    }, 50);
  }, 300);
}

async function saveProfile(user) {
  const name = document.getElementById('edit-name').value.trim();
  const phone = document.getElementById('edit-phone').value.trim();

  if (!name) return showToast("Введите ваше имя");

  try {
    const response = await fetch('/api/save-user', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ username: user.username, name, phone })
    });

    const result = await response.json();

    if (result.status === 'success') {
      user.first_name = name;
      user.phone = phone;
      localStorage.setItem(`user_${user.id}`, JSON.stringify(user));

      showPersonalCabinet(user);
      document.getElementById('edit-form').style.display = 'none';
      showToast("Данные успешно сохранены");
    } else {
      throw new Error(result.message || 'Ошибка сохранения');
    }
  } catch (error) {
    console.error('Ошибка сохранения:', error);
    showToast("Ошибка при сохранении данных");
  }
}

function showToast(message, duration = 2000) {
  const toast = document.createElement('div');
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 12px 24px;
    border-radius: 4px;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s;
  `;
  document.body.appendChild(toast);

  setTimeout(() => toast.style.opacity = 1, 10);
  setTimeout(() => {
    toast.style.opacity = 0;
    setTimeout(() => toast.remove(), 300);
  }, duration);
}
