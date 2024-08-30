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
  var navbarHeight = window.parent.document.querySelector("#iframe-header");
  if (verticalNavbar.style.display == "none") {
    verticalNavbar.style.display = "flex";
    navbarHeight.style.height = "100%";
  } else {
    verticalNavbar.style.display = "none";
    navbarHeight.style.height = "60px";
  }
}

iframe.addEventListener("load", function () {
  const iframeDocument =
    iframe.contentDocument || iframe.contentWindow.document;
  const dropdown = iframeDocument.querySelector(".dropdown");

  dropdown.addEventListener("mouseover", () => {
    console.log("Hovering over dropdown button.");
    const navbarHeight = iframe;
    navbarHeight.style.height = "200px";
  });
  dropdown.addEventListener("mouseleave", () => {
    const navbarHeight = iframe;
    navbarHeight.style.height = "60px";
  });
});

document.addEventListener("DOMContentLoaded", function () {
  // Function to toggle instructor fields
  function toggleInstructorFields() {
    var instructorRadio = document.getElementById("instructor");
    var instructorFields = document.getElementById("instructor-fields");

    if (instructorRadio.checked) {
      instructorFields.style.display = "block";
    } else {
      instructorFields.style.display = "none";
    }
  }

  // Add event listeners to account type radio buttons
  var accountTypeRadios = document.querySelectorAll(
    'input[name="account-type"]'
  );
  accountTypeRadios.forEach(function (radio) {
    radio.addEventListener("change", toggleInstructorFields);
  });

  // Initial call to set the correct visibility on page load
  toggleInstructorFields();
});
