document.addEventListener("DOMContentLoaded", function () {

  /* ===============================
     autocomplete on
  =============================== */
  document.querySelectorAll("input[type='text']").forEach(input => {
    input.setAttribute("autocomplete", "on");
  });

  /* ===============================
     タグ追加（最大3個）
  =============================== */
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

  /* ===============================
     休業日（カスタムUI）
  =============================== */
  const box = document.getElementById("holiday-box");
  const list = document.getElementById("holiday-options");
  const hiddenContainer = document.getElementById("holiday-hidden-container");

  if (!box || !list || !hiddenContainer) return;

  const text = box.querySelector(".holiday-text");
  const arrow = box.querySelector(".holiday-arrow");
  if (!text) return;

  /* ---------- 表示更新 ---------- */
  function updateDisplay() {
    const selected = Array.from(
      list.querySelectorAll(".holiday-option.selected")
    ).map(opt => opt.dataset.value);

    hiddenContainer.innerHTML = "";

    if (selected.length === 0) {
      text.textContent = "選択してください";
      return;
    }

    text.textContent = selected.join("、");

    selected.forEach(value => {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "holiday";
      input.value = value;
      hiddenContainer.appendChild(input);
    });
  }

/* ---------- 初期値反映 ---------- */
const initial = box.dataset.initial;
if (initial) {
  const initialValues = initial
    // 半角カンマを全角に統一
    .replace(/,/g, "、")
    // 分割
    .split("、")
    // 空白除去
    .map(v => v.trim())
    // 空文字除外
    .filter(v => v.length > 0);

  list.querySelectorAll(".holiday-option").forEach(opt => {
    if (initialValues.includes(opt.dataset.value)) {
      opt.classList.add("selected");
    }
  });

  // 表示＆hidden input 更新
  updateDisplay(initialValues);
}


  /* ---------- 開閉 ---------- */
  box.addEventListener("click", function () {
    list.classList.toggle("hidden");
    box.classList.toggle("open");
    arrow.textContent = list.classList.contains("hidden") ? "▼" : "▲";
  });

  /* ---------- 選択 ---------- */
  list.querySelectorAll(".holiday-option").forEach(opt => {
    opt.addEventListener("click", function (e) {
      e.stopPropagation();
      opt.classList.toggle("selected");
      updateDisplay();
    });
  });

});
