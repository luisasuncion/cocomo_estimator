document.querySelectorAll(".rating-select").forEach((select) => {
    select.addEventListener("change", () => {
        const target = document.querySelector(`[data-value-target="${select.dataset.target}"]`);
        const selected = select.options[select.selectedIndex];
        if (target && selected) {
            target.textContent = selected.dataset.value;
        }
    });
});
