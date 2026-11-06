
const browseButton = document.getElementById("browse-btn");
const organizeButton = document.getElementById("organize-btn");
const previewButton = document.getElementById("preview-btn");
const previewResult = document.getElementById("preview-result");
const undoButton = document.getElementById("undo-btn");
const folderPathDisplay = document.getElementById("folder-path");
const resultDisplay = document.getElementById("result");
const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");
const progressPercent = document.getElementById("progress-percent");
const statisticsSection = document.getElementById("statistics-section");
const statTotalFiles = document.getElementById("stat-total-files");
const statTotalSize = document.getElementById("stat-total-size");
const statLargestFile = document.getElementById("stat-largest-file");
const statLargestSize = document.getElementById("stat-largest-size");
const categoryStatistics = document.getElementById("category-statistics");
const statisticsButton = document.getElementById("statistics-btn");
const previewPanel = document.getElementById("preview-panel");
const previewSummary = document.getElementById("preview-summary");
const previewList = document.getElementById("preview-list");
const themeToggle = document.getElementById("theme-toggle");
const historySection = document.getElementById("history-section");
const historyList = document.getElementById("history-list");

let selectedFolder = "";
let progressTimer = null;
previewButton.addEventListener("click", async () => {
    if (!selectedFolder) {
        return;
    }

    previewButton.disabled = true;
    previewButton.textContent = "Scanning files...";

    try {
        const response = await window.pywebview.api.preview_files(
            selectedFolder
        );

       if (!response.success) {

    showResult(response.message, true);
}else {
    const counts = response.counts;

    previewResult.textContent =
        `Total files: ${response.total}\n` +
        Object.entries(counts)
            .map(([category, count]) => `${category}: ${count}`)
            .join("\n");

    previewResult.hidden = false;

    previewSummary.textContent =
        `Total files to organize: ${response.total}`;

    previewList.innerHTML = "";

    response.files.forEach(file => {
        const row = document.createElement("tr");

        const nameCell = document.createElement("td");
        nameCell.textContent = file.name;

        const categoryCell = document.createElement("td");
        categoryCell.textContent = file.category;

        const sizeCell = document.createElement("td");
        sizeCell.textContent = formatFileSize(file.size);

        row.append(nameCell, categoryCell, sizeCell);
        previewList.appendChild(row);
    });

    previewPanel.hidden = false;
}

        previewResult.hidden = false;
        statisticsButton.disabled = false;

    } catch (error) {
        previewResult.textContent = "Could not preview files.";
        previewResult.hidden = false;
        console.error(error);

    } finally {
        previewButton.disabled = false;
        previewButton.textContent = "👁 Preview files";
    }
});

browseButton.addEventListener("click", async () => {
    try {
        const folder = await window.pywebview.api.select_folder();

        if (folder) {
            selectedFolder = folder;
            folderPathDisplay.textContent = folder;
            organizeButton.disabled = false;
            previewButton.disabled = false;
            resultDisplay.hidden = true;
            resultDisplay.textContent = "";
            resultDisplay.classList.remove("error");
        }
    } catch (error) {
        showResult(
            "Could not open the folder picker. Please try again.",
            true
        );
        console.error(error);
    }
});

