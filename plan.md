# Smart Android Migration Tool

## Complete Implementation Specification (V2)

Author: Khaled Mohamed
Language: Python 3.11+
UI: PySide6
Platform: Windows / Linux / macOS

---

# 1. Project Overview

Smart Android Migration Tool is a **cross-platform desktop application** that safely migrates user storage from:

• an **old Android phone (ADB)**
• or a **local `/sdcard` folder**

to a **new Android phone connected via ADB**.

The system analyzes files, detects duplicates, resolves conflicts, and performs **fast archive-based transfers** while preserving file paths and metadata.

Goals:

• Never overwrite files
• Avoid duplicates
• Maintain folder structures
• Handle large storages (100k+ files)
• Provide clear migration preview
• Generate migration reports
• Allow migration resume if interrupted

---

# 2. Key Capabilities

### Supported Source Types

1️⃣ Android phone via ADB

```
adb shell access
```

2️⃣ Local folder representing `/sdcard`

```
/Users/khaled/backup/sdcard/
```

---

### Supported Destination

Android phone connected through ADB.

---

### Duplicate Detection

Fast method using:

```
size + partial hash
```

Partial hash algorithm:

```
hash(first 64KB + last 64KB)
```

Library:

```
xxhash
```

This allows scanning **100k+ files quickly**.

---

### Conflict Resolution

If file exists on destination:

Case A: same hash
→ skip

Case B: different hash
→ rename

Rename pattern:

```
filename (migrated).ext
```

Example:

```
IMG001.jpg
IMG001 (migrated).jpg
```

---

### Smart Media Organization

The tool reorganizes media where appropriate.

Examples:

```
WhatsApp Images → Pictures/WhatsApp
Telegram Images → Pictures/Telegram
Screenshots → Pictures/Screenshots
Camera Photos → DCIM/Camera
```

Path mapping engine ensures paths remain valid.

---

### Fast Transfer Mode

To avoid slow ADB operations:

Instead of:

```
adb push 10000 files
```

We use:

```
tar archive → adb push → extract
```

Benefits:

• drastically faster
• fewer ADB operations
• preserves folder structure

---

### Migration Preview

Before execution, UI shows:

```
Total files
Duplicate files skipped
Conflicts resolved
Total size
Estimated transfer time
```

User must confirm migration.

---

### Migration Resume

If migration stops due to:

• cable disconnect
• device reboot
• user interruption

The tool resumes using saved state:

```
migration_state.json
```

---

### Migration Report

After completion:

```
migration_report.json
```

Contains:

```
start_time
end_time
duration
files_scanned
files_migrated
duplicates_skipped
conflicts_resolved
errors
transfer_speed
```

---

# 3. Technology Stack

Language

```
Python 3.11+
```

UI

```
PySide6
```

Hashing

```
xxhash
```

Database

```
SQLite
```

ADB Interface

```
subprocess
```

Threading

```
QThread
```

Packaging

```
PyInstaller
```

Archive handling

```
tarfile
```

---

# 4. High-Level Architecture

```
UI Layer
   │
Controller Layer
   │
Migration Engine
   │
ADB Interface
   │
Android Device
```

Components:

```
UI
Controllers
Workers
Core Engines
Database
Utilities
```

---

# 5. Project Folder Structure

```
smart_migrate/

app.py

ui/
    main_window.py
    device_selector.py
    source_selector.py
    migration_preview.py
    progress_view.py
    log_view.py

controllers/
    migration_controller.py
    device_controller.py

core/
    adb_manager.py
    device_scanner.py
    file_indexer.py
    hash_engine.py
    duplicate_detector.py
    conflict_resolver.py
    migration_planner.py
    archive_builder.py
    transfer_engine.py
    extraction_engine.py
    report_generator.py
    resume_manager.py
    media_classifier.py
    path_mapper.py

workers/
    scan_worker.py
    hash_worker.py
    migration_worker.py

models/
    file_record.py
    migration_plan.py
    device_info.py

database/
    index_db.py

utils/
    file_utils.py
    logger.py
    constants.py
    adb_utils.py

logs/

assets/
    icons
    ui
```

