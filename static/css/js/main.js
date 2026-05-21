// ─── Auto-refresh slots via API ──────────────
function refreshSlots() {
    fetch('/api/slots')
        .then(response => response.json())
        .then(data => {
            console.log('Slots refreshed:', data.stats);
        })
        .catch(err => console.log('Refresh error:', err));
}

// ─── Show loading on form submit ─────────────
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function () {
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Processing...';
            }
        });
    });
});

// ─── Dismiss alerts automatically ────────────
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 4000);
    });
});