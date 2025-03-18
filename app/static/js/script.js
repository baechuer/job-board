document.addEventListener("DOMContentLoaded", function () {
    const appData = document.getElementById("app-data");
    const applicationId = appData.getAttribute("data-application-id");

    fetch(`/api/get_filename/${applicationId}`)
        .then(response => response.json())
        .then(data => {
            let filename = data.filename;
            let downloadLink = document.getElementById("downloadLink");
            let viewLink = document.getElementById("viewLink");
            viewLink.src = `/view/${filename}`;
            downloadLink.href = `/download/${filename}`;
            downloadLink.textContent = `Download ${filename}`;
        })
        .catch(error => console.error("Error fetching filename:", error));
});

document.addEventListener("DOMContentLoaded", function () {
    const statusText = document.getElementById("statusText");
    const actionLinks = document.getElementById("actionLinks");
    const appData = document.getElementById("app-data");
    const applicationId = appData.getAttribute("data-application-id");

    function fetchApplicationStatus() {
        fetch(`/get_application_status/${applicationId}`)
        .then(response => response.json())
        .then(data => {
            statusText.textContent = data.status; // Update status text
            updateActionLinks(data.status);
        })
        .catch(error => console.error('Error fetching status:', error));
    }

    function updateActionLinks(status) {
        if (status === "APPROVED" || status === "REJECTED") {
            actionLinks.style.display = "none"; // Hide links if already decided
        } else {
            actionLinks.style.display = "block"; // Show links if pending
        }
    }

    function sendApplicationAction(action) {
        fetch(`/handle_application/${applicationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action: action })
        })
        .then(response => response.json())
        .then(data => {
            statusText.textContent = data.status; // Update status without refreshing
            updateActionLinks(data.status);
        })
        .catch(error => console.error('Error:', error));
    }

    document.getElementById("approveLink").addEventListener("click", function (event) {
        event.preventDefault();
        sendApplicationAction("approve");
    });

    document.getElementById("rejectLink").addEventListener("click", function (event) {
        event.preventDefault();
        sendApplicationAction("reject");
    });

    // Load application status when the page loads
    fetchApplicationStatus();
});
