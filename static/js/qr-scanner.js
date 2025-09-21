/**
 * QR Code Scanner for EcoTracker Events
 * Uses html5-qrcode library for camera scanning
 */

class QRScanner {
    constructor() {
        this.html5QrCode = null;
        this.isScanning = false;
        this.init();
    }

    init() {
        this.initElements();
        this.bindEvents();
    }

    initElements() {
        this.scannerContainer = document.getElementById('qr-scanner');
        this.startBtn = document.getElementById('start-scan-btn');
        this.stopBtn = document.getElementById('stop-scan-btn');
        this.resultDiv = document.getElementById('scan-result');
        this.userIdInput = document.getElementById('user-id-input');
        this.checkinBtn = document.getElementById('checkin-btn');
        this.statusDiv = document.getElementById('status-message');
    }

    bindEvents() {
        if (this.startBtn) {
            this.startBtn.addEventListener('click', () => this.startScanning());
        }

        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stopScanning());
        }

        if (this.checkinBtn) {
            this.checkinBtn.addEventListener('click', () => this.performCheckin());
        }
    }

    async startScanning() {
        try {
            if (this.isScanning) return;

            // Import html5-qrcode dynamically
            if (typeof Html5Qrcode === 'undefined') {
                this.showStatus('Loading QR scanner...', 'info');
                await this.loadHtml5QrCode();
            }

            this.html5QrCode = new Html5Qrcode("qr-scanner");
            
            const config = {
                fps: 10,
                qrbox: { width: 250, height: 250 },
                aspectRatio: 1.0
            };

            await this.html5QrCode.start(
                { facingMode: "environment" }, // Use back camera
                config,
                (decodedText, decodedResult) => {
                    this.onScanSuccess(decodedText, decodedResult);
                },
                (errorMessage) => {
                    // Handle scan errors silently - they're frequent and normal
                }
            );

            this.isScanning = true;
            this.updateButtons();
            this.showStatus('Scanner active. Point camera at QR code.', 'success');

        } catch (error) {
            console.error('Error starting scanner:', error);
            this.showStatus('Failed to start camera. Please check permissions.', 'error');
        }
    }

    async stopScanning() {
        try {
            if (!this.isScanning || !this.html5QrCode) return;

            await this.html5QrCode.stop();
            this.html5QrCode.clear();
            
            this.isScanning = false;
            this.updateButtons();
            this.showStatus('Scanner stopped.', 'info');

        } catch (error) {
            console.error('Error stopping scanner:', error);
        }
    }

    onScanSuccess(decodedText, decodedResult) {
        console.log('QR Code scanned:', decodedText);
        
        // Stop scanning after successful scan
        this.stopScanning();
        
        // Extract event ID from scanned URL
        const eventId = this.extractEventId(decodedText);
        
        if (eventId) {
            this.showScanResult(decodedText, eventId);
            this.showStatus('QR code scanned successfully! Enter user ID to check in.', 'success');
        } else {
            this.showStatus('Invalid QR code. Please scan an event QR code.', 'error');
        }
    }

    extractEventId(scannedText) {
        // Extract event ID from URL like: /events/api/checkin/123/
        const match = scannedText.match(/\/events\/api\/checkin\/(\d+)\//);
        return match ? match[1] : null;
    }

    showScanResult(qrText, eventId) {
        if (this.resultDiv) {
            this.resultDiv.innerHTML = `
                <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h3 class="text-lg font-semibold text-green-800 mb-2">QR Code Scanned</h3>
                    <p class="text-sm text-green-700 mb-2">Event ID: ${eventId}</p>
                    <p class="text-xs text-green-600 break-all">${qrText}</p>
                </div>
            `;
            this.resultDiv.classList.remove('hidden');
        }

        // Store event ID for check-in
        if (this.checkinBtn) {
            this.checkinBtn.dataset.eventId = eventId;
            this.checkinBtn.classList.remove('hidden');
        }

        // Show user ID input
        if (this.userIdInput) {
            this.userIdInput.classList.remove('hidden');
        }
    }

    async performCheckin() {
        const eventId = this.checkinBtn?.dataset.eventId;
        const userId = document.getElementById('user-id')?.value.trim();

        if (!eventId || !userId) {
            this.showStatus('Please enter a valid user ID.', 'error');
            return;
        }

        try {
            this.showStatus('Processing check-in...', 'info');
            this.checkinBtn.disabled = true;

            const response = await fetch(`/events/api/checkin/${eventId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: `user_id=${encodeURIComponent(userId)}`
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                this.showStatus(data.message, 'success');
                this.resetScanner();
            } else {
                this.showStatus(data.message || 'Check-in failed.', 'error');
            }

        } catch (error) {
            console.error('Check-in error:', error);
            this.showStatus('Network error. Please try again.', 'error');
        } finally {
            this.checkinBtn.disabled = false;
        }
    }

    resetScanner() {
        // Hide result and input elements
        if (this.resultDiv) {
            this.resultDiv.classList.add('hidden');
        }
        if (this.userIdInput) {
            this.userIdInput.classList.add('hidden');
        }
        if (this.checkinBtn) {
            this.checkinBtn.classList.add('hidden');
        }

        // Clear user input
        const userIdField = document.getElementById('user-id');
        if (userIdField) {
            userIdField.value = '';
        }
    }

    updateButtons() {
        if (this.startBtn && this.stopBtn) {
            if (this.isScanning) {
                this.startBtn.classList.add('hidden');
                this.stopBtn.classList.remove('hidden');
            } else {
                this.startBtn.classList.remove('hidden');
                this.stopBtn.classList.add('hidden');
            }
        }
    }

    showStatus(message, type = 'info') {
        if (!this.statusDiv) return;

        const colorClasses = {
            'success': 'bg-green-100 text-green-800 border-green-200',
            'error': 'bg-red-100 text-red-800 border-red-200',
            'info': 'bg-blue-100 text-blue-800 border-blue-200'
        };

        this.statusDiv.className = `p-3 rounded-lg border ${colorClasses[type]}`;
        this.statusDiv.textContent = message;
        this.statusDiv.classList.remove('hidden');

        // Auto-hide after 5 seconds for non-error messages
        if (type !== 'error') {
            setTimeout(() => {
                this.statusDiv.classList.add('hidden');
            }, 5000);
        }
    }

    async loadHtml5QrCode() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/html5-qrcode/minified/html5-qrcode.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

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

// Initialize scanner when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new QRScanner();
});