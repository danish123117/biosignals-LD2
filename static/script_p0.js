document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById("loadBaselineBtn");
    const statusDiv = document.getElementById("baselineStatus");

    button.addEventListener("click", function () {
        fetch('/load_baseline', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            statusDiv.innerText = data.status || "Unknown response";
            statusDiv.style.color = data.status.toLowerCase().includes("success") ? "green" : "red";
        })
        .catch(error => {
            statusDiv.innerText = "Error loading baseline";
            statusDiv.style.color = "red";
        });
    });
});
