const browseButton = document.getElementById("browse-btn");
const organizeButton = document.getElementById("organize-btn");
const folderPathDisplay = document.getElementById("folder-path");
const resultDisplay = document.getElementById("result");

let selectedFolder = "";

browseButton.addEventListener("click", async () => {
    try {
        const folder = await window.pywebview.api.select_folder();

        if (folder) {
            selectedFolder = folder;
            folderPathDisplay.textContent = folder;
            organizeButton.disabled = false;

            resultDisplay.hidden = true;
            resultDisplay.textContent = "";
            resultDisplay.classList.remove("error");
        }
    } catch (error) {
        showResult("Could not open the folder picker. Please try again.", true);
        console.error(error);
    }
});

organizeButton.addEventListener("click", async () => {
    if (!selectedFolder) {
        showResult("Please select a folder first.", true);
        return;
    }

    const confirmed = window.confirm(
        "FileFlow will move files into category folders inside:\n\n" +
        selectedFolder +
        "\n\nContinue?"
    );

    if (!confirmed) {
        return;
    }

    organizeButton.disabled = true;
    browseButton.disabled = true;
    organizeButton.textContent = "Organizing files...";

    try {
        const response = await window.pywebview.api.organize_files(
            selectedFolder
        );

        showResult(response.message, !response.success);

        if (response.success) {
            organizeButton.textContent = "✓ Organization complete";
        } else {
            organizeButton.innerHTML =
                "<span>✦</span> Try organizing again <span>→</span>";
        }
    } catch (error) {
        showResult(
            "Something went wrong while organizing files. Please check the application.",
            true
        );

        organizeButton.innerHTML =
            "<span>✦</span> Try organizing again <span>→</span>";

        console.error(error);
    } finally {
        browseButton.disabled = false;
        organizeButton.disabled = false;
    }
});

function showResult(message, isError = false) {
    resultDisplay.textContent = message;
    resultDisplay.hidden = false;
    resultDisplay.classList.toggle("error", isError);
}

window.addEventListener("pywebviewready", () => {
    console.log("FileFlow is connected to Python.");
});