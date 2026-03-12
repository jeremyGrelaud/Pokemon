/**
 * Toast Notification System
 * Système de notifications élégantes pour remplacer les alert()
 * 
 * Usage:
 * showToast('Message', 'success');
 * showToast('Erreur!', 'error');
 * showToast('Info', 'info');
 * showToast('Attention', 'warning');
 */

class ToastNotification {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
    // Créer le conteneur de toasts s'il n'existe pas
    if (!document.getElementById('toast-container')) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    } else {
      this.container = document.getElementById('toast-container');
    }
  }

  show(message, type = 'info', duration = 4000) {
    const toast = this.createToast(message, type);
    this.container.appendChild(toast);

    // Animation d'entrée
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto-hide
    setTimeout(() => {
      this.hide(toast);
    }, duration);

    // Retourner l'élément pour permettre manipulation externe
    return toast;
  }

  createToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = this.getIcon(type);
    const title = this.getTitle(type);
    const color = this.getColor(type);

    toast.innerHTML = `
      <div class="toast-header" style="background-color: ${color};">
        <i class="fas fa-${icon} mr-2"></i>
        <strong class="mr-auto">${title}</strong>
        <button type="button" class="toast-close" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
      <div class="toast-progress">
        <div class="toast-progress-bar" style="background-color: ${color};"></div>
      </div>
    `;

    // Event listener pour le bouton de fermeture
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => this.hide(toast));

    // Event listener pour clic sur le toast
    toast.addEventListener('click', (e) => {
      if (!e.target.closest('.toast-close')) {
        this.hide(toast);
      }
    });

    return toast;
  }

  hide(toast) {
    toast.classList.remove('show');
    toast.classList.add('hide');

    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }

  getIcon(type) {
    const icons = {
      success: 'check-circle',
      error: 'exclamation-circle',
      warning: 'exclamation-triangle',
      info: 'info-circle'
    };
    return icons[type] || icons.info;
  }

  getTitle(type) {
    const titles = {
      success: 'Succès',
      error: 'Erreur',
      warning: 'Attention',
      info: 'Information'
    };
    return titles[type] || titles.info;
  }

  getColor(type) {
    const colors = {
      success: '#28a745',
      error: '#dc3545',
      warning: '#ffc107',
      info: '#17a2b8'
    };
    return colors[type] || colors.info;
  }

  // Méthodes de raccourci
  success(message, duration) {
    return this.show(message, 'success', duration);
  }

  error(message, duration) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration) {
    return this.show(message, 'info', duration);
  }

  // Notification avec action
  showWithAction(message, type, actionText, actionCallback, duration = 6000) {
    const toast = this.createToast(message, type);
    
    // Ajouter un bouton d'action
    const actionBtn = document.createElement('button');
    actionBtn.className = 'toast-action-btn';
    actionBtn.textContent = actionText;
    actionBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      actionCallback();
      this.hide(toast);
    });

    const body = toast.querySelector('.toast-body');
    body.appendChild(actionBtn);

    this.container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => this.hide(toast), duration);

    return toast;
  }

  // Notification persistante (ne disparaît pas automatiquement)
  showPersistent(message, type) {
    const toast = this.createToast(message, type);
    
    // Retirer la barre de progression
    const progressBar = toast.querySelector('.toast-progress');
    if (progressBar) {
      progressBar.remove();
    }

    this.container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);

    return toast;
  }

  // Effacer tous les toasts
  clearAll() {
    const toasts = this.container.querySelectorAll('.toast');
    toasts.forEach(toast => this.hide(toast));
  }
}

// Créer une instance globale
let toastNotification = new ToastNotification();

// Fonctions globales pour faciliter l'utilisation
function showToast(message, type = 'info', duration = 4000) {
  return toastNotification.show(message, type, duration);
}

function showSuccessToast(message, duration) {
  return toastNotification.success(message, duration);
}

function showErrorToast(message, duration) {
  return toastNotification.error(message, duration);
}

function showWarningToast(message, duration) {
  return toastNotification.warning(message, duration);
}

function showInfoToast(message, duration) {
  return toastNotification.info(message, duration);
}

function showToastWithAction(message, type, actionText, actionCallback, duration) {
  return toastNotification.showWithAction(message, type, actionText, actionCallback, duration);
}

function showPersistentToast(message, type) {
  return toastNotification.showPersistent(message, type);
}

function clearAllToasts() {
  toastNotification.clearAll();
}

// Export pour utilisation en module (optionnel)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ToastNotification,
    showToast,
    showSuccessToast,
    showErrorToast,
    showWarningToast,
    showInfoToast,
    showToastWithAction,
    showPersistentToast,
    clearAllToasts
  };
}