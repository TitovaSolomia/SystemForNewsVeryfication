import { CONFIG } from './config.js';

export class SidebarManager {
    constructor() {
        this.menuBtn = document.querySelector(CONFIG.SELECTORS.mobileMenuBtn);
        this.sidebar = document.querySelector(CONFIG.SELECTORS.sidebar);
        this.overlay = document.querySelector(CONFIG.SELECTORS.sidebarOverlay);
        this.init();
    }

    init() {
        if (!this.menuBtn || !this.sidebar || !this.overlay) return;

        this.menuBtn.addEventListener('click', () => this.toggleSidebar());
        this.overlay.addEventListener('click', () => this.closeSidebar());
    }

    toggleSidebar() {
        this.sidebar.classList.toggle('active');
        this.overlay.classList.toggle('active');
    }

    closeSidebar() {
        this.sidebar.classList.remove('active');
        this.overlay.classList.remove('active');
    }
}
