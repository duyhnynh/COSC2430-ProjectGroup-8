window.addEventListener("scroll", function () {
  console.log(scrollY);
  var header = document.querySelector("header");
  if (window.scrollY > 0) {
    header.className = "header-scroll";
  } else {
    header.className = "header";
  }
});

function showVerticalNavbar() {
  var verticalNavbar = document.querySelector("#hidden-vertical-navbar");
  if (verticalNavbar.style.display == "none") {
    verticalNavbar.style.display = "flex";
  } else {
    verticalNavbar.style.display = "none";
  }
}
