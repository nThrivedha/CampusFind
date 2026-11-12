document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (menuButton && navLinks) {
        menuButton.addEventListener("click", () => {
            const isOpen = navLinks.classList.toggle("nav-open");
            menuButton.setAttribute("aria-expanded", String(isOpen));
        });
    }

    document.querySelectorAll("form[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!window.confirm(form.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    const dateInput = document.querySelector('input[name="item_date"]');
    if (dateInput && !dateInput.value) {
        dateInput.max = new Date().toISOString().slice(0, 10);
    }

    document.querySelectorAll(".flash").forEach((message) => {
        window.setTimeout(() => {
            message.classList.add("flash-hide");
        }, 5000);
    });
});
