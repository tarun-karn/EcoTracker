/**
 * EcoTracker Dashboard JavaScript
 * Handles dashboard interactions, charts, and real-time updates
 */

class EcoTracker {
    constructor() {
        this.init();
    }

    init() {
        this.initChart();
        this.initChatbot();
        this.initAnimations();
        this.initNotifications();
    }

    /**
     * Initialize the carbon savings chart
     * Note: Chart initialization is handled in dashboard template
     */
    initChart() {
        // Chart is now initialized directly in the dashboard template
        // This method is kept for future chart enhancements
        console.log('Chart initialization handled by template');
    }

    /**
     * Initialize chatbot functionality
     */
    initChatbot() {
        const chatbotToggle = document.getElementById('chatbot-toggle');
        const chatbotWindow = document.getElementById('chatbot-window');
        const chatbotClose = document.getElementById('chatbot-close');
        const chatForm = document.getElementById('chat-form');
        const chatInput = document.getElementById('chat-input');
        const chatMessages = document.getElementById('chat-messages');

        if (!chatbotToggle) return;

        chatbotToggle.addEventListener('click', () => {
            chatbotWindow.classList.toggle('hidden');
            if (!chatbotWindow.classList.contains('hidden')) {
                chatInput.focus();
                this.animateElement(chatbotWindow, 'success-animation');
            }
        });

        if (chatbotClose) {
            chatbotClose.addEventListener('click', () => {
                chatbotWindow.classList.add('hidden');
            });
        }

        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleChatMessage(chatInput, chatMessages);
            });
        }
    }

    /**
     * Handle chat message submission
     */
    handleChatMessage(chatInput, chatMessages) {
        const message = chatInput.value.trim();
        if (!message) return;

        // Show user message
        this.addChatMessage(message, 'user', chatMessages);
        chatInput.value = '';

        // Show typing indicator
        const typingIndicator = this.addTypingIndicator(chatMessages);

        // Send to backend
        fetch('/dashboard/api/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({ query: message }),
        })
        .then(response => response.json())
        .then(data => {
            this.removeTypingIndicator(typingIndicator);
            this.addChatMessage(data.response, 'bot', chatMessages);
        })
        .catch(error => {
            console.error('Chatbot error:', error);
            this.removeTypingIndicator(typingIndicator);
            this.addChatMessage("Sorry, I'm having trouble connecting.", 'bot', chatMessages);
        });
    }

    /**
     * Add message to chat
     */
    addChatMessage(text, sender, chatMessages) {
        const messageEl = document.createElement('div');
        messageEl.className = 'mb-3 animate-fade-in';

        const bubbleEl = document.createElement('div');
        bubbleEl.className = 'p-3 rounded-lg inline-block max-w-xs sm:max-w-sm break-words';
        bubbleEl.textContent = text;

        if (sender === 'user') {
            messageEl.classList.add('text-right');
            bubbleEl.classList.add('bg-blue-500', 'text-white', 'ml-auto');
        } else {
            bubbleEl.classList.add('bg-gray-200', 'text-gray-800');
        }

        messageEl.appendChild(bubbleEl);
        chatMessages.appendChild(messageEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Add animation
        this.animateElement(messageEl, 'success-animation');
    }

    /**
     * Add typing indicator
     */
    addTypingIndicator(chatMessages) {
        const indicator = document.createElement('div');
        indicator.className = 'mb-3 typing-indicator';
        indicator.innerHTML = `
            <div class="bg-gray-200 text-gray-600 p-3 rounded-lg inline-block">
                <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
            </div>
        `;
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return indicator;
    }

    /**
     * Remove typing indicator
     */
    removeTypingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }

    /**
     * Initialize animations
     */
    initAnimations() {
        // Animate elements on scroll
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        });

        document.querySelectorAll('.stats-card, .badge-item').forEach((el) => {
            observer.observe(el);
        });
    }

    /**
     * Initialize notifications system
     */
    initNotifications() {
        // Auto-hide alerts after 5 seconds
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                this.fadeOut(alert);
            }, 5000);
        });
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg text-white ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        this.animateElement(notification, 'success-animation');
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            this.fadeOut(notification);
        }, 3000);
    }

    /**
     * Animate element
     */
    animateElement(element, animationClass) {
        element.classList.add(animationClass);
        setTimeout(() => {
            element.classList.remove(animationClass);
        }, 600);
    }

    /**
     * Fade out element
     */
    fadeOut(element) {
        element.style.transition = 'opacity 0.5s ease';
        element.style.opacity = '0';
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 500);
    }

    /**
     * Get CSRF token
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EcoTracker();
});

// Add fade-in animation class
const style = document.createElement('style');
style.textContent = `
    @keyframes fade-in {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
        animation: fade-in 0.5s ease-out;
    }
`;
document.head.appendChild(style);