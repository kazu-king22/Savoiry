document.addEventListener("DOMContentLoaded", function () {

  console.log("holiday ui loaded");

  console.log({
  box: document.getElementById("holiday-box"),
  list: document.getElementById("holiday-options"),
  hidden: document.getElementById("holiday-hidden-container")
  });

  const box = document.getElementById("holiday-box");
  const list = document.getElementById("holiday-options");
  const hiddenContainer = document.getElementById("holiday-hidden-container");

  if (!box || !list || !hiddenContainer) return;

  const text = box.querySelector(".holiday-text");

  box.addEventListener("click", function (e) {
    e.stopPropagation();   // ← これが決定打
    list.classList.toggle("hidden");
    box.classList.toggle("open");
  });

  list.addEventListener("click", function (e) {
    e.stopPropagation();
  });


  list.querySelectorAll(".holiday-option").forEach(opt => {
    opt.addEventListener("click", function (e) {
      e.stopPropagation();

      opt.classList.toggle("selected");
      hiddenContainer.innerHTML = "";

      const selected = Array.from(
        list.querySelectorAll(".holiday-option.selected")
      ).map(item => item.dataset.value);

      text.textContent = selected.length
        ? selected.join("、")
        : "選択してください";

      selected.forEach(value => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "holiday";
        input.value = value;
        hiddenContainer.appendChild(input);
      });
    });
  });
});
