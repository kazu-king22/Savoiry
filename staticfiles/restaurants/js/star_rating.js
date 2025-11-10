document.addEventListener("DOMContentLoaded", () => {
  const stars = document.querySelectorAll(".star");
  const ratingInput = document.getElementById("rating-value");
  let currentRating = 0;

  if (!stars.length) return;

  stars.forEach((star) => {
    // ホバー時
    star.addEventListener("mouseenter", () => {
      const value = parseInt(star.dataset.value);
      highlightStars(value);
    });

    // マウスが外れた時
    star.addEventListener("mouseleave", () => {
      highlightStars(currentRating);
    });

    // クリックで確定
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
