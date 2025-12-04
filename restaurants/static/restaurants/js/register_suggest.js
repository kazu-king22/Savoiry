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

    // ▼ 現在の入力欄の数をチェック
    const currentCount = tagContainer.querySelectorAll(".tag-row").length;
    if (currentCount >= 3) {
      alert("タグは最大3つまでです。");
      return;
    }

    // ▼ 新しいタグ欄を追加
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

if (box && list && hiddenContainer) {

  // ▼ 初期値反映（編集用）
  const initial = box.dataset.initial;
  if (initial) {
    const initialValues = initial.split("、").map(s => s.trim());

    // 表示にセット
    box.textContent = initial;

    // 選択状態にする
    list.querySelectorAll(".holiday-option").forEach(opt => {
      if (initialValues.includes(opt.dataset.value)) {
        opt.classList.add("selected");

        // hidden input 追加
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "holiday";
        input.value = opt.dataset.value;
        hiddenContainer.appendChild(input);
      }
    });
  }

  // ▼ ボックス開閉
  box.addEventListener("click", () => {
    list.classList.toggle("hidden");
  });

  // ▼ 選択処理
  list.querySelectorAll(".holiday-option").forEach(opt => {
    opt.addEventListener("click", () => {

      // 選択状態 ON/OFF
      opt.classList.toggle("selected");

      // hidden コンテナリセット
      hiddenContainer.innerHTML = "";

      // 選択されている項目を配列に
      const selected = Array.from(
        list.querySelectorAll(".holiday-option.selected")
      ).map(item => item.dataset.value);

      // 表示更新
      box.textContent = selected.length ? selected.join("、") : "選択してください";

      // hidden input を複数追加
      selected.forEach(value => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "holiday";
        input.value = value;
        hiddenContainer.appendChild(input);
      });
    });
  });
}
});