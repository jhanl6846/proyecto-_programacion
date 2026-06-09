// Auto-ocultar flash messages
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach(f => {
    setTimeout(() => {
      f.style.transition = "opacity 0.5s";
      f.style.opacity = "0";
      setTimeout(() => f.remove(), 500);
    }, 5000);
  });

  const menuToggle = document.querySelector(".menu-toggle");
  const sideMenu = document.querySelector(".side-menu");
  const sideClose = document.querySelector(".side-close");
  const sideOverlay = document.querySelector(".side-overlay");

  const setMenuOpen = (isOpen) => {
    document.body.classList.toggle("menu-open", isOpen);
    if (menuToggle) {
      menuToggle.setAttribute("aria-expanded", String(isOpen));
    }
    if (sideMenu) {
      sideMenu.setAttribute("aria-hidden", String(!isOpen));
    }
  };

  menuToggle?.addEventListener("click", () => setMenuOpen(true));
  sideClose?.addEventListener("click", () => setMenuOpen(false));
  sideOverlay?.addEventListener("click", () => setMenuOpen(false));

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setMenuOpen(false);
    }
  });
});
