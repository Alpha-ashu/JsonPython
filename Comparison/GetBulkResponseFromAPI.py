import os
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define source and destination directories
SOURCE_DIR = os.path.join(os.path.dirname(__file__), "sampleResponseFiles")
DEST_DIR = os.path.join(os.path.dirname(__file__), "target", "jsonResponse","bulkResponse")

def copy_sample_response_files():
    """ Copies all files from sampleResponseFiles to target/jsonResponse """

    # Ensure destination directory exists
    os.makedirs(DEST_DIR, exist_ok=True)

    # Iterate over files in the source directory
    for file_name in os.listdir(SOURCE_DIR):
        source_path = os.path.join(SOURCE_DIR, file_name)
        dest_path = os.path.join(DEST_DIR, file_name)

        # Check if it's a file before copying
        if os.path.isfile(source_path):
            shutil.copy2(source_path, dest_path)  # Copy with metadata
            logger.info(f"Copied: {file_name} -> {dest_path}")

if __name__ == "__main__":
    copy_sample_response_files()
    logger.info("File copying completed successfully.")
