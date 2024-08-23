var iframe = document.querySelector("iframe"); // Correctly target the iframe
iframe.addEventListener("load", function () {
  var header = iframe.contentDocument.querySelector("header"); // Access the header inside the iframe

  window.addEventListener("scroll", function () {
    if (window.scrollY > 0) {
      header.className = "header-scroll";
    } else {
      header.className = "header";
    }
  });
});
function showVerticalNavbar() {
  var verticalNavbar = document.querySelector("#hidden-vertical-navbar");
  if (verticalNavbar.style.display == "none") {
    verticalNavbar.style.display = "flex";
  } else {
    verticalNavbar.style.display = "none";
  }
}
