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