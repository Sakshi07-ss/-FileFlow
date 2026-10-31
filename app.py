import os
import shutil
import webview
from pathlib import Path


class FileOrganizer:
    def select_folder(self):
        result = webview.windows[0].create_file_dialog(
           webview.FileDialog.FOLDER
        )

        if result:
            return result[0]

        return ""
    
        if not folder_path:
            return {
                "success": False,
                "message": "Please select a folder."
            }

        folder = Path(folder_path).expanduser()

    def organize_files(self, folder_path):
        if not folder_path:
            return {
                "success": False,
                "message": "Please select a folder."
            }

        folder = Path(folder_path).expanduser()

        if not folder.is_dir():
            return {
                "success": False,
                "message": "The selected folder does not exist."
            }

        categories = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"],
            "Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
            "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Code": [".py", ".c", ".cpp", ".java", ".js", ".html", ".css", ".json"]
        }

        moved_count = 0
        errors = []

        try:
            # Find files in the selected folder and its subfolders.
            # Skip category folders created by FileFlow.
            files = []

            for current_folder, subfolders, filenames in os.walk(folder):
                subfolders[:] = [
                    name for name in subfolders
                    if name not in categories and name != "Others"
                ]

                for filename in filenames:
                    files.append(Path(current_folder) / filename)

            for file in files:
                if not file.is_file():
                    continue

                category = "Others"

                for name, extensions in categories.items():
                    if file.suffix.lower() in extensions:
                        category = name
                        break

                destination_folder = folder / category
                destination_folder.mkdir(exist_ok=True)

                destination = destination_folder / file.name
                counter = 1

                while destination.exists():
                    destination = destination_folder / (
                        f"{file.stem}_{counter}{file.suffix}"
                    )
                    counter += 1

                try:
                    shutil.move(str(file), str(destination))
                    moved_count += 1
                except OSError as error:
                    errors.append(f"{file.name}: {error}")

        except OSError as error:
            return {
                "success": False,
                "message": f"Could not read folder: {error}"
            }

        message = f"Successfully organized {moved_count} file(s)."

        if errors:
            message += (
                "\nSome files could not be moved:\n"
                + "\n".join(errors)
            )

        return {
            "success": len(errors) == 0,
            "message": message,
            "moved": moved_count
        }

if __name__ == "__main__":
    organizer = FileOrganizer()

    window = webview.create_window(
        "File Organizer",
        "frontend/index.html",
        js_api=organizer,
        width=1000,
        height=700,
        min_size=(750, 550),
        background_color="#111827"
    )

    webview.start()