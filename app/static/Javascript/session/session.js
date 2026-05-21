let idleTime = 0;

    function resetIdleTime() {
        idleTime = 0;
    }

    function pingServer() {
        fetch('/keepalive', { method: 'POST' });
    }

    setInterval(() => {
        idleTime++;
        if (idleTime < 5) {
            pingServer(); // extend session if active
        } else {
            window.location.href = "/logout"; // auto logout
        }
    }, 60000); // every minute

    window.onload = () => {
        document.addEventListener("mousemove", resetIdleTime);
        document.addEventListener("keypress", resetIdleTime);
    };



    