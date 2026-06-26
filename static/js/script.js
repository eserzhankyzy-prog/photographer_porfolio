document.addEventListener("DOMContentLoaded", () => {
    const navToggle = document.querySelector("[data-nav-toggle]");
    const navMenu = document.querySelector("[data-nav-menu]");

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", () => {
            const isOpen = navMenu.classList.toggle("open");
            navToggle.setAttribute("aria-expanded", String(isOpen));
        });

        navMenu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                navMenu.classList.remove("open");
                navToggle.setAttribute("aria-expanded", "false");
            });
        });
    }

    const filterButtons = document.querySelectorAll("[data-filter]");
    const photos = document.querySelectorAll(".photo[data-category]");

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const selected = button.dataset.filter;

            filterButtons.forEach((item) => item.classList.remove("active"));
            button.classList.add("active");

            photos.forEach((photo) => {
                const shouldShow = selected === "all" || photo.dataset.category === selected;
                photo.hidden = !shouldShow;
            });
        });
    });

    const lightbox = document.getElementById("lightbox");
    const lightboxImg = document.getElementById("lightbox-img");
    const lightboxCaption = document.getElementById("lightbox-caption");
    const closeButton = document.querySelector("[data-lightbox-close]");

    function closeLightbox() {
        if (!lightbox || !lightboxImg) {
            return;
        }

        lightbox.hidden = true;
        lightboxImg.src = "";
        document.body.classList.remove("lightbox-open");
    }

    document.querySelectorAll("[data-lightbox]").forEach((trigger) => {
        trigger.addEventListener("click", () => {
            if (!lightbox || !lightboxImg) {
                return;
            }

            lightboxImg.src = trigger.dataset.full;
            lightboxImg.alt = trigger.dataset.caption || "";

            if (lightboxCaption) {
                lightboxCaption.textContent = trigger.dataset.caption || "";
            }

            lightbox.hidden = false;
            document.body.classList.add("lightbox-open");
        });
    });

    if (closeButton) {
        closeButton.addEventListener("click", closeLightbox);
    }

    if (lightbox) {
        lightbox.addEventListener("click", (event) => {
            if (event.target === lightbox) {
                closeLightbox();
            }
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && lightbox && !lightbox.hidden) {
            closeLightbox();
        }
    });

    document.querySelectorAll("[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.dataset.confirm || "Are you sure?";
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });
});
