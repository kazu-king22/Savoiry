document.addEventListener("DOMContentLoaded", function () {

  // ======================================
  // autocomplete on
  // ======================================
  document.querySelectorAll("input[type='text']").forEach(input => {
    input.setAttribute("autocomplete", "on");
  });


  // ======================================
  // タグ追加（最大 3 個まで）
  // ======================================
  const addTagBtn = document.getElementById("add-tag");
  const tagContainer = document.getElementById("tag-container");

  if (addTagBtn && tagContainer) {
    addTagBtn.addEventListener("click", function () {

      const currentCount = tagContainer.querySelectorAll(".tag-row").length;
      if (currentCount >= 3) {
        alert("タグは最大3つまでです。");
        return;
      }

      const newTag = `
        <div class="tag-row">
          <div class="input-with-arrow-tag">
            <input type="text" name="tags" class="tag-input"
                   placeholder="例：おしゃれ・個室など"
                   list="tag-list" autocomplete="on">
          </div>
        </div>`;
      tagContainer.insertAdjacentHTML("beforeend", newTag);
    });
  }


  // ======================================
  // 休業日（カスタム UI）
  // ======================================
  const box = document.getElementById("holiday-box");
  const list = document.getElementById("holiday-options");
  const hiddenContainer = document.getElementById("holiday-hidden-container");

  if (!box || !list || !hiddenContainer) return;

  const text = box.querySelector(".holiday-text");
  if (!text) return;

  // 初期値反映
  const initial = box.dataset.initial;
  if (initial) {
    const initialValues = initial.split("、").map(s => s.trim());
    text.textContent = initial;

    list.querySelectorAll(".holiday-option").forEach(opt => {
      if (initialValues.includes(opt.dataset.value)) {
        opt.classList.add("selected");

        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "holiday";
        input.value = opt.dataset.value;
        hiddenContainer.appendChild(input);
      }
    });
  }

  // 開閉
  box.addEventListener("click", function () {
    list.classList.toggle("hidden");
    box.classList.toggle("open");
  });

  // 選択
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
