# DroidBridge

Migrate storage from an old Android phone or local backup to a new Android phone — without overwriting files or creating duplicates.

## What it does

- **Source**: Old Android device (ADB) or a local folder (e.g. `/sdcard` backup)
- **Destination**: New Android device connected via ADB
- **Duplicate detection**: Skips files that already exist (size + partial hash)
- **Conflict handling**: Renames conflicting files instead of overwriting (`filename (migrated).ext`)
- **Transfer**: Uses tar archives for faster bulk transfer instead of pushing files one by one

## Requirements

- Python 3.11+
- [ADB](https://developer.android.com/tools/adb) in your PATH
- USB debugging enabled on both devices

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

1. Connect both devices via USB
2. Choose source (device or local folder) and destination device
3. Click **Analyze Storage** to scan and build a migration plan
4. Review the summary, then click **Start Migration**

## Output

- `migration_plan.json` — plan before execution
- `migration_report.json` — report after completion
- `logs/app.log` — application log

## Platform

Windows, Linux, macOS.
