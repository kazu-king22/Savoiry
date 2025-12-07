document.addEventListener("DOMContentLoaded", () => {
  const stars = document.querySelectorAll(".star");
  const ratingInput = document.getElementById("rating-value");

  // ⭐ 評価フォームが無いページ（詳細画面など）は処理しない
  if (!ratingInput || !stars.length) return;

  // ★ 現在の値を初期状態としてセット
  let currentRating = parseInt(ratingInput.value || "0", 10);

  // 初期状態の星を反映
  highlightStars(currentRating);

  // クリック・ホバー処理
  stars.forEach(star => {
    star.addEventListener("mouseenter", () => {
      highlightStars(parseInt(star.dataset.value));
    });

    star.addEventListener("mouseleave", () => {
      highlightStars(currentRating);
    });

    star.addEventListener("click", () => {
      currentRating = parseInt(star.dataset.value);
      ratingInput.value = currentRating;
      highlightStars(currentRating);
    });
  });

  function highlightStars(count) {
    stars.forEach((s, i) => {
      s.classList.toggle("selected", i < count);
    });
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  const modalDate = document.getElementById("modal-date");
  const closeBtn = document.querySelector(".close-modal");

  document.querySelectorAll(".visit-photo").forEach(img => {
    img.addEventListener("click", () => {
      modal.style.display = "flex";
      modalImg.src = img.src;

      // ★ 写真に埋め込んだ訪問日を取得
      const visitDate = img.dataset.visitDate;
      modalDate.textContent = visitDate ? `訪問日：${visitDate}` : "";
    });
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});
