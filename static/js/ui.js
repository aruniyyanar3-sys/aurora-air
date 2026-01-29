document.addEventListener('DOMContentLoaded', function() {
    initFormValidation();
    initPasswordToggle();
    initMobileInput();
    initUploadZone();
});

function initFormValidation() {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    const predictForm = document.getElementById('predictForm');

    if (registerForm) {
        registerForm.addEventListener('submit', validateRegisterForm);
    }
    if (loginForm) {
        loginForm.addEventListener('submit', validateLoginForm);
    }
    if (predictForm) {
        predictForm.addEventListener('submit', validatePredictForm);
    }

    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateGmailField(this);
        });
    });

    const passwordInputs = document.querySelectorAll('input[name="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validatePasswordField(this);
        });
    });
}

function validateGmailField(input) {
    const value = input.value.trim().toLowerCase();
    const errorEl = document.getElementById(input.id + '-error');
    const pattern = /^[a-zA-Z0-9._%+-]+@gmail\.com$/;

    if (!value) {
        showError(input, errorEl, 'Email is required');
        return false;
    }

    if (!pattern.test(value)) {
        showError(input, errorEl, 'Email must be in format: username@gmail.com');
        return false;
    }

    hideError(input, errorEl);
    return true;
}

function validatePasswordField(input) {
    const value = input.value;
    const errorEl = document.getElementById(input.id + '-error');

    if (!value) {
        showError(input, errorEl, 'Password is required');
        return false;
    }

    if (value.length < 8) {
        showError(input, errorEl, 'Password must be at least 8 characters');
        return false;
    }

    if (!/[A-Z]/.test(value)) {
        showError(input, errorEl, 'Password must contain at least one uppercase letter');
        return false;
    }

    if (!/[a-z]/.test(value)) {
        showError(input, errorEl, 'Password must contain at least one lowercase letter');
        return false;
    }

    if (!/\d/.test(value)) {
        showError(input, errorEl, 'Password must contain at least one digit');
        return false;
    }

    if (!/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
        showError(input, errorEl, 'Password must contain at least one special character');
        return false;
    }

    hideError(input, errorEl);
    return true;
}

function validateMobileField(input) {
    const value = input.value.replace(/\D/g, '');
    const errorEl = document.getElementById(input.id + '-error');

    if (!value) {
        showError(input, errorEl, 'Mobile number is required');
        return false;
    }

    if (value.length !== 10) {
        showError(input, errorEl, 'Mobile number must be exactly 10 digits');
        return false;
    }

    hideError(input, errorEl);
    return true;
}

function validateNameField(input) {
    const value = input.value.trim();
    const errorEl = document.getElementById(input.id + '-error');

    if (!value) {
        showError(input, errorEl, 'Name is required');
        return false;
    }

    if (value.length < 2) {
        showError(input, errorEl, 'Name must be at least 2 characters');
        return false;
    }

    hideError(input, errorEl);
    return true;
}

function validateRegisterForm(e) {
    let isValid = true;

    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const mobileInput = document.getElementById('mobile');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');

    if (!validateNameField(nameInput)) isValid = false;
    if (!validateGmailField(emailInput)) isValid = false;
    if (!validateMobileField(mobileInput)) isValid = false;
    if (!validatePasswordField(passwordInput)) isValid = false;

    const confirmErrorEl = document.getElementById('confirm_password-error');
    if (passwordInput.value !== confirmPasswordInput.value) {
        showError(confirmPasswordInput, confirmErrorEl, 'Passwords do not match');
        isValid = false;
    } else {
        hideError(confirmPasswordInput, confirmErrorEl);
    }

    if (!isValid) {
        e.preventDefault();
    }

    return isValid;
}

function validateLoginForm(e) {
    let isValid = true;

    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (!emailInput.value.trim()) {
        const errorEl = document.getElementById('email-error');
        showError(emailInput, errorEl, 'Email is required');
        isValid = false;
    }

    if (!passwordInput.value) {
        const errorEl = document.getElementById('password-error');
        showError(passwordInput, errorEl, 'Password is required');
        isValid = false;
    }

    if (!isValid) {
        e.preventDefault();
    }

    return isValid;
}

function validatePredictForm(e) {
    let isValid = true;
    const fields = ['temperature', 'humidity', 'pm2_5', 'pm10', 'co', 'no2', 'so2', 'o3'];

    fields.forEach(field => {
        const input = document.getElementById(field);
        const errorEl = document.getElementById(field + '-error');

        if (!input.value.trim()) {
            showError(input, errorEl, 'This field is required');
            isValid = false;
        } else if (isNaN(parseFloat(input.value))) {
            showError(input, errorEl, 'Must be a valid number');
            isValid = false;
        } else {
            hideError(input, errorEl);
        }
    });

    if (!isValid) {
        e.preventDefault();
    }

    return isValid;
}

function showError(input, errorEl, message) {
    if (input) {
        input.classList.add('error');
    }
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.classList.add('show');
    }
}

function hideError(input, errorEl) {
    if (input) {
        input.classList.remove('error');
    }
    if (errorEl) {
        errorEl.classList.remove('show');
    }
}

function initPasswordToggle() {
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            if (input.type === 'password') {
                input.type = 'text';
                this.textContent = '🙈';
            } else {
                input.type = 'password';
                this.textContent = '👁️';
            }
        });
    });
}

function initMobileInput() {
    const mobileInputs = document.querySelectorAll('input[name="mobile"]');
    mobileInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            this.value = this.value.replace(/\D/g, '').slice(0, 10);
        });

        input.addEventListener('blur', function() {
            validateMobileField(this);
        });
    });
}

function initUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('csvFile');

    if (!uploadZone || !fileInput) return;

    uploadZone.addEventListener('click', () => fileInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length && files[0].name.endsWith('.csv')) {
            fileInput.files = files;
            updateUploadZoneText(files[0].name);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            updateUploadZoneText(fileInput.files[0].name);
        }
    });
}

function updateUploadZoneText(filename) {
    const uploadText = document.querySelector('.upload-text');
    if (uploadText) {
        uploadText.textContent = `Selected: ${filename}`;
    }
}

function confirmAction(message) {
    return confirm(message);
}

function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

function showNotification(message, type = 'info') {
    const existingNotif = document.querySelector('.notification');
    if (existingNotif) {
        existingNotif.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification alert alert-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
