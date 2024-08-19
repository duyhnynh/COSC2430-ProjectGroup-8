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
  var navbarStatus = 0;
  var verticalNavbar = document.querySelector("#hidden-vertical-navbar");
  if (navbarStatus == 0) {
    verticalNavbar.style.display = "flex";
    navbarStatus = 1;
  }
  if (navbarStatus == 1) {
    verticalNavbar.style.display = "none";
    navbarStatus = 0;
  }
}
