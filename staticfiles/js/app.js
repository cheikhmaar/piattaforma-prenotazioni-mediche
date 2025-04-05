// Initialisation des composants Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Confirmation des actions critiques
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', event => {
            if (!confirm(element.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    // Gestion des dates
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.datepicker', {
            dateFormat: 'Y-m-d',
            allowInput: true
        });

        flatpickr('.datetimepicker', {
            enableTime: true,
            dateFormat: 'Y-m-d H:i',
            allowInput: true
        });
    }
});

// Fonction pour les requêtes AJAX
function makeRequest(url, method, data, successCallback, errorCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            successCallback(JSON.parse(xhr.responseText));
        } else {
            errorCallback(xhr.statusText);
        }
    };

    xhr.onerror = function() {
        errorCallback('Erreur réseau');
    };

    xhr.send(JSON.stringify(data));
}

// Helper pour les cookies
function getCookie(name) {
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

// Gestion des formulaires dynamiques
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.classList.contains('ajax-form')) {
        e.preventDefault();

        const formData = new FormData(form);
        const url = form.getAttribute('action');
        const method = form.getAttribute('method') || 'POST';

        makeRequest(
            url,
            method,
            Object.fromEntries(formData),
            function(response) {
                if (response.redirect) {
                    window.location.href = response.redirect;
                } else {
                    // Mettre à jour l'interface utilisateur
                    const message = response.message || 'Opération réussie';
                    const alertType = response.success ? 'success' : 'danger';

                    const alertHTML = `
                        <div class="alert alert-${alertType} alert-dismissible fade show" role="alert">
                            ${message}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    `;

                    const messagesContainer = document.querySelector('.messages-container');
                    if (messagesContainer) {
                        messagesContainer.insertAdjacentHTML('afterbegin', alertHTML);
                    }
                }
            },
            function(error) {
                console.error('Erreur:', error);
            }
        );
    }
});