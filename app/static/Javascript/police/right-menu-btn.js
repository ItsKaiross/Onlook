// SIDEBAR TOGGLE
const burger = document.querySelector(".burger");
const sidebar = document.querySelector(".sidebar");

burger.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    burger.classList.toggle("active"); 
});


// ACTIVE LINK
const links = document.querySelectorAll(".sidebar a");
const activeLink = localStorage.getItem("activeLink");

if(activeLink){
    links.forEach(link => {
        if(
            link.getAttribute("href") === activeLink &&
            !link.parentElement.classList.contains("logout") 
        ){
            link.classList.add("active");
        }
    });
}

links.forEach(link => {
    link.addEventListener("click", () => {


        links.forEach(l => l.classList.remove("active"));

        if(!link.parentElement.classList.contains("logout")){
            link.classList.add("active");
            localStorage.setItem("activeLink", link.getAttribute("href"));
        } else {
            localStorage.removeItem("activeLink"); 
        }

    });
});


// NOTIFICATION BADGE POLLING
function updateNotificationBadge() {
    fetch('/police-notification-count')
        .then(res => res.json())
        .then(data => {
            const notifLink = document.querySelector('.notification a');
            if (!notifLink) return;

            let badge = notifLink.querySelector('.notification-badge');
            if (data.count > 0) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'notification-badge';
                    notifLink.appendChild(badge);
                }
                badge.textContent = data.count;
            } else if (badge) {
                badge.remove();
            }
        })
        .catch(() => {});
}

updateNotificationBadge();
setInterval(updateNotificationBadge, 30000);