(function () {
  const slides = [...document.querySelectorAll(".slide")];
  let index = 0;

  function show(i) {
    index = Math.max(0, Math.min(i, slides.length - 1));
    slides.forEach((s, j) => s.classList.toggle("active", j === index));
    const num = document.getElementById("slide-counter");
    if (num) num.textContent = `${index + 1} / ${slides.length}`;
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight" || e.key === " ") {
      e.preventDefault();
      show(index + 1);
    }
    if (e.key === "ArrowLeft") show(index - 1);
    if (e.key === "Home") show(0);
    if (e.key === "End") show(slides.length - 1);
  });

  document.addEventListener("click", (e) => {
    const x = e.clientX;
    if (x > window.innerWidth / 2) show(index + 1);
    else show(index - 1);
  });

  show(0);
})();
