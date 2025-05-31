class ModernFooter {
  constructor() {
    this.footer = document.querySelector('.footer-nav');
    this.indicator = document.querySelector('.footer-indicator');
    this.buttons = document.querySelectorAll('.footer-btn');
    this.activePage = 'home';
    
    this.init();
  }
  
  init() {
    this.setupEventListeners();
    this.setActiveButton(this.activePage);
    this.updateIndicatorSize();
    window.addEventListener('resize', () => this.updateIndicatorSize());
  }
  
  setActiveButton(page) {
    this.activePage = page;
    
    this.buttons.forEach(btn => {
      const isActive = btn.dataset.page === page;
      btn.classList.toggle('active', isActive);
      
      if (isActive) {
        this.moveIndicator(btn);
      }
    });
  }
  
  moveIndicator(activeBtn) {
    const btnRect = activeBtn.getBoundingClientRect();
    const footerRect = this.footer.getBoundingClientRect();
    const left = btnRect.left - footerRect.left;
    const width = btnRect.width;
    
    this.indicator.style.left = `${left}px`;
    this.indicator.style.width = `${width}px`;
  }
  
  updateIndicatorSize() {
    const activeBtn = document.querySelector(`.footer-btn[data-page="${this.activePage}"]`);
    if (activeBtn) {
      this.moveIndicator(activeBtn);
    }
  }
  
  setupEventListeners() {
    this.buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const page = btn.dataset.page;
        if (page === 'cart') {
          this.toggleCart(btn);
          return;
        }
        this.setActiveButton(page);
        // Ваш код перехода между страницами
      });
    });
  }
  
  toggleCart(btn) {
    btn.classList.toggle('active');
    if (typeof toggleCart === 'function') {
      toggleCart();
    }
  }
  
  updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
      badge.textContent = count > 9 ? '9+' : count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    }
  }
}
