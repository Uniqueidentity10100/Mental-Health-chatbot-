document.addEventListener('DOMContentLoaded', function() {
    // Add animation class after page load
    const authBox = document.querySelector('.auth-box');
    if (authBox) {
        setTimeout(() => {
            authBox.classList.add('fade-in');
        }, 100);
    }

    // Form validation
    const authForm = document.querySelector('.auth-form');
    if (authForm) {
        authForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            let isValid = true;
            
            // Reset previous error states
            clearErrors();

            // Username validation
            if (username.length < 3) {
                showError('username', 'Username must be at least 3 characters long');
                isValid = false;
            }

            // Password validation
            if (password.length < 6) {
                showError('password', 'Password must be at least 6 characters long');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // Show error message under input field
    function showError(fieldId, message) {
        const field = document.getElementById(fieldId);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
        field.classList.add('error');
    }

    // Clear all error messages
    function clearErrors() {
        document.querySelectorAll('.error-message').forEach(err => err.remove());
        document.querySelectorAll('.error').forEach(field => field.classList.remove('error'));
    }

    // Add input animations
    document.querySelectorAll('.form-group input').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentNode.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentNode.classList.remove('focused');
            }
        });

        // Add initial focused class if field has value
        if (input.value) {
            input.parentNode.classList.add('focused');
        }
    });
});
