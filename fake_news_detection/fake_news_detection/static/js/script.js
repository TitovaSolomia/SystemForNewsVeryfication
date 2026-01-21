import { ThemeManager } from './modules/theme.js';
import { SidebarManager } from './modules/sidebar.js';
import { NewsChecker } from './modules/news.js';

document.addEventListener('DOMContentLoaded', () => {
    const theme = new ThemeManager();
    const sidebar = new SidebarManager();
    const news = new NewsChecker();

    console.log('FactChecker Initialized');
});