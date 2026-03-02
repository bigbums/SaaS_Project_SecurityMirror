import os
import sys
import shutil
import datetime
import json
import zipfile

# --- Load settings from JSON ---
settings_file = "settings.json"
if os.path.exists(settings_file):
    with open(settings_file, "r", encoding="utf-8") as f:
        settings = json.load(f)
else:
    settings = {}

reports_dir = settings.get("reports_dir", "reports")
backup_dir = settings.get("backup_dir", reports_dir)
retention_days = settings.get("backup_retention_days", 30)
log_file = settings.get("log_file", os.path.join(reports_dir, "export_log.txt"))
error_file = os.path.join(reports_dir, "error_log.txt")
summary_file = os.path.join(reports_dir, "run_summary.txt")

def log_error(message):
    """Write error messages into error_log.txt with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] ERROR: {message}\n"
    with open(error_file, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry.strip())

def append_test_entry(log_file, max_entries=10):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_line = f"TEST ENTRY - Scheduled run at {timestamp}\n"
        summary_line = f"Last run: {timestamp}\n"

        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        else:
            lines = []

        # Remove any existing summary line
        lines = [line for line in lines if not line.startswith("Last run:")]

        # Filter only test entries
        test_entries = [line for line in lines if line.startswith("TEST ENTRY -")]

        # Keep only the last (max_entries - 1) and add the new one
        test_entries = test_entries[-(max_entries - 1):] + [test_line]

        # Remove old test entries
        non_test_entries = [line for line in lines if not line.startswith("TEST ENTRY -")]

        # Combine back
        new_content = [summary_line] + non_test_entries + test_entries

        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(new_content)

        print(f"Updated {log_file} with test entry and summary line.")
    except Exception as e:
        log_error(f"Failed to update {log_file}: {e}")

def is_utf8(file_path):
    """Check if file is already UTF-8 encoded."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.read()
        return True
    except UnicodeDecodeError:
        return False

def convert_to_utf8(log_file):
    try:
        if not os.path.exists(log_file):
            log_error(f"{log_file} does not exist.")
            return

        if is_utf8(log_file):
            print(f"{log_file} is already UTF-8. No conversion needed.")
        else:
            # --- Create timestamped backup and compress immediately ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = f"{os.path.basename(log_file).replace('.txt','')}_backup_{timestamp}.txt"
            backup_path = os.path.join(backup_dir, backup_name)

            shutil.copy(log_file, backup_path)

            archive_name = os.path.join(backup_dir, f"backup_{timestamp}.zip")
            with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, backup_name)

            os.remove(backup_path)
            print(f"Backup created and compressed: {archive_name}")

            # Read using Windows default encoding (cp1252), ignoring errors
            with open(log_file, "r", encoding="cp1252", errors="ignore") as f:
                content = f.read()

            # Overwrite the same file in UTF-8
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Converted {log_file} to UTF-8 in place.")
    except Exception as e:
        log_error(f"Failed to convert {log_file}: {e}")

def update_run_summary(max_entries=100):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"Run at {timestamp}\n"

        if os.path.exists(summary_file):
            with open(summary_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        else:
            lines = []

        lines = lines[-(max_entries - 1):] + [entry]

        with open(summary_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"Updated run summary: {entry.strip()}")
    except Exception as e:
        log_error(f"Failed to update run summary: {e}")

def restore_backup(backup_file):
    try:
        if os.path.exists(backup_file):
            with zipfile.ZipFile(backup_file, "r") as zipf:
                zipf.extractall(backup_dir)
            print(f"Extracted backups from {backup_file} into {backup_dir}")
        else:
            print(f"No backup archive found at {backup_file}.")
    except Exception as e:
        log_error(f"Failed to restore backup {backup_file}: {e}")

def list_backups():
    try:
        backups = [f for f in os.listdir(backup_dir) if f.startswith("backup_") and f.endswith(".zip")]
        if backups:
            print("Available backup archives:")
            for b in sorted(backups):
                print(f" - {os.path.join(backup_dir, b)}")
        else:
            print("No backup archives found.")
    except Exception as e:
        log_error(f"Failed to list backups: {e}")

def restore_latest():
    try:
        backups = [f for f in os.listdir(backup_dir) if f.startswith("backup_") and f.endswith(".zip")]
        if backups:
            latest = sorted(backups)[-1]
            latest_path = os.path.join(backup_dir, latest)
            with zipfile.ZipFile(latest_path, "r") as zipf:
                zipf.extractall(backup_dir)
            print(f"Restored logs from latest backup archive: {latest_path}")
        else:
            print("No backup archives found to restore.")
    except Exception as e:
        log_error(f"Failed to restore latest backup: {e}")

def delete_old_backups(days=retention_days):
    try:
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        deleted = []
        for f in os.listdir(backup_dir):
            if f.startswith("backup_") and f.endswith(".zip"):
                path = os.path.join(backup_dir, f)
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                if mtime < cutoff:
                    os.remove(path)
                    deleted.append(path)
        if deleted:
            print("Deleted old backup archives:")
            for d in deleted:
                print(f" - {d}")
        else:
            print("No old backup archives found to delete.")
    except Exception as e:
        log_error(f"Failed to delete old backups: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "restore":
            if len(sys.argv) > 2:
                restore_backup(sys.argv[2])
            else:
                print("Please provide the backup archive path to restore.")
        elif sys.argv[1] == "list-backups":
            list_backups()
        elif sys.argv[1] == "auto-restore-latest":
            restore_latest()
        elif sys.argv[1] == "delete-old-backups":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else retention_days
            delete_old_backups(days)
        else:
            print("Unknown option. Use 'restore <archive>', 'list-backups', 'auto-restore-latest', or 'delete-old-backups [days]'.")
    else:
        # Process all .txt logs in reports/
        for file in os.listdir(reports_dir):
            if file.endswith(".txt") and file not in ["run_summary.txt", "error_log.txt", "health_status.txt"]:
                log_path = os.path.join(reports_dir, file)
                append_test_entry(log_path)
                convert_to_utf8(log_path)

        update_run_summary()
