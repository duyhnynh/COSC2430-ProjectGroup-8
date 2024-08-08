window.addEventListener("scroll", function () {
  console.log(scrollY);
  var header = document.querySelector("header");
  if (window.scrollY > 0) {
    header.className = "header-scroll";
  } else {
    header.className = "header";
  }
});
