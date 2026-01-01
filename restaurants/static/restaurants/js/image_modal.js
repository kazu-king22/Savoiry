document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  const closeBtn = modal?.querySelector(".close-modal");

  if (!modal || !modalImg) return;

  // ★ イベント委譲（これが超重要）
  document.addEventListener("click", (e) => {
    const img = e.target.closest(".visit-photo");
    if (!img) return;

    modal.style.display = "flex";
    modalImg.src = img.src;
  });

  // ✕ ボタン
  closeBtn?.addEventListener("click", () => {
    modal.style.display = "none";
  });

  // 背景クリック
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});
