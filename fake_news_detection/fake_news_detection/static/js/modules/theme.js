import { CONFIG } from './config.js';

export class ThemeManager {
    constructor() {
        this.themeToggle = document.querySelector(CONFIG.SELECTORS.themeToggle);
        this.init();
    }

    init() {
        const savedTheme = localStorage.getItem('theme') || CONFIG.THEMES.DARK;
        this.applyTheme(savedTheme);

        if (this.themeToggle) {
            this.themeToggle.checked = savedTheme === CONFIG.THEMES.LIGHT;
            this.themeToggle.addEventListener('change', () => this.handleToggle());
        }
    }

    handleToggle() {
        const newTheme = this.themeToggle.checked ? CONFIG.THEMES.LIGHT : CONFIG.THEMES.DARK;
        this.applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    }
}
