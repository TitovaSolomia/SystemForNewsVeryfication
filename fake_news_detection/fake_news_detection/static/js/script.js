document.addEventListener('DOMContentLoaded', function() {
    const checkBtn = document.getElementById('check-btn');
    const newsInput = document.getElementById('news-input');
    const resultDisplay = document.getElementById('result-display');
    const historyList = document.querySelector('.history-list');
    const themeToggle = document.getElementById('theme-toggle');

    if (checkBtn) {
        checkBtn.addEventListener('click', function() {
            const newsText = newsInput.value.trim();
            if (!newsText) return;

            resultDisplay.innerHTML = "<p style='color: gray; text-align: center;'>=Analazing...</p>";

            fetch('/check/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: newsText })
            })
            .then(response => response.json())
            .then(data => {
                resultDisplay.innerHTML = `<h2 style="color: white; text-align: center;">${data.result}</h2>`;

                const historyList = document.querySelector('.history-list');
    
                if (historyList) {
                    const isLoggedOut = historyList.innerText.includes('Sign in to see');

                    if (!isLoggedOut) {
                        const now = new Date();
                        const dateStr = now.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }) + 
                                        `, ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
                        
                        const newRecord = document.createElement('div');
                        newRecord.className = 'history-item';
                        newRecord.innerHTML = `
                            <small style="color: #888;">${dateStr}</small>
                            <p style="margin: 5px 0; color: #fff;">${newsText.substring(0, 40)}...</p>
                            <strong style="color: #4ade80;">${data.result}</strong>
                        `;
                        historyList.prepend(newRecord);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                resultDisplay.innerHTML = "<p style='color: red;'>Connection failed.</p>";
            });
        });
    }
});