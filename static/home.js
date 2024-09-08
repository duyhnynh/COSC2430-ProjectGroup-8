const tabs = document.querySelectorAll(".featured-tab");
const contents = document.querySelectorAll(".featured-content");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    contents.forEach((content) => (content.style.display = "none"));
    tab.classList.add("active");
    const target = tab.getAttribute("data-target");
    document.getElementById(target).style.display = "block";
  });
});

document.querySelector(".featured-tab.active").click();
