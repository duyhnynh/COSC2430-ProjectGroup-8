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

window.onload = function () {
  var navbarHeight = document.querySelector("#iframe-header");

  if (!navbarHeight) {
    console.error("#iframe-header not found in the DOM.");
  } else {
    console.log(navbarHeight);
    // Proceed with your logic
  }
};

function showVerticalNavbar() {
  var verticalNavbar = document.querySelector("#hidden-vertical-navbar");
  var navbarHeight = window.parent.document.querySelector("#iframe-header");
  if (verticalNavbar.style.display == "none") {
    verticalNavbar.style.display = "flex";
    navbarHeight.style.height = "100%";
  } else {
    verticalNavbar.style.display = "none";
    navbarHeight.style.height = "60px";
  }
}
