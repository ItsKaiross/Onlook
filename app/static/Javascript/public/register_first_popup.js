// Register First Popup Functionality

document.addEventListener('DOMContentLoaded', function() {
    const registerFirstBtn = document.querySelector('.login-or-sign-up');
    const registerFirstPopup = document.getElementById('register-first-popup');
    const blackBg = document.getElementById('bg-black');

    if (registerFirstBtn) {
        registerFirstBtn.addEventListener('click', function() {
            showRegisterPopup();
        });
    };
});

document.addEventListener('DOMContentLoaded', function() {
    const registerFirstBtn = document.querySelector('#register-first-btn1');
    const registerFirstPopup = document.getElementById('register-first-popup');
    const blackBg = document.getElementById('bg-black');

    if (registerFirstBtn) {
        registerFirstBtn.addEventListener('click', function() {
            showRegisterPopup();
        });
    };
});

function showRegisterPopup() {
    const popup = document.getElementById('register-first-popup');
    const blackBg = document.getElementById('bg-black');
    
    if (popup && blackBg) {
        document.body.classList.add('popup-open');
        popup.style.display = 'block';
        blackBg.style.display = 'block';
        
        setTimeout(() => popup.classList.add('show'), 10);
    }
}

function closeRegisterPopup() {
    const popup = document.getElementById('register-first-popup');
    const blackBg = document.getElementById('bg-black');
    
    if (popup && blackBg) {
        document.body.classList.remove('popup-open');
        popup.classList.remove('show');
        setTimeout(() => {
            popup.style.display = 'none';
            blackBg.style.display = 'none';
        }, 300);
    }
}

function goToRegister() {
    window.location.href = '/register';
}




// Login process

document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("login-btn");

    if (!loginBtn) return;

    loginBtn.addEventListener("click", async() => {
        const email = document.getElementById("login-email").value;
        const pass = document.getElementById("pass-login").value;

        loginBtn.disabled = true;
        loginBtn.textContent = "Logging in...";

        const response = await fetch("/signIn", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email:email, password:pass })
        });

        const result = await response.json();

        if(result.status === "user-login"){
            window.location.href = "/";
            loginBtn.disabled = false;
            loginBtn.textContent = "Log In";
        }else if(result.status === "police-login"){
            window.location.href = "/police-dashboard";
            loginBtn.disabled = false;
            loginBtn.textContent = "Log In";
        }else if(result.status === "admin-login"){
            window.location.href = "/admin-dashboard";
            loginBtn.disabled = false;
            loginBtn.textContent = "Log In";
        }else if(result.status === "restricted"){
            window.location.href = "/";   
            loginBtn.disabled = false;
            loginBtn.textContent = "Log In";
        }else if (result.status === "not-registered"){
            window.location.href = "/";
            loginBtn.disabled = false;
            loginBtn.textContent = "Log In";
        }else{
            window.location.href = "/";
            loginBtn.disabled = false;
            loginBtn.textContent = "Log In";
        }

    });
});


document.addEventListener("keydown", function(event){
    if(event.key === "Enter"){
        document.getElementById("login-btn").click();
    }
});