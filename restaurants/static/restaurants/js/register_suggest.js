document.addEventListener("DOMContentLoaded", function () {

  // ===============================
  // 全 input に autocomplete を付ける
  // ===============================
  document.querySelectorAll("input[type='text']").forEach(input => {
    input.setAttribute("autocomplete", "on");
  });

  // ===============================
  // タグ追加ボタン
  // ===============================
  const addTagBtn = document.getElementById("add-tag");
  const tagContainer = document.getElementById("tag-container");

  addTagBtn.addEventListener("click", function () {
    const lastInput = document.querySelector(".tag-input:last-of-type");
    const newInput = lastInput.cloneNode(true);
    newInput.value = "";
    newInput.setAttribute("autocomplete", "on");
    tagContainer.appendChild(newInput);
  });


  // ===============================
  // 休業日表示
  // ===============================
  const select = document.querySelector('select[name="holiday"]');
  const display = document.getElementById("selected-holidays");

  if (select) {
    const updateHoliday = () => {
      const selected = Array.from(select.selectedOptions).map(opt => opt.text);
      display.textContent = selected.length ? selected.join("、") : "";
    };

    select.addEventListener("change", updateHoliday);
    updateHoliday();
  }

});
