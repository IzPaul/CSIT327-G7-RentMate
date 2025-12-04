/**
 * Auto-hide Django messages after 5 seconds
 * Add this script to any template that displays messages
 */
document.addEventListener('DOMContentLoaded', function () {
    const messages = document.querySelectorAll('.success-message, .error-message, .info-message, .warning-message');

    messages.forEach(function (message) {
        // Auto-hide after 5 seconds
        setTimeout(function () {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';

            // Remove from DOM after fade out
            setTimeout(function () {
                message.remove();
            }, 500);
        }, 5000);

        // Add close button
        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '×';
        closeBtn.style.cssText = 'float: right; cursor: pointer; margin-left: 10px; font-size: 20px;';
        closeBtn.onclick = function () {
            message.style.transition = 'opacity 0.3s ease';
            message.style.opacity = '0';
            setTimeout(function () {
                message.remove();
            }, 300);
        };
        message.insertBefore(closeBtn, message.firstChild);
    });
});
