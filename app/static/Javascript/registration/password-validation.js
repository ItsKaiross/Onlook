const passwordInput = document.getElementById('password');
const confirmInput  = document.getElementById('confirm_password');
const validationList = document.getElementById('validationList');
const strengthBar   = document.getElementById('strengthBar');
const strengthLabel = document.getElementById('strengthLabel');
const matchMsg      = document.getElementById('matchMsg');
const nextBtnValidation = document.getElementById('next_button3');

nextBtnValidation.disabled = true;

const rules = {
    length: { el: document.getElementById('rule-length'), test: v => v.length >= 8 },
    upper:  { el: document.getElementById('rule-upper'),  test: v => /[A-Z]/.test(v) },
    lower:  { el: document.getElementById('rule-lower'),  test: v => /[a-z]/.test(v) },
    number: { el: document.getElementById('rule-number'), test: v => /[0-9]/.test(v) },
    symbol: { el: document.getElementById('rule-symbol'), test: v => /[^A-Za-z0-9]/.test(v) },
};


const strengthLevels = [
    { label: '',           color: 'transparent', width: '0%'   },
    { label: 'Weak',       color: '#ef4444',      width: '20%'  },
    { label: 'Fair',       color: '#f97316',      width: '40%'  },
    { label: 'Good',       color: '#eab308',      width: '60%'  },
    { label: 'Strong',     color: '#22c55e',      width: '80%'  },
    { label: 'Very Strong',color: '#16a34a',      width: '100%' },
];



function updateNextBtn() {
    const val = passwordInput.value;
    const allRulesPassed = Object.values(rules).every(r => r.test(val));
    const passwordsMatch = val === confirmInput.value && confirmInput.value !== '';
    nextBtnValidation.disabled = !(allRulesPassed && passwordsMatch);
}


passwordInput.addEventListener('input', () => {
    const val = passwordInput.value;
    validationList.classList.toggle('visible', val.length > 0);

    let passed = 0;
    for (const key in rules) {
        const r = rules[key];
        const ok = r.test(val);
        r.el.className = 'rule ' + (val.length > 0 ? (ok ? 'pass' : 'fail') : '');
        r.el.querySelector('.rule-icon').textContent = ok ? '✓' : '✕';
        if (ok) passed++;
    }

    const level = strengthLevels[passed];
    strengthBar.style.width = level.width;
    strengthBar.style.background = level.color;
    strengthLabel.textContent = level.label;
    strengthLabel.style.color = level.color;

    passwordInput.classList.toggle('valid-input', passed === 5);
    passwordInput.classList.toggle('invalid-input', passed < 5 && val.length > 0);
    checkMatch();
    updateNextBtn();
});

confirmInput.addEventListener('input', () => {
    checkMatch();
    updateNextBtn();
});

function checkMatch() {
    const p = passwordInput.value, c = confirmInput.value;
    if (!c) { matchMsg.textContent = ''; confirmInput.classList.remove('valid-input','invalid-input'); return; }
    const ok = p === c;
    matchMsg.textContent = ok ? '✓ Passwords match' : '✕ Passwords do not match';
    matchMsg.style.color  = ok ? '#16a34a' : '#ef4444';
    confirmInput.classList.toggle('valid-input', ok);
    confirmInput.classList.toggle('invalid-input', !ok);
}

function togglePass(id, btn) {
    const input = document.getElementById(id);
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.querySelector('.eye-icon').style.display    = show ? 'none' : '';
    btn.querySelector('.eye-off-icon').style.display = show ? '' : 'none';
}


document.addEventListener("DOMContentLoaded", function () {
    const firstNameInput = document.getElementById("firstName");
    const lastNameInput = document.getElementById("lastName");
    const middleNameInput = document.getElementById("middleName");

    if (firstNameInput) {
        firstNameInput.addEventListener("input", function () {
            this.value = this.value.replace(/[^a-zA-Z\s]/g, '');
        });
    }

    if (lastNameInput) {
        lastNameInput.addEventListener("input", function () {
            this.value = this.value.replace(/[^a-zA-Z\s]/g, '');
        });
    }

    if (middleNameInput) {
        middleNameInput.addEventListener("input", function () {
            this.value = this.value.replace(/[^a-zA-Z\s]/g, '');
        });
    }
});
