const settingsButtons = document.querySelectorAll('[data-settings-section]');
const settingsPanels = document.querySelectorAll('[data-settings-panel]');

settingsButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const section = button.dataset.settingsSection;
    settingsButtons.forEach((item) => item.classList.toggle('is-active', item === button));
    settingsPanels.forEach((panel) => {
      const active = panel.dataset.settingsPanel === section;
      panel.hidden = !active;
      panel.classList.toggle('is-active', active);
    });

  });
});

const deleteAccountForm = document.querySelector('#delete-account-form');
const deleteConfirmation = document.querySelector('#delete-confirmation');
const deleteConfirmationValue = document.querySelector('#delete-confirmation-value');
if (deleteAccountForm && deleteConfirmation && deleteConfirmationValue) {
  deleteAccountForm.addEventListener('submit', (event) => {
    deleteConfirmationValue.value = deleteConfirmation.value.trim();
    if (deleteConfirmationValue.value !== 'DELETE') {
      event.preventDefault();
      deleteConfirmation.setCustomValidity('Type DELETE to confirm account deletion.');
      deleteConfirmation.reportValidity();
    }
  });
  deleteConfirmation.addEventListener('input', () => deleteConfirmation.setCustomValidity(''));
}
