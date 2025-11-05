/**
 * Prompt Template Engine - Main JavaScript
 */

// Global utilities and application logic
class PromptTemplateApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupTheme();
        this.setupNotifications();
        this.setupFormValidation();
        this.setupTemplateHighlighting();
        this.setupCopyButtons();
        this.setupAutoSave();
    }

    // Theme management
    setupTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        this.showNotification('Theme changed to ' + newTheme, 'success');
    }

    // Notification system
    setupNotifications() {
        // HTMX response handlers
        document.body.addEventListener('htmx:responseError', (e) => {
            this.showNotification('Request failed. Please try again.', 'error');
        });

        document.body.addEventListener('htmx:sendError', (e) => {
            this.showNotification('Network error. Please check your connection.', 'error');
        });
    }

    showNotification(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = 'toast toast-top toast-end';
        
        const alertClasses = {
            success: 'alert-success',
            error: 'alert-error',
            warning: 'alert-warning',
            info: 'alert-info'
        };
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-triangle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <div class="alert ${alertClasses[type] || alertClasses.info}">
                <i class="${icons[type] || icons.info} mr-2"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="btn btn-sm btn-ghost">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
    }

    // Form validation
    setupFormValidation() {
        // Enhanced form validation for template creation
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.highlightField(field, false);
                isValid = false;
            } else {
                this.highlightField(field, true);
            }
        });

        // Template-specific validation
        const templateText = form.querySelector('textarea[name="text"]');
        if (templateText) {
            const variables = this.extractVariables(templateText.value);
            if (variables.length === 0 && templateText.value.trim()) {
                this.showNotification('Consider adding variables to make your template more flexible', 'warning');
            }
        }

        return isValid;
    }

    highlightField(field, isValid) {
        field.classList.remove('input-error', 'input-success');
        field.classList.add(isValid ? 'input-success' : 'input-error');
        
        setTimeout(() => {
            field.classList.remove('input-error', 'input-success');
        }, 3000);
    }

    // Template syntax highlighting
    setupTemplateHighlighting() {
        const templateTexts = document.querySelectorAll('.template-text, textarea[name="text"]');
        templateTexts.forEach(element => {
            if (element.tagName === 'TEXTAREA') {
                element.addEventListener('input', () => {
                    this.updateVariablePreview(element);
                });
            } else {
                this.highlightTemplate(element);
            }
        });
    }

    highlightTemplate(element) {
        const text = element.textContent || element.innerText;
        const highlighted = this.highlightVariables(text);
        element.innerHTML = highlighted;
    }

    highlightVariables(text) {
        return text.replace(
            /<%=\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*%>/g,
            '<span class="variable-highlight"><%=$1%></span>'
        );
    }

    extractVariables(text) {
        const pattern = /<%=\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*%>/g;
        const variables = [];
        let match;
        
        while ((match = pattern.exec(text)) !== null) {
            if (!variables.includes(match[1])) {
                variables.push(match[1]);
            }
        }
        
        return variables;
    }

    updateVariablePreview(textarea) {
        const variables = this.extractVariables(textarea.value);
        const previewContainer = document.getElementById('current-variables');
        
        if (previewContainer) {
            if (variables.length > 0) {
                previewContainer.innerHTML = variables.map(v => 
                    `<span class="badge badge-primary">${v}</span>`
                ).join(' ');
            } else {
                previewContainer.innerHTML = '<span class="text-base-content/50 italic">No variables detected</span>';
            }
        }
    }

    // Copy functionality
    setupCopyButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.copy-btn') || e.target.matches('.copy-btn')) {
                e.preventDefault();
                const button = e.target.closest('.copy-btn') || e.target;
                const targetSelector = button.dataset.target;
                const target = document.querySelector(targetSelector);
                
                if (target) {
                    this.copyToClipboard(target.textContent, button);
                }
            }
        });
    }

    async copyToClipboard(text, button) {
        try {
            await navigator.clipboard.writeText(text);
            this.showCopySuccess(button);
            this.showNotification('Copied to clipboard!', 'success', 1500);
        } catch (err) {
            // Fallback for older browsers
            this.fallbackCopyToClipboard(text);
            this.showCopySuccess(button);
        }
    }

    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showNotification('Copied to clipboard!', 'success', 1500);
        } catch (err) {
            this.showNotification('Could not copy to clipboard', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    showCopySuccess(button) {
        const originalContent = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check mr-2"></i>Copied!';
        button.classList.add('copy-success');
        
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.classList.remove('copy-success');
        }, 1500);
    }

    // Auto-save functionality
    setupAutoSave() {
        const autoSaveForms = document.querySelectorAll('[data-autosave]');
        autoSaveForms.forEach(form => {
            const saveKey = form.dataset.autosave;
            let saveTimeout;
            
            // Load saved data
            this.loadAutoSaveData(form, saveKey);
            
            // Save on input
            form.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    this.saveFormData(form, saveKey);
                }, 1000);
            });
            
            // Clear on submit
            form.addEventListener('submit', () => {
                this.clearAutoSaveData(saveKey);
            });
        });
    }

    saveFormData(form, key) {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, fieldKey) => {
            data[fieldKey] = value;
        });
        
        localStorage.setItem(`autosave_${key}`, JSON.stringify(data));
    }

    loadAutoSaveData(form, key) {
        const savedData = localStorage.getItem(`autosave_${key}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                const confirmRestore = confirm('Found previously saved changes. Would you like to restore them?');
                
                if (confirmRestore) {
                    Object.entries(data).forEach(([fieldKey, value]) => {
                        const field = form.querySelector(`[name="${fieldKey}"]`);
                        if (field) {
                            field.value = value;
                            // Trigger events for dynamic updates
                            field.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    });
                    this.showNotification('Previous changes restored', 'info');
                } else {
                    this.clearAutoSaveData(key);
                }
            } catch (e) {
                this.clearAutoSaveData(key);
            }
        }
    }

    clearAutoSaveData(key) {
        localStorage.removeItem(`autosave_${key}`);
    }

    // Search functionality
    setupSearch() {
        const searchInputs = document.querySelectorAll('.search-input');
        searchInputs.forEach(input => {
            let searchTimeout;
            input.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        });
    }

    performSearch(query) {
        if (query.length < 2) return;
        
        fetch(`/api/templates/search/${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                this.updateSearchResults(data);
            })
            .catch(error => {
                this.showNotification('Search failed', 'error');
            });
    }

    updateSearchResults(templates) {
        const container = document.getElementById('search-results');
        if (container) {
            // Update search results UI
            container.innerHTML = this.renderTemplateCards(templates);
        }
    }

    renderTemplateCards(templates) {
        return templates.map(template => `
            <div class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow card-hover">
                <div class="card-body">
                    <h3 class="card-title">${template.name}</h3>
                    <p class="text-sm text-base-content/70">${template.description || 'No description'}</p>
                    <div class="card-actions justify-end">
                        <a href="/templates/${template.id}/use" class="btn btn-primary btn-sm">Use</a>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Utility methods
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit'
        });
    }

    // Export functionality
    exportTemplate(templateId) {
        fetch(`/api/templates/${templateId}`)
            .then(response => response.json())
            .then(template => {
                const dataStr = JSON.stringify(template, null, 2);
                const dataBlob = new Blob([dataStr], { type: 'application/json' });
                
                const link = document.createElement('a');
                link.href = URL.createObjectURL(dataBlob);
                link.download = `${template.name}.json`;
                link.click();
                
                this.showNotification('Template exported successfully', 'success');
            })
            .catch(error => {
                this.showNotification('Export failed', 'error');
            });
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PromptTemplateApp();
});

// Expose global functions for inline event handlers
window.toggleTheme = () => window.app.toggleTheme();
window.exportTemplate = (id) => window.app.exportTemplate(id);

// HTMX configuration
document.addEventListener('htmx:configRequest', (e) => {
    // Add CSRF token if available
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        e.detail.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
    }
});

// Service Worker registration (for offline support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}