class LocalizationSystem {
    constructor() {
        this.translations = {};
        this.currentLanguage = this.detectLanguage();
        this.loadTranslations();
    }

    detectLanguage() {
        const savedLang = localStorage.getItem('preferred_language');
        if (savedLang) return savedLang;
        
        const browserLang = navigator.language || navigator.userLanguage;
        return browserLang.startsWith('ru') ? 'ru' : 'en';
    }

    async loadTranslations() {
        try {
            const response = await fetch('/api/translations');
            this.translations = await response.json();
            this.applyTranslations();
        } catch (error) {
            console.error('translation loading error', error);
            try {
                const response = await fetch('/static/translations/translations.json');
                this.translations = await response.json();
                this.applyTranslations();
            } catch (fallbackError) {
                console.error('fallback translation loading error', fallbackError);
            }
        }
    }

    applyTranslations() {
        this.localizeElements();
        this.localizeAttributes();
    }

    localizeElements() {
        document.querySelectorAll('[data-localize]').forEach(element => {
            const key = element.getAttribute('data-localize');
            const translation = this.getTranslation(key);
            if (!translation) return;

            if (element.tagName === 'INPUT' && element.type === 'submit') {
                element.value = translation;
            } else {
                this.updateElementText(element, translation);
            }
        });
    }

    localizeAttributes() {
        document.querySelectorAll('[data-localize-attr]').forEach(element => {
            const attrConfig = element.getAttribute('data-localize-attr');
            attrConfig.split(',').forEach(attrPair => {
                const [attrName, key] = attrPair.split(':');
                const translation = this.getTranslation(key.trim());
                if (translation) {
                    element.setAttribute(attrName.trim(), translation);
                }
            });
        });
    }

    updateElementText(element, newText) {
        const hasSvg = element.querySelectorAll('svg').length > 0;
        if (hasSvg) {
            this.replaceTextNodes(element, newText);
        } else {
            element.textContent = newText;
        }
    }

    replaceTextNodes(element, newText) {
        const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);
        const textNodes = [];
        let node;
        
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }
        
        textNodes.forEach(textNode => textNode.remove());
        element.insertBefore(document.createTextNode(newText), element.firstChild);
    }

    getTranslation(key) {
        return this.translations[this.currentLanguage]?.[key] || key;
    }

    async setLanguage(lang) {
        this.currentLanguage = lang;
        this.applyTranslations();
        this.updateHtmlLang(lang);
        localStorage.setItem('preferred_language', lang);
        await this.saveLanguageToSession(lang);
    }

    updateHtmlLang(lang) {
        document.documentElement.lang = lang;
    }

    async saveLanguageToSession(lang) {
        try {
            await fetch('/set-language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `language=${lang}`
            });
        } catch (error) {
            console.error('language saving error', error);
        }
    }

    async init() {
        const savedLang = localStorage.getItem('preferred_language');
        if (savedLang) {
            this.currentLanguage = savedLang;
            await this.saveLanguageToSession(savedLang);
        }
        this.updateHtmlLang(this.currentLanguage);
        this.loadTranslations();
    }
}

window.localization = new LocalizationSystem();

window.t = (key) => window.localization.getTranslation(key);

document.addEventListener('DOMContentLoaded', async () => {
    await window.localization.init();
    setupLanguageButtons();
});

function setupLanguageButtons() {
    const langButtons = document.querySelectorAll('.lang-btn');
    
    langButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const lang = button.getAttribute('data-lang');
            await window.localization.setLanguage(lang);
            
            langButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });
    
    const activeButton = document.querySelector(`[data-lang="${window.localization.currentLanguage}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
}
