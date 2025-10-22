document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll(".bottom-nav li.active img").forEach(img => {
    const activeSrc = img.getAttribute("data-active");
    if (activeSrc) {
      img.setAttribute("src", activeSrc);
    }
  });
});
