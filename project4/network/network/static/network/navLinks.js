document.querySelector(".navbar-brand").addEventListener("click", handleLink);

const navLinks = [...document.querySelector(".navbar-nav").children];

const normalLinks = ["/login", "/logout", "/register"];

// Disable normal link behavior in Django templates, blocking page
// reload and allowing React Router to handle them
navLinks.forEach((child) => {
  child.addEventListener("click", handleLink);
});

// Update nav links style on page reload, django template links
["popstate", "load"].forEach((e) =>
  window.addEventListener(e, () => {
    navLinks.forEach((item) => {
      item.classList.remove("active");
      if (item.pathname === window.location.pathname) {
        item.classList.add("active");
      }
    });
  })
);

function handleLink(e) {
  const route = e.currentTarget.pathname;
  if (normalLinks.includes(route)) {
    return;
  }
  e.preventDefault();
  history.pushState("", route, route);
  history.pushState("", route, route);
  history.go(-1);
}