---

# 6. UI Design

Main window layout.

```
-----------------------------------------------------
 Smart Android Migration Tool
-----------------------------------------------------

SOURCE

[ Old Device ▼ ]      [ Select Local Folder ]

DESTINATION

[ New Device ▼ ]

-----------------------------------------------------

[ Analyze Storage ]

-----------------------------------------------------

Migration Summary

Files Found
Duplicates
Conflicts
Total Size

-----------------------------------------------------

[ Start Migration ]

-----------------------------------------------------

Progress

[██████████--------]

Transfer Speed
Remaining Time
Current File

-----------------------------------------------------

Log Output
```

---

# 7. Device Detection

Run:

```
adb devices -l
```

Parse output.

Example:

```
R58M123ABC device usb:1-1 product:device model:Pixel_6
```

Displayed to user as:

```
Pixel 6 (R58M123ABC)
```

Information retrieved:

```
model
android_version
storage_size
available_space
```

---

# 8. File Indexing

### Local Folder

Use:

```
os.walk()
```

### ADB Device

Use:

```
adb shell find /sdcard -type f
```

Each file converted to:

```
FileRecord
```

---

### FileRecord Model

Attributes:

```
path
size
modified_time
partial_hash
mime_type
source
```

Example:

```
DCIM/Camera/IMG001.jpg
size: 3.2MB
hash: ab12cd34
```

---

# 9. Hash Engine

Algorithm:

```
xxhash
```

Procedure:

```
read first 64KB
read last 64KB
hash both
combine result
```

Benefits:

• very fast
• reliable for duplicate detection

---

# 10. Duplicate Detection

Two files are duplicates when:

```
size matches
partial hash matches
```

Duplicate files skipped automatically.

---

# 11. Conflict Resolution

Destination path checked via:

```
adb shell ls
```

Cases:

### Case 1

Same file exists

```
skip
```

---

### Case 2

Different file same name

Rename:

```
filename (migrated).ext
```

---

# 12. Migration Planning

The planner builds a migration plan.

Structure:

```
MigrationPlan
```

Fields:

```
files_to_transfer
duplicates
conflicts
total_size
estimated_time
```

Saved in:

```
migration_plan.json
```

---

# 13. Archive Builder

Creates archive containing files to migrate.

Implementation:

```
tarfile.open(mode="w")
```

Paths stored relative to `/sdcard`.

Example archive structure:

```
DCIM/Camera/IMG001.jpg
Pictures/WhatsApp/img02.jpg
```

Archive location:

```
temp/migration.tar
```

---

# 14. Transfer Engine

Process:

Step 1

```
adb push migration.tar /sdcard/.migration_temp/
```

Step 2

```
adb shell tar -xf /sdcard/.migration_temp/migration.tar
```

Step 3

cleanup

```
adb shell rm migration.tar
```

---

# 15. Extraction Safety

Prevent path traversal attacks.

Validate paths before extraction.

Rules:

```
no ".."
no absolute paths
must remain under /sdcard
```

---

# 16. Threading Model

Heavy tasks run in worker threads.

Workers:

```
ScanWorker
HashWorker
MigrationWorker
```

Signals sent to UI:

```
scan_progress
hash_progress
migration_progress
migration_complete
error_occurred
```

---

# 17. Resume Manager

Migration state stored in:

```
migration_state.json
```

Contains:

```
files_completed
files_remaining
archive_status
```

On restart:

```
resume from last file
```

---

# 18. Logging System

Logs stored in:

```
logs/app.log
```

Logged events:

```
scan started
scan finished
file hashed
file migrated
duplicate skipped
conflict resolved
error
```

---

# 19. Error Handling

Handle:

```
ADB disconnect
device storage full
transfer failure
permission errors
archive corruption
```

Retries implemented.

---

# 20. Packaging

Using PyInstaller.

Build command:

```
pyinstaller app.py --onefile --windowed
```

Include:

```
adb binaries
icons
assets
```

---

# 21. Cross Platform Support

Supported OS:

```
Windows
Linux
macOS
```

ADB automatically bundled.

---