organizeButton.addEventListener("click", async () => {
    if (!selectedFolder) {
        showResult("Please select a folder first.", true);
        await loadHistory();
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
    undoButton.disabled = true;

    organizeButton.textContent = "Organizing files...";
    progressContainer.hidden = false;
    progressBar.style.width = "0%";
    progressPercent.textContent = "0%";

progressTimer = setInterval(updateProgress, 300);

    try {
        const response = await window.pywebview.api.organize_files(
            selectedFolder
        );

        showResult(response.message, !response.success);
        await loadHistory();
        undoButton.hidden = !response.can_undo;
        undoButton.disabled = !response.can_undo;

        if (response.success) {
            organizeButton.innerHTML =
                "✓ Organization complete";
        } else {
            organizeButton.innerHTML =
                "<span>✦</span> Try organizing again <span>→</span>";
        }

    } catch (error) {
        showResult(
            "Something went wrong while organizing files.",
            true
        );

        organizeButton.innerHTML =
            "<span>✦</span> Try organizing again <span>→</span>";

        console.error(error);

    } finally {
        clearInterval(progressTimer); 

        progressContainer.hidden = true;
        progressBar.style.width = "0%";
        progressPercent.textContent = "0%";
        
        browseButton.disabled = false;
        organizeButton.disabled = false;
    }
});

undoButton.addEventListener("click", async () => {
    const confirmed = window.confirm(
        "Are you sure you want to undo the last organization?\n\n" +
        "Your files will be restored to their original locations."
    );

    if (!confirmed) {
        return;
    }

    undoButton.disabled = true;
    organizeButton.disabled = true;
    browseButton.disabled = true;

    undoButton.textContent = "Restoring files...";

    try {
        const response = await window.pywebview.api.undo_organization();

        showResult(response.message, !response.success);

        undoButton.hidden = !response.can_undo;
        undoButton.disabled = !response.can_undo;

        if (!response.can_undo) {
            undoButton.textContent = "↶ Undo organization";
        }

        organizeButton.innerHTML =
            "<span>✦</span> Organize my files <span>→</span>";

    } catch (error) {
        showResult(
            "Something went wrong while restoring your files.",
            true
        );

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

window.addEventListener("pywebviewready", async () => {
    console.log("FileFlow is connected to Python.");

    await loadHistory();
});
async function updateProgress() {
    try {
        const progress = await window.pywebview.api.get_progress();

        progressBar.style.width = progress + "%";
        progressPercent.textContent = progress + "%";

    } catch (error) {
        console.error("Progress update failed:", error);
    }
}
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + " Bytes";

    const units = ["KB", "MB", "GB", "TB"];
    let size = bytes / 1024;
    let index = 0;

    while (size >= 1024 && index < units.length - 1) {
        size /= 1024;
        index++;
    }

    return size.toFixed(2) + " " + units[index];
}

async function loadStatistics() {
    if (!selectedFolder) return;

    try {
        const response = await window.pywebview.api.get_file_statistics(
            selectedFolder
        );

        if (!response.success) {
            showResult(response.message, true);
            return;
        }

        statTotalFiles.textContent = response.total_files;
        statTotalSize.textContent = formatFileSize(response.total_size);
        statLargestFile.textContent = response.largest_file;
        statLargestSize.textContent = formatFileSize(response.largest_size);

        categoryStatistics.innerHTML = "";

        for (const [category, details] of Object.entries(response.categories)) {
            const item = document.createElement("div");
            item.className = "category-stat";

            const name = document.createElement("span");
            name.textContent = category;

            const detailsText = document.createElement("span");
            detailsText.textContent =
                `${details.count} files · ${formatFileSize(details.size)}`;

            item.append(name, detailsText);
            categoryStatistics.appendChild(item);
        }

        statisticsSection.hidden = false;

    } catch (error) {
        showResult("Could not load file statistics.", true);
        console.error(error);
    }
}
statisticsButton.addEventListener("click", async () => {
    statisticsButton.disabled = true;
    statisticsButton.textContent = "Calculating...";

    await loadStatistics();

    statisticsButton.disabled = false;
    statisticsButton.textContent = "📊 File Statistics";
});
themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");

    const isLightMode = document.body.classList.contains("light-mode");

    themeToggle.textContent = isLightMode
        ? "🌙 Dark Mode"
        : "☀️ Light Mode";
});
async function loadHistory() {
    try {
        const history = await window.pywebview.api.get_history();

        historyList.innerHTML = "";

        if (!history || history.length === 0) {
            historyList.textContent = "No activity history yet.";
            return;
        }

        history.slice().reverse().forEach(item => {
            const card = document.createElement("div");
            card.className = "history-card";

            const date = document.createElement("p");
            date.textContent = "📅 " + item.date;

            const folder = document.createElement("p");
            folder.textContent = "📁 " + item.folder;

            const files = document.createElement("p");
            files.textContent = "📄 Files organized: " + item.files_organized;

            const status = document.createElement("p");
            status.textContent = "Status: " + item.status;

            card.append(date, folder, files, status);
            historyList.appendChild(card);
        });

    } catch (error) {
        historyList.textContent = "Could not load activity history.";
        console.error(error);
    }
}
document.getElementById("clear-history-btn").addEventListener("click", async () => {
    const confirmClear = confirm("Are you sure you want to clear all activity history?");

    if (!confirmClear) return;

    const response = await window.pywebview.api.clear_history();

    if (response.success) {
        await loadHistory();
        alert(response.message);
    } else {
        alert(response.message);
    }
});
document.getElementById("duplicate-check-btn").addEventListener("click", async () => {
    const folderPath = document.getElementById("folder-path").textContent.trim();

    if (!folderPath) {
        alert("Please select a folder first.");
        return;
    }

    const button = document.getElementById("duplicate-check-btn");
    const results = document.getElementById("duplicate-results");

    button.disabled = true;
    button.textContent = "Scanning...";
    results.textContent = "";

    try {
        const response = await window.pywebview.api.find_duplicates(folderPath);

        if (!response.success) {
            results.textContent = "Could not scan for duplicates.";
        } else if (response.count === 0) {
            results.textContent = "No duplicate files found!";
        } else {
            results.textContent = "";

            response.duplicates.forEach(item => {
                const entry = document.createElement("p");
                entry.textContent =
                    "Duplicate: " + item.file +
                    " | Original: " + item.duplicate_of;

                results.appendChild(entry);
            });
        }
    } catch (error) {
        results.textContent = "Error scanning for duplicates.";
        console.error(error);
    } finally {
        button.disabled = false;
        button.textContent = "🔍 Find Duplicate Files";
    }
});
document.getElementById("search-files-btn").addEventListener("click", async () => {
    const folderPath = document.getElementById("folder-path").textContent.trim();
    const keyword = document.getElementById("search-keyword").value.trim();
    const resultsDiv = document.getElementById("search-results");

    if (!folderPath) {
        alert("Please select a folder first.");
        return;
    }

    if (!keyword) {
        alert("Please enter a filename to search.");
        return;
    }

    resultsDiv.textContent = "Searching...";

    try {
        const response = await window.pywebview.api.search_files(folderPath, keyword);

        resultsDiv.textContent = "";

        if (!response.success) {
            resultsDiv.textContent = "Could not search this folder.";
        } else if (response.count === 0) {
            resultsDiv.textContent = "No matching files found.";
        } else {
            const heading = document.createElement("p");
            heading.textContent = `Found ${response.count} matching file(s):`;
            resultsDiv.appendChild(heading);

            response.results.forEach(file => {
                const item = document.createElement("p");
                item.textContent = "📄 " + file;
                resultsDiv.appendChild(item);
            });
        }
    } catch (error) {
        resultsDiv.textContent = "Search failed.";
        console.error(error);
    }
});