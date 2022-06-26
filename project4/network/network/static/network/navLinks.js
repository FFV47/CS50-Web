// Disable normal link behavior in Django templates, blocking page
// reload and allowing React Router to handle the paths
const navBar = document.querySelector(".navbar-nav");

const navLinks = [...navBar.children];

const normalLinks = ["/login", "/logout", "/register"];

navLinks.forEach((child) => {
  child.addEventListener("click", (e) => {
    const route = e.currentTarget.pathname;
    if (normalLinks.includes(route)) {
      return;
    }

    navLinks.forEach((item) => item.classList.remove("active"));
    e.currentTarget.classList.add("active");

    e.preventDefault();
    history.pushState("", route, route);
    history.pushState("", route, route);
    history.go(-1);
  });
});
