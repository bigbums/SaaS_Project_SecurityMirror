import os
import sys
import datetime
import json

# --- Load settings from JSON ---
settings_file = "settings.json"
if os.path.exists(settings_file):
    with open(settings_file, "r", encoding="utf-8") as f:
        settings = json.load(f)
else:
    settings = {}

# Paths
reports_dir = settings.get("reports_dir", "reports")
summary_file = os.path.join(reports_dir, "run_summary.txt")
status_file = os.path.join(reports_dir, "health_status.txt")
error_file = os.path.join(reports_dir, "error_log.txt")

# Configurable rotation size
error_log_max_entries = settings.get("error_log_max_entries", 200)


def write_status(message):
    """Write single check result into health_status.txt with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(status_file, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry.strip())


def check_errors(max_age_hours=24):
    """Check error_log.txt for recent errors."""
    results = []
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(hours=max_age_hours)

    if not os.path.exists(error_file):
        results.append("✅ No error_log.txt found. No errors recorded.")
    else:
        with open(error_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        recent_errors = []
        for line in lines:
            if line.startswith("["):
                try:
                    timestamp_str = line.split("]")[0].strip("[")
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if timestamp >= cutoff:
                        recent_errors.append(line.strip())
                except ValueError:
                    continue

        if recent_errors:
            results.append("⚠️ Recent errors detected in error_log.txt:")
            results.extend(recent_errors)
        else:
            results.append("✅ No errors detected in the last 24 hours.")

    return results


def rotate_error_log(max_entries=error_log_max_entries):
    """Keep only the last N entries in error_log.txt to prevent uncontrolled growth."""
    if not os.path.exists(error_file):
        return  # Nothing to rotate

    try:
        with open(error_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        rotated = lines[-max_entries:]

        with open(error_file, "w", encoding="utf-8") as f:
            f.writelines(rotated)

        print(f"Rotated error_log.txt to last {max_entries} entries.")
    except Exception as e:
        print(f"⚠️ Failed to rotate error_log.txt: {e}")


def check_last_run(max_age_hours=24):
    """Simple check: verify last run timestamp in run_summary.txt"""
    if not os.path.exists(summary_file):
        result = "❌ No run_summary.txt found. Task may not have run yet."
        write_status(result)
        return

    with open(summary_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    if not lines:
        result = "❌ run_summary.txt is empty. No runs recorded."
        write_status(result)
        return

    last_entry = lines[-1].strip()
    try:
        timestamp_str = last_entry.replace("Run at ", "")
        last_run = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        result = f"❌ Could not parse timestamp from last entry: {last_entry}"
        write_status(result)
        return

    now = datetime.datetime.now()
    age = now - last_run
    if age.total_seconds() > max_age_hours * 3600:
        result = f"⚠️ Last run was at {last_run}, more than {max_age_hours} hours ago. Task may have failed."
    else:
        result = f"✅ Task ran successfully at {last_run} (within {max_age_hours} hours)."

    write_status(result)


def check_log_freshness(max_age_hours=24):
    """Check if log files in reports/ are fresh (recently updated)."""
    issues = []
    if not os.path.exists(reports_dir):
        issues.append("❌ reports/ folder not found.")
        return issues

    now = datetime.datetime.now()
    for filename in os.listdir(reports_dir):
        filepath = os.path.join(reports_dir, filename)
        if os.path.isfile(filepath):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            age_hours = (now - mtime).total_seconds() / 3600
            if age_hours > max_age_hours:
                issues.append(f"⚠️ {filename} is {age_hours:.1f} hours old (stale).")

    return issues


def check_all_logs(max_age_hours=24):
    """Comprehensive check: verify all log files in reports/"""
    results = []

    write_status("Starting comprehensive log check...")

    # Check for recent errors
    error_results = check_errors(max_age_hours)
    results.extend(error_results)
    for err in error_results:
        write_status(err)

    # Rotate error_log.txt
    rotate_error_log(error_log_max_entries)

    # Check log freshness
    log_results = check_log_freshness(max_age_hours)
    results.extend(log_results)
    for log in log_results:
        write_status(log)

    # Final status
    if results:
        write_status("Comprehensive check completed with issues.")
    else:
        write_status("Comprehensive check completed successfully — no critical errors found.")

    return results


if __name__ == "__main__":
    # Default mode is comprehensive
    mode = "all"
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

    if mode == "simple":
        check_last_run()
    elif mode == "all":
        check_all_logs()
    else:
        print("Usage: python health_check.py [simple|all]")
