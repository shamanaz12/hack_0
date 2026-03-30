# File Watcher for AI Employee Vault

This file watcher monitors the `Drop_Folder` and automatically copies any new files to the `Needs_Action` folder.

## How It Works

1. The script continuously monitors the `Drop_Folder` for new files
2. When a file is added to the `Drop_Folder`, it gets copied to the `Needs_Action` folder
3. The original file remains in the `Drop_Folder` (the script copies rather than moves)
4. Duplicate filenames are handled by appending a number to the filename

## Setup

1. Ensure you have Python installed on your system
2. Install the required dependency:
   ```
   pip install watchdog
   ```

## Running the Watcher

To start the file watcher, run:
```
python file_watcher.py
```

The watcher will run continuously until you stop it with `Ctrl+C`.

## Important Notes

- The watcher runs 24/7 once started until manually stopped
- It monitors only the top level of the Drop_Folder (non-recursive)
- Files are copied (not moved) to preserve originals in Drop_Folder
- The script handles duplicate filenames automatically
- All operations are logged with timestamps

## Troubleshooting

If you encounter permission errors, make sure:
- The script has read/write access to both folders
- No other processes are locking the files
- Both folder paths exist and are accessible