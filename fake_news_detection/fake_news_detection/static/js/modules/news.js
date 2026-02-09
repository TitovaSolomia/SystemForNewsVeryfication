import { CONFIG } from './config.js';

export class NewsChecker {
    constructor() {
        this.checkBtn = document.querySelector(CONFIG.SELECTORS.checkBtn);
        this.newsInput = document.querySelector(CONFIG.SELECTORS.newsInput);
        this.resultDisplay = document.querySelector(CONFIG.SELECTORS.resultDisplay);
        this.historyList = document.querySelector(CONFIG.SELECTORS.historyList);
        this.init();
    }

    init() {
        if (!this.checkBtn || !this.newsInput) return;
        this.checkBtn.addEventListener('click', () => this.handleAnalysis());

        this.newsInput.addEventListener('input', () => this.autoResize());
        this.newsInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleAnalysis();
            }
        });

        setTimeout(() => this.autoResize(), 100);
    }

    autoResize() {
        if (!this.newsInput) return;

        this.newsInput.style.height = 'auto';

        const scrollHeight = this.newsInput.scrollHeight;
        const maxHeight = 200;

        if (scrollHeight > maxHeight) {
            this.newsInput.style.height = maxHeight + 'px';
            this.newsInput.style.overflowY = 'auto';
        } else {
            this.newsInput.style.height = scrollHeight + 'px';
            this.newsInput.style.overflowY = 'hidden';
        }
    }

    async handleAnalysis() {
        const text = this.newsInput.value.trim();
        if (!text) return;

        this.setLoading(true);

        try {
            const data = await this.fetchAnalysis(text);
            this.updateUI(text, data.result);
        } catch (error) {
            this.handleError(error);
        } finally {
            this.setLoading(false);
        }
    }

    async fetchAnalysis(text) {
        const response = await fetch(CONFIG.API_ENDPOINTS.CHECK_NEWS, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    }

    updateUI(originalText, result) {
        this.resultDisplay.innerHTML = `<h2 class="analysis-result">${result}</h2>`;

        this.appendToHistory(originalText, result);
    }

    appendToHistory(text, result) {
        if (!this.historyList || this.historyList.querySelector(CONFIG.SELECTORS.loginPrompt)) return;

        const dateStr = this.getFormattedDate();
        const historyItem = this.createHistoryElement(text, result, dateStr);

        this.historyList.prepend(historyItem);
    }

    createHistoryElement(text, result, date) {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.innerHTML = `
            <div class="history-header">
                <span class="history-date">${date}</span>
            </div>
            <p class="history-text">${text.substring(0, 40)}${text.length > 40 ? '...' : ''}</p>
            <span class="history-result">${result}</span>
        `;
        return div;
    }

    setLoading(isLoading) {
        if (isLoading) {
            this.resultDisplay.innerHTML = `<p class="analysis-loading">Analyzing...</p>`;
            if (this.checkBtn) this.checkBtn.disabled = true;
        } else {
            if (this.checkBtn) this.checkBtn.disabled = false;
        }
    }

    handleError(error) {
        console.error('FactChecker Error:', error);
        this.resultDisplay.innerHTML = `<p style="color: var(--accent-pink); font-weight: 600;">Connection failed. Try again.</p>`;
    }

    getFormattedDate() {
        const now = new Date();
        const options = { day: '2-digit', month: 'short' };
        const time = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
        return `${now.toLocaleDateString('en-GB', options)}, ${time}`;
    }
}
