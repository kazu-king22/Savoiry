document.addEventListener("DOMContentLoaded", function () {

  // autocomplete
  document.querySelectorAll("input[type='text']").forEach(input => {
    input.setAttribute("autocomplete", "on");
  });

  // タグ追加
  const addTagBtn = document.getElementById("add-tag");
  const tagContainer = document.getElementById("tag-container");

  addTagBtn.addEventListener("click", function () {
    const lastTag = tagContainer.querySelector(".tag-row:last-of-type");

    if (!lastTag) return;

    const newTag = lastTag.cloneNode(true);

    const input = newTag.querySelector("input");
    input.value = "";
    input.setAttribute("autocomplete", "on");

    tagContainer.appendChild(newTag);
});




  // 休業日表示
  const select = document.querySelector('select[name="holiday"]');
  const display = document.getElementById("selected-holidays");

  if (select && display) {
    const updateHoliday = () => {
      const selected = Array.from(select.selectedOptions).map(opt => opt.text);
      display.textContent = selected.length ? selected.join("、") : "";
    };

    select.addEventListener("change", updateHoliday);
    updateHoliday();
  }

});
