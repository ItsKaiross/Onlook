document.addEventListener('DOMContentLoaded', function() {
    checkAccountVerification();
});


async function checkAccountVerification() {
    try{
        const response = await fetch('/is-verified');
        const data = await response.json();
        
        console.log('Verification check response:', data);

        if (!data.verified){
            showVerificationNotification(); //Show notification
        } else {
            console.log('Account is verified, hiding notification');
        }
    } catch (error){
        console.error('Error checking verification:', error);
    }
}

function showVerificationNotification() {
    const notification = document.getElementById('verificationNotification');
    notification.style.display = "block";
}

function closeVerificationNotification() {
    const notification = document.getElementById('verificationNotification');
    notification.style.display = "none";
}



const overlay = document.getElementById("TwoFactorAuth-overlay");

const sendCodeBtn = document.getElementById("sendCode-btn");
const resendBtn = document.getElementById("resend-btn");
const cancelBtn = document.getElementById("cancel-btn");
const verifyBtn = document.getElementById("verify-btn");
const resetBtn = document.getElementById("reset-btn");

const RESEND_DELAY = 30;
let countdownInterval;

function show2faOverlay(){
    overlay.classList.add('active');
}

function startResendCountdown() {
    let remaining = RESEND_DELAY;

    resendBtn.textContent = `Resend (${remaining})`;
    resendBtn.classList.add("disabled");

    if (countdownInterval) clearInterval(countdownInterval);

    countdownInterval = setInterval(() => {
        remaining--;
        resendBtn.textContent = `Resend (${remaining})`;

        if (remaining <= 0) {
            clearInterval(countdownInterval);
            resendBtn.textContent = "Resend";
            resendBtn.classList.remove("disabled");
        }
    },1000);
}

//STEP  1 - send code
sendCodeBtn.addEventListener("click", async() => {
    sendCodeBtn.disabled = true;
    sendCodeBtn.textContent = "Sending...";

    const response = await fetch("/send_code", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})
    });

    const result = await response.json();

    if (result.status === "sent") {
        alert("Code sent!");
        document.querySelector(".step-email").style.display = "none";
        document.querySelector(".step-code").style.display = "block";
        startResendCountdown();
    }else {
        alert("Error sending code. Please try again.");
        sendCodeBtn.disabled = false;
        sendCodeBtn.textContent = "Send Code";
    }
});

// STEP 2 - verify code
verifyBtn.addEventListener("click", async() => {
    const code = document.getElementById("code-input").value.trim();

    if (!code || code.length !== 6) {
        alert("Please enter a valid 6-digit code.");
        return;
    }

    verifyBtn.disabled = true;
    verifyBtn.textContent = "Verifying...";

    const response = await fetch("/verify_2fa", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ code:code })
    });

    const result = await response.json();

    if (result.status ==="ok") {
        alert("Verified successfully!");
        document.getElementById("TwoFactorAuth-overlay").classList.remove("active");
        closeVerificationNotification();

        // Reset inputs
        document.getElementById("code-input").value = "";
        document.querySelector(".step-email").style.display = "block";
        document.querySelector(".step-code").style.display = "none";

        // stop countdown
        clearInterval(countdownInterval);
        resendBtn.textContent = "Resend";
        resendBtn.classList.remove("disabled");
        
        verifyBtn.disabled = false;
        verifyBtn.textContent = "Verify";
        sendCodeBtn.disabled = false;
        sendCodeBtn.textContent = "Send Code";

    } else if (result.status === "expired") {
        alert("Code has expired. Please request a new code.");
        verifyBtn.disabled = false;
        verifyBtn.textContent = "Verify";
    } else {
        alert("Invalid code. Please try again.");
        verifyBtn.disabled = false;
        verifyBtn.textContent = "Verify";
    }
})

// Resend code
resendBtn.addEventListener("click", async(e) => {
    e.preventDefault();

    resendBtn.classList.add("disabled");

    const response = await fetch("/resend_2fa", {method: "POST"});
    const result = await response.json();

    if (result.status  === "sent") {
        startResendCountdown();
        alert("New code sent!");
    }else {
        alert("Error sending code. Please try again.");
    }
});


// Reset (User another email)
resetBtn.addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelector(".step-email").style.display = "block";
    document.querySelector(".step-code").style.display = "none";
    document.getElementById("code-input").value = "";
    sendCodeBtn.disabled = false;
    sendCodeBtn.textContent = "Send Code";
    verifyBtn.disabled = false;
    verifyBtn.textContent = "Verify";

    // stop countdown
    clearInterval(countdownInterval);
    resendBtn.textContent = "Resend";
    resendBtn.classList.remove("disabled");
});

cancelBtn.addEventListener("click", () => {
    window.location.href = "/";
})
