// Only the Search page has the form; the other pages skip this file's work.
const form = document.getElementById("search-form");

if (form) {
  const queryBox = document.getElementById("query");

  // Example chips: put the example in the search box and submit the form.
  document.querySelectorAll(".chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      queryBox.value = chip.textContent;
      form.submit();
    });
  });

  // Do not send an empty query.
  form.addEventListener("submit", function (event) {
    if (queryBox.value.trim() === "") {
      event.preventDefault();
    }
  });
}

// Dataset and Inverted index pages: hide the table rows that do not contain the typed text.
const tableFilter = document.getElementById("table-filter");

if (tableFilter) {
  tableFilter.addEventListener("input", function () {
    const text = tableFilter.value.trim().toLowerCase();
    document.querySelectorAll("tbody tr").forEach(function (row) {
      row.hidden = !row.textContent.toLowerCase().includes(text);
    });
  });
}

// Colour theme switcher: remember the choice in the browser.
const swatches = document.querySelectorAll(".swatch");

function showTheme(name) {
  document.documentElement.dataset.theme = name;
  swatches.forEach(function (swatch) {
    swatch.setAttribute("aria-pressed", swatch.dataset.choice === name ? "true" : "false");
  });
}

swatches.forEach(function (swatch) {
  swatch.addEventListener("click", function () {
    showTheme(swatch.dataset.choice);
    try { localStorage.setItem("theme", swatch.dataset.choice); } catch (e) {}
  });
});

showTheme(document.documentElement.dataset.theme || "redbeige");
