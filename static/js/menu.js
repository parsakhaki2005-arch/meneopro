(function () {
    "use strict";

    const searchInput = document.getElementById("menuSearch");
    const clearSearch = document.getElementById("clearSearch");
    const cards = Array.from(document.querySelectorAll(".food-card"));
    const sections = Array.from(document.querySelectorAll(".menu-section"));
    const categoryButtons = Array.from(document.querySelectorAll(".category-chip"));
    const filterButtons = Array.from(document.querySelectorAll(".filter-chip"));
    const resultCount = document.getElementById("resultCount");
    const noResults = document.getElementById("noResults");
    const modal = document.getElementById("foodModal");
    const modalTitle = document.getElementById("modalTitle");
    const modalDescription = document.getElementById("modalDescription");
    const modalIngredients = document.getElementById("modalIngredients");
    const modalImage = document.getElementById("modalImage");
    const modalPrice = document.getElementById("modalPrice");
    const resetButton = document.getElementById("resetFilters");

    if (!searchInput || !modal) return;

    let activeCategory = "all";
    let activeFilter = "all";
    let previousFocus = null;

    function normalize(value) {
        return (value || "").toString()
            .toLocaleLowerCase("fa")
            .replace(//g, "ی")
            .replace(/ك/g, "ک")
            .replace(/[أإ]/g, "ا")
            .replace(/\s+/g, " ")
            .trim();
    }

    function formatPrice(value) {
        const number = Number(value);
        if (!Number.isFinite(number)) return "";
        return new Intl.NumberFormat("fa-IR").format(number);
    }

    function updateMenu() {
        const query = normalize(searchInput.value);
        let visibleCount = 0;

        cards.forEach(card => {
            const matchesSearch = !query ||
                normalize(card.dataset.name).includes(query) ||
                normalize(card.dataset.description).includes(query) ||
                normalize(card.dataset.ingredients).includes(query);

            const matchesCategory = activeCategory === "all" ||
                card.dataset.category === activeCategory;

            let matchesFilter = true;
            if (activeFilter === "featured") matchesFilter = card.dataset.featured === "true";
            if (activeFilter === "available") matchesFilter = card.dataset.available === "true";
            if (activeFilter === "unavailable") matchesFilter = card.dataset.available === "false";

            const visible = matchesSearch && matchesCategory && matchesFilter;
            card.classList.toggle("hidden", !visible);
            if (visible) visibleCount++;
        });

        sections.forEach(section => {
            const hasVisibleCard = section.querySelector(".food-card:not(.hidden)");
            section.classList.toggle("hidden", !hasVisibleCard);
        });

        resultCount.textContent = `${formatPrice(visibleCount)} غذا`;
        noResults.classList.toggle("hidden", visibleCount !== 0);
        clearSearch.style.display = searchInput.value ? "block" : "none";
    }

    searchInput.addEventListener("input", updateMenu);

    clearSearch.addEventListener("click", () => {
        searchInput.value = "";
        updateMenu();
        searchInput.focus();
    });

    categoryButtons.forEach(button => {
        button.addEventListener("click", () => {
            activeCategory = button.dataset.category;
            categoryButtons.forEach(item => item.classList.toggle("active", item === button));
            updateMenu();
        });
    });

    filterButtons.forEach(button => {
        button.addEventListener("click", () => {
            activeFilter = button.dataset.filter;
            filterButtons.forEach(item => item.classList.toggle("active", item === button));
            updateMenu();
        });
    });

    function closeModal() {
        modal.classList.add("hidden");
        document.body.style.overflow = "";
        if (previousFocus) previousFocus.focus();
    }

    function openModal(button) {
        const card = button.closest(".food-card");
        if (!card) return;

        previousFocus = button;
        modalTitle.textContent = card.dataset.name || "";
        modalDescription.textContent = card.dataset.description || "توضیحی برای این غذا ثبت نشده است.";
        modalIngredients.textContent = card.dataset.ingredients || "اطلاعات ترکیبات ثبت نشده است.";

        const image = card.querySelector(".food-image");
        if (image && image.tagName === "IMG") {
            modalImage.style.backgroundImage = `url("${image.src}")`;
        } else {
            modalImage.style.backgroundImage = "linear-gradient(135deg,#eee3d5,#d9c7b1)";
        }

        const price = card.dataset.price;
        const currency = card.dataset.currency || "تومان";
        const priceArea = card.querySelector(".food-price-area");
        const priceVisible = priceArea && !priceArea.querySelector(".price-hidden");
        modalPrice.textContent = priceVisible && price
            ? `${formatPrice(price)} ${currency}`
            : "";

        modal.classList.remove("hidden");
        document.body.style.overflow = "hidden";
        modal.querySelector(".modal-close").focus();
    }

    document.querySelectorAll(".details-button").forEach(button => {
        button.addEventListener("click", () => openModal(button));
    });

    modal.querySelectorAll("[data-close-modal]").forEach(element => {
        element.addEventListener("click", closeModal);
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape" && !modal.classList.contains("hidden")) closeModal();
    });

    if (resetButton) {
        resetButton.addEventListener("click", () => {
            searchInput.value = "";
            activeCategory = "all";
            activeFilter = "all";
            categoryButtons.forEach(button => button.classList.toggle("active", button.dataset.category === "all"));
            filterButtons.forEach(button => button.classList.toggle("active", button.dataset.filter === "all"));
            updateMenu();
        });
    }

    updateMenu();
})();
