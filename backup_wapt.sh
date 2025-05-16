#!/bin/bash

# Define variables
SOURCE_DIR="$HOME/WSTT-Project"  # Change to your actual source directory
NAS_SHARE="/media/dev/projects/open-university/TM470 The Computing and IT Project/project-files/5. project-work/repo"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")  # Format: YYYYmmdddd-hhmmss
BACKUP_DIR="$NAS_SHARE/wapt_backup_$TIMESTAMP"

# Create the backup directory
mkdir -p "$BACKUP_DIR"

# Perform full backup using rsync
rsync -av --progress --exclude="env/" --exclude="__pycache__/" --exclude=".pytest_cache/" --exclude="backup_wapt.sh" --exclude=".git/" "$SOURCE_DIR/" "$BACKUP_DIR/"

# Confirmation message
echo "Backup completed successfully! Files saved to: $BACKUP_DIR"