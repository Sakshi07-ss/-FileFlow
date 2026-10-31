from pathlib import Path
import shutil

# File extensions and their destination folders
FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "Documents": [".pdf", ".docx", ".txt", ".doc", ".pptx", ".xlsx"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi"],
    "Audio": [".mp3", ".wav", ".aac", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar"],
    "Code": [".py", ".c", ".cpp", ".java", ".html", ".css", ".js"]
}


def get_category(file_path):
    """Return the category for a file based on its extension."""
    extension = file_path.suffix.lower()

    for category, extensions in FILE_TYPES.items():
        if extension in extensions:
            return category

    return "Others"


def organize_files(folder_path):
    """Organize files in the specified folder."""
    folder = Path(folder_path).expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        print("Error: The specified folder does not exist.")
        return

    for file_path in folder.iterdir():
        if not file_path.is_file():
            continue

        category = get_category(file_path)
        destination_folder = folder / category
        destination_folder.mkdir(exist_ok=True)

        destination = destination_folder / file_path.name

        # Avoid overwriting files with the same name
        counter = 1

        while destination.exists():
            destination = destination_folder / (
                f"{file_path.stem}_{counter}{file_path.suffix}"
            )
            counter += 1

        try:
            shutil.move(str(file_path), str(destination))
            print(f"Moved: {file_path.name} -> {category}/")
        except OSError as error:
            print(f"Could not move {file_path.name}: {error}")

    print("\nFile organization completed!")


if __name__ == "__main__":
    test_folder = input("Enter the folder path to organize: ").strip()
    organize_files(test_folder)