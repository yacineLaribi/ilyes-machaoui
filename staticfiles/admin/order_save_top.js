document.addEventListener("DOMContentLoaded", () => {
    const actions = document.querySelector(".submit-row");
    if (!actions) return;

    const clone = actions.cloneNode(true);
    clone.style.marginBottom = "15px";

    const container = document.querySelector("#changelist-form");
    container.prepend(clone);
});
