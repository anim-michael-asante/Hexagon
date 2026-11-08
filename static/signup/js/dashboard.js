const profileButton = document.querySelector('.profile-button');
const profileMenu = document.querySelector('.profile-menu__panel');
const notificationButton = document.querySelector('.notification-button');
const notificationPanel = document.querySelector('.notification-panel');
const notificationEmpty = document.querySelector('.notification-empty');

if (profileButton && profileMenu) {
  profileButton.addEventListener('click', () => {
    const isOpen = profileMenu.hidden;
    profileMenu.hidden = !isOpen;
    profileButton.setAttribute('aria-expanded', String(isOpen));
  });
}

if (notificationButton && notificationPanel) {
  notificationButton.addEventListener('click', () => {
    const isOpen = notificationPanel.hidden;
    notificationPanel.hidden = !isOpen;
    notificationButton.setAttribute('aria-expanded', String(isOpen));
  });
}

document.querySelector('.js-mark-notifications')?.addEventListener('click', () => {
  if (notificationEmpty) notificationEmpty.textContent = 'All notifications marked as read.';
});

document.querySelector('.js-delete-notifications')?.addEventListener('click', () => {
  if (notificationEmpty) notificationEmpty.textContent = 'No notifications to delete.';
});

const dashboard = document.querySelector('.dashboard-shell');
const scanButtons = document.querySelectorAll('.js-scan-projector');
const connectionTime = document.getElementById('connection-time');
const connectionLabel = document.querySelector('.connection-label');
const connectionStrength = document.querySelector('.connection-strength');
const disconnectButton = document.querySelector('.js-disconnect');
let scanTimer = null;
let connectedAt = null;

const formatConnectionTime = () => {
  if (!connectionTime || !connectedAt) return;
  const elapsed = Math.floor((Date.now() - connectedAt) / 1000);
  const hours = String(Math.floor(elapsed / 3600)).padStart(2, '0');
  const minutes = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
  const seconds = String(elapsed % 60).padStart(2, '0');
  connectionTime.textContent = `${hours}:${minutes}:${seconds}`;
};

scanButtons.forEach((button) => {
  button.addEventListener('click', () => {
    if (button.classList.contains('is-scanning')) {
      return;
    }

    button.classList.add('is-scanning');
    button.classList.add('is-loading');
    button.setAttribute('aria-busy', 'true');
    button.setAttribute('aria-label', 'Scanning for projector');
    button.querySelector('.button-label')?.replaceChildren('Scan for projector');
    scanButtons.forEach((scanButton) => {
      if (scanButton !== button) scanButton.classList.add('is-scanning');
    });
    scanTimer = window.setTimeout(() => {
      connectedAt = Date.now();
      formatConnectionTime();
      if (connectionLabel) connectionLabel.textContent = 'Connected';
      if (connectionStrength) {
        connectionStrength.classList.add('is-connected');
        connectionStrength.setAttribute('aria-label', 'Connection strength: 93 percent');
      }
      if (dashboard) dashboard.classList.add('is-lecture-ready');
      scanButtons.forEach((scanButton) => {
        scanButton.classList.remove('is-scanning');
        scanButton.classList.remove('is-loading');
        scanButton.setAttribute('aria-label', 'Scan for projector');
        scanButton.removeAttribute('aria-busy');
      });
      if (disconnectButton) disconnectButton.disabled = false;
      scanTimer = null;
    }, 900);
  });
});

if (disconnectButton) {
  disconnectButton.addEventListener('click', () => {
    window.clearTimeout(scanTimer);
    scanTimer = null;
    connectedAt = null;
    if (connectionTime) connectionTime.textContent = '00:00:00';
    if (connectionLabel) connectionLabel.textContent = 'Not connected';
    if (connectionStrength) {
      connectionStrength.classList.remove('is-connected');
      connectionStrength.setAttribute('aria-label', 'Connection strength: 0 percent');
    }
    if (dashboard) {
      dashboard.classList.remove('is-lecture-ready');
      dashboard.classList.add('is-disconnected');
    }
    disconnectButton.disabled = true;
  });
}

window.setInterval(formatConnectionTime, 1000);
