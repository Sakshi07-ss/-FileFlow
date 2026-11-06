
import os
import shutil
import webview
import json
import hashlib
from datetime import datetime
from pathlib import Path


class FileOrganizer: 

    def save_history(self, folder_path, moved_count, success):
        history_file = Path(__file__).parent / "history.json"

        history = []

        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as file:
                    history = json.load(file)
            except (json.JSONDecodeError, OSError):
                history = []

        history.append({
            "date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
            "folder": str(folder_path),
            "files_organized": moved_count,
            "status": "Success" if success else "Partial / Failed"
        })

        with open(history_file, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4) 
    
    def get_history(self):

        history_file = Path(__file__).parent / "history.json"

        if not history_file.exists():
            return []

        try:
            with open(history_file, "r", encoding="utf-8") as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            return []

    def clear_history(self):

        history_file = Path(__file__).parent / "history.json"

        try:
            if history_file.exists():
                history_file.unlink()

            return {
                "success": True,
                "message": "Activity history cleared successfully!"
            }

        except OSError:
            return {
                "success": False,
                "message": "Could not clear activity history."
            }

    def find_duplicates(self, folder_path):
        folder = Path(folder_path)
        hashes = {}
        duplicates = []

        for file_path in folder.rglob("*"):
            if not file_path.is_file():
                continue

            try:
                file_hash = hashlib.sha256(
                    file_path.read_bytes()
                ).hexdigest()

                if file_hash in hashes:
                    duplicates.append({
                        "file": str(file_path),
                        "duplicate_of": str(hashes[file_hash])
                    })
                else:
                    hashes[file_hash] = file_path

            except OSError:
                continue

        return {
            "success": True,
            "count": len(duplicates),
            "duplicates": duplicates
        }
    def search_files(self, folder_path, keyword):
        folder = Path(folder_path)
        results = []

        if not folder.exists() or not folder.is_dir():
            return {"success": False, "results": []}

        for file_path in folder.rglob("*"):
            if file_path.is_file() and keyword.lower() in file_path.name.lower():
                results.append(str(file_path))

        return {
            "success": True,
            "count": len(results),
            "results": results
        }

    def __init__(self):
     self.undo_history = []
     self.progress = 0

    def get_progress(self):
        return self.progress
    
    def select_folder(self):
        result = webview.windows[0].create_file_dialog(
            webview.FileDialog.FOLDER
        )

        if result:
            return result[0]

        return ""
    def get_file_statistics(self, folder_path):
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

        stats = {
            name: {"count": 0, "size": 0}
            for name in list(categories) + ["Others"]
        }

        largest_file = None
        largest_size = 0
        total_size = 0

        try:
            for current_folder, subfolders, filenames in os.walk(folder):
                subfolders[:] = [
                    name for name in subfolders
                    if name not in categories and name != "Others"
                ]

                for filename in filenames:
                    file = Path(current_folder) / filename

                    try:
                        if not file.is_file():
                            continue

                        size = file.stat().st_size
                        category = "Others"

                        for name, extensions in categories.items():
                            if file.suffix.lower() in extensions:
                                category = name
                                break

                        stats[category]["count"] += 1
                        stats[category]["size"] += size
                        total_size += size

                        if size > largest_size:
                            largest_size = size
                            largest_file = filename

                    except OSError:
                        continue

            return {
                "success": True,
                "total_files": sum(
                    item["count"] for item in stats.values()
                ),
                "total_size": total_size,
                "largest_file": largest_file or "None",
                "largest_size": largest_size,
                "categories": stats
            }

        except OSError as error:
            return {
                "success": False,
                "message": f"Could not scan folder: {error}"
            }
   
    def preview_files(self, folder_path):

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

        counts = {
            "Images": 0,
            "Documents": 0,
            "Videos": 0,
            "Audio": 0,
            "Archives": 0,
            "Code": 0,
            "Others": 0
        }
        file_details = []

        try:
            for current_folder, subfolders, filenames in os.walk(folder):
                subfolders[:] = [
                    name for name in subfolders
                    if name not in categories and name != "Others"
                ]

                for filename in filenames:
                    file = Path(current_folder) / filename
                    category = "Others"

                    for name, extensions in categories.items():
                        if file.suffix.lower() in extensions:
                            category = name
                            break

                    counts[category] += 1
                    try:
                        file_size = file.stat().st_size
                    except OSError:
                        file_size = 0

                    file_details.append({
                        "name": filename,
                        "category": category,
                        "size": file_size
                    })

            return {
                "files": file_details,
                "success": True,
                "counts": counts,
                "total": sum(counts.values())
                
            }

        except OSError as error:
            return {
                "success": False,
                "message": f"Could not scan folder: {error}"
            }

    def organize_files(self, folder_path):

        if not folder_path:
            return {
                "success": False,
                "message": "Please select a folder.",
                "moved": 0,
                "can_undo": False
            }

        folder = Path(folder_path).expanduser()

        if not folder.is_dir():
            return {
                "success": False,
                "message": "The selected folder does not exist.",
                "moved": 0,
                "can_undo": False
            }

        categories = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"],
            "Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
            "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Code": [".py", ".c", ".cpp", ".java", ".js", ".html", ".css", ".json"]
        }

        # Clear history from the previous operation.
        self.undo_history = []
        self.progress=0
        moved_count = 0
        errors = []

        try:
            files = []

            # Find files in the selected folder and its subfolders.
            # Skip category folders already managed by FileFlow.
            for current_folder, subfolders, filenames in os.walk(folder):
                subfolders[:] = [
                    name for name in subfolders
                    if name not in categories and name != "Others"
                ]
                
                for filename in filenames:
                    files.append(Path(current_folder) / filename)
            total_files = len(files)
            processed_files = 0

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
                    original_path = str(file)

                    shutil.move(str(file), str(destination))

                    # Record successful moves for Undo.
                    self.undo_history.append({
                        "original": original_path,
                        "destination": str(destination)
                    })

                    moved_count += 1
                    processed_files += 1

                    if total_files > 0:
                      self.progress = int((processed_files / total_files) * 100)

                except OSError as error:
                    errors.append(f"{file.name}: {error}")

        except OSError as error:
            return {
                "success": False,
                "message": f"Could not read folder: {error}",
                "moved": moved_count,
                "can_undo": len(self.undo_history) > 0
            }

        message = f"Successfully organized {moved_count} file(s)."

        if errors:
            message += (
                "\nSome files could not be moved:\n"
                + "\n".join(errors)
            )
        self.progress = 100
        success = len(errors) == 0

        self.save_history(
          folder_path,
          moved_count,
          success
        )

        return {
          "success": success,
          "message": message,
          "moved": moved_count,
          "can_undo": len(self.undo_history) > 0
        }

    def undo_organization(self):
        if not self.undo_history:
            return {
                "success": False,
                "message": "There is no organization to undo.",
                "can_undo": False
            }

        restored_count = 0
        errors = []
        remaining_history = []

        # Restore files in reverse order.
        for item in reversed(self.undo_history):
            original = Path(item["original"])
            destination = Path(item["destination"])

            if not destination.exists():
                errors.append(
                    f"Could not find organized file: {destination.name}"
                )
                remaining_history.append(item)
                continue

            if original.exists():
                errors.append(
                    f"Original location already contains a file: {original.name}"
                )
                remaining_history.append(item)
                continue

            try:
                original.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(destination), str(original))
                restored_count += 1

            except OSError as error:
                errors.append(f"{destination.name}: {error}")
                remaining_history.append(item)

        self.undo_history = list(reversed(remaining_history))

        message = f"Successfully restored {restored_count} file(s)."

        if errors:
            message += (
                "\nSome files could not be restored:\n"
                + "\n".join(errors)
            )

        return {
            "success": len(errors) == 0,
            "message": message,
            "restored": restored_count,
            "can_undo": len(self.undo_history) > 0
        }


if __name__ == "__main__":
    organizer = FileOrganizer()

    window = webview.create_window(
        "FileFlow",
        "frontend/index.html",
        js_api=organizer,
        width=1000,
        height=700,
        min_size=(750, 550),
        background_color="#111827"
    )

    webview.start()
