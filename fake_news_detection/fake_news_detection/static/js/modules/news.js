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

        if (this.historyList) {
            this.historyList.addEventListener('click', (e) => {
                if (e.target.classList.contains('delete-btn')) {
                    this.handleDelete(e);
                }
            });
        }

        setTimeout(() => this.autoResize(), 100);
    }

    async handleDelete(e) {
        const btn = e.target;
        const itemId = btn.dataset.id;
        if (!itemId) return;

        try {
            const response = await fetch(`/delete-history/${itemId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            if (response.ok) {
                const item = btn.closest('.history-item');
                item.style.opacity = '0';
                setTimeout(() => item.remove(), 300);
            }
        } catch (error) {
            console.error('Failed to delete item:', error);
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
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

        const isUrl = text.match(/^https?:\/\//i);
        const wordCount = text.split(/\s+/).filter(w => w.length > 0).length;

        if (!isUrl && wordCount < 100) {
            this.handleError(new Error(`Text is too short (${wordCount} words). Please provide at least 100 words or a URL for accurate prediction.`));
            return;
        }

        this.setLoading(true);

        try {
            const data = await this.fetchAnalysis(text);
            this.updateUI(text, data.result, data.category, data.id);
        } catch (error) {
            this.handleError(error);
        } finally {
            this.setLoading(false);
        }
    }

    async fetchAnalysis(text) {
        try {
            const response = await fetch(CONFIG.API_ENDPOINTS.CHECK_NEWS, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Connection failed. Please try again later.');
            }

            return data;
        } catch (error) {
            if (error.name === 'SyntaxError') {
                throw new Error('Server returned an invalid response');
            }
            throw error;
        }
    }

    updateUI(originalText, result, category, id) {
        this.resultDisplay.innerHTML = `<h2 class="analysis-result" style="color: var(--text-primary) !important;">${result}</h2>`;

        this.appendToHistory(originalText, result, id);
    }

    appendToHistory(text, result, id, color) {
        if (!this.historyList || this.historyList.querySelector(CONFIG.SELECTORS.loginPrompt)) return;

        const dateStr = this.getFormattedDate();
        const historyItem = this.createHistoryElement(text, result, dateStr, id, color);

        this.historyList.prepend(historyItem);
    }

    createHistoryElement(text, result, date, id, color) {
        const div = document.createElement('div');
        div.className = 'history-item';
        if (color) div.style.borderLeftColor = color;
        div.innerHTML = `
            ${id ? `<button class="delete-btn" data-id="${id}" title="Delete">×</button>` : ''}
            <div class="history-header">
                <span class="history-date">${date}</span>
            </div>
            <p class="history-text">${text.substring(0, 40)}${text.length > 40 ? '...' : ''}</p>
            <span class="history-result" ${color ? `style="color: ${color}"` : ''}>${result}</span>
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
        const message = error.message || 'Connection failed. Try again.';
        this.resultDisplay.innerHTML = `<p style="color: var(--accent-pink); font-weight: 600;">${message}</p>`;
    }

    getFormattedDate() {
        const now = new Date();
        const options = { day: '2-digit', month: 'short' };
        const time = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
        return `${now.toLocaleDateString('en-GB', options)}, ${time}`;
    }
}
