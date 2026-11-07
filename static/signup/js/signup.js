document.querySelectorAll('.password-toggle').forEach((toggle) => {
  toggle.addEventListener('click', () => {
    const input = document.getElementById(toggle.dataset.target);
    const visible = input.type === 'text';
    input.type = visible ? 'password' : 'text';
    toggle.textContent = visible ? 'Show' : 'Hide';
    toggle.setAttribute('aria-label', visible ? 'Show password' : 'Hide password');
  });
});

const password = document.getElementById('id_password1');
const strength = document.querySelector('.strength');
if (password && strength) {
  const label = strength.querySelector('.strength__label');
  password.addEventListener('input', () => {
    const value = password.value;
    const level = value.length < 10 ? 'weak' : (/[A-Z]/.test(value) && /[^A-Za-z0-9]/.test(value) ? 'strong' : 'medium');
    strength.dataset.level = level;
    label.textContent = level === 'weak' ? 'Use 10+ characters' : (level === 'medium' ? 'Good — add a symbol or capital' : 'Strong password');
  });
}

document.querySelectorAll('form').forEach((form) => {
  form.addEventListener('submit', () => {
    const button = form.querySelector('.submit-button');
    if (button) {
      button.disabled = true;
      button.classList.add('is-loading');
    }
  });
});
