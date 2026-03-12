"""Application constants."""

# Hash settings
HASH_CHUNK_SIZE = 64 * 1024  # 64KB
HASH_ALGORITHM = "xxhash"

# Paths
SDCARD_PATH = "/sdcard"
MIGRATION_TEMP_DIR = "/sdcard/.migration_temp"
MIGRATION_ARCHIVE_NAME = "migration.tar"

# Conflict resolution
MIGRATED_SUFFIX = " (migrated)"

# Media path mappings (source pattern -> destination under /sdcard)
MEDIA_PATH_MAPPINGS = {
    "WhatsApp/Media/WhatsApp Images": "Pictures/WhatsApp",
    "WhatsApp/Media/WhatsApp Animated Gifs": "Pictures/WhatsApp",
    "WhatsApp/Media/WhatsApp Video": "Movies/WhatsApp",
    "Telegram/Telegram Images": "Pictures/Telegram",
    "Telegram/Telegram Video": "Movies/Telegram",
    "Screenshots": "Pictures/Screenshots",
    "DCIM/Camera": "DCIM/Camera",
}

# State files
MIGRATION_STATE_FILE = "migration_state.json"
MIGRATION_PLAN_FILE = "migration_plan.json"
MIGRATION_REPORT_FILE = "migration_report.json"

# Logging
LOG_DIR = "logs"
LOG_FILE = "app.log"
