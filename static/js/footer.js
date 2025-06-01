export function initFooter() {
  const setActiveFooter = (section) => {
    document.querySelectorAll('.footer-item').forEach(item => {
      item.classList.toggle('active', item.dataset.section === section);
    });
  };

  const goHome = () => {
    setActiveFooter('home');
    window.goHome(); // из глобального скрипта
  };

  const openCart = () => {
    setActiveFooter('cart');
    window.openCart();
  };

  const handleLogin = () => {
    const user = window.Telegram?.WebApp?.initDataUnsafe?.user;
    if (user) {
      location.href = '/user';
    } else {
      Telegram.WebApp.openTelegramLink('https://t.me/Shop_NEKURIBY_bot?start=login');
    }
  };

  document.getElementById('home-button')?.addEventListener('click', goHome);
  document.getElementById('catalog-button')?.addEventListener('click', () => {
    setActiveFooter('catalog');
    window.showSection('catalog');
  });
  document.getElementById('cart-footer-button')?.addEventListener('click', openCart);
  document.getElementById('promotions-button')?.addEventListener('click', () => {
    setActiveFooter('promotions');
    window.showSection('promotions');
  });
  document.getElementById('login-button')?.addEventListener('click', handleLogin);

  // Установка активного раздела при загрузке
  setActiveFooter('home');
}
