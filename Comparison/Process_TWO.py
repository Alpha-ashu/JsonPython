import os
import json
import logging
import pandas as pd
from openpyxl import Workbook

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
BASE_DIRECTORY = os.path.join(BASE_DIR, "target", "filteredRecord")
MAPPING_FILE_PATH = os.path.join(BASE_DIR, "config", "mapping.xlsx")
OUTPUT_EXCEL_PATH = os.path.join(BASE_DIR, "target", "output", "output.xlsx")
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, "target", "output", "output_matched.json")


def read_mapping(file_path):
    """ Reads an Excel file (Sheet Two) and returns a mapping dictionary {old_path: new_path} """
    mapping = {}
    try:
        df = pd.read_excel(file_path, sheet_name=1)  # Reads the second sheet (0-based index)
        for _, row in df.iterrows():
            if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):  # Ensure both columns have values
                mapping[row.iloc[0]] = row.iloc[1]
    except Exception as e:
        logger.error(f"Error reading mapping file: {e}")
    return mapping

def find_node_value(json_node, keys, level=0):
    if level >= len(keys):
        return json_node if isinstance(json_node, (str, int, float)) else None  # Ensure numbers are not lost

    key = keys[level]

    if key.endswith("[*]"):  # Handling wildcard arrays
        array_key = key[:-3]
        array_node = json_node.get(array_key, [])

        if isinstance(array_node, list) and array_node:
            values = [find_node_value(item, keys, level + 1) for item in array_node]
            values = [v for v in values if v is not None]  # Remove None values
            return values[0] if values else None
        else:
            return None

    return find_node_value(json_node.get(key, {}), keys, level + 1)

def process_paths(old_json, new_json, old_path, new_path):
    """ Retrieves values from JSON using mapped paths and compares them. """
    old_value = find_node_value(old_json, old_path.split("/"), 0)
    new_value = find_node_value(new_json, new_path.split("/"), 0)

    # Ensure values are not None or empty before comparison
    if not old_value or not new_value:
        match_status = "Not Matched (One or both values are empty/null)"
    elif old_value == new_value:
        match_status = "Matched"
    elif isinstance(old_value, str) and isinstance(new_value, str) and (
            old_value.lower() in new_value.lower() or new_value.lower() in old_value.lower()
    ):
        match_status = "Partial Match"
    else:
        match_status = "Not Matched"

    print(old_path, new_path, old_value, new_value, match_status)
    return old_path, new_path, old_value, new_value, match_status

def update_json_result(result_json, new_path, old_value, new_value):
    """ Updates a JSON object with comparison results. """
    keys = new_path.split("/")
    current_node = result_json

    for key in keys[:-1]:  # Traverse until last key
        current_node = current_node.setdefault(key, {})

    key = keys[-1]
    match_status = "Matched" if old_value == new_value else "Not Matched"
    if old_value and new_value and (old_value.lower() in new_value.lower() or new_value.lower() in old_value.lower()):
        match_status = "Partial Match"

    current_node[key] = {
        "OldValue": old_value if old_value else "null",
        "NewValue": new_value if new_value else "null",
        "Status": match_status
    }

def main():
    try:
        # Load the mapping file
        mapping = read_mapping(MAPPING_FILE_PATH)

        # Create an Excel workbook
        workbook = Workbook()
        consolidated_sheet = workbook.active
        consolidated_sheet.title = "Consolidated"
        consolidated_sheet.append(["Payer Control Claim Account Number", "Coverage Percentage", "Matched Values"])

        aggregated_json_results = {}

        # Process each subdirectory in the base directory
        if os.path.exists(BASE_DIRECTORY):
            for folder in os.listdir(BASE_DIRECTORY):
                folder_path = os.path.join(BASE_DIRECTORY, folder)
                if os.path.isdir(folder_path):
                    legacy_file = os.path.join(folder_path, f"Legacy_{folder}.json")
                    payer_file = os.path.join(folder_path, f"Payer_{folder}.json")

                    if os.path.exists(legacy_file) and os.path.exists(payer_file):
                        with open(legacy_file, "r", encoding="utf-8") as f:
                            legacy_json = json.load(f)
                        with open(payer_file, "r", encoding="utf-8") as f:
                            payer_json = json.load(f)

                        folder_result_json = {}

                        # Create a new sheet for this folder
                        sheet = workbook.create_sheet(title=folder[:30])  # Excel sheet names must be ≤ 31 chars
                        sheet.append(["Old Path", "New Path", "Old Value", "New Value", "Matched/Not Matched"])

                        matched_count = 0
                        total_keys = len(mapping)

                        # Compare JSON files based on mapping
                        for old_path, new_path in mapping.items():
                            result = process_paths(legacy_json, payer_json, old_path, new_path)
                            sheet.append(result)

                            if result[-1] in ["Matched"]:
                                matched_count += 1

                        # Store results in aggregated JSON
                        aggregated_json_results[folder] = folder_result_json

                        # Calculate coverage percentage
                        coverage_percentage = (matched_count / total_keys) * 100 if total_keys > 0 else 0
                        consolidated_sheet.append([folder, f"{coverage_percentage:.2f}%", f"{matched_count}/{total_keys}"])

                    else:
                        logger.warning(f"Skipping folder '{folder}' as required files are missing.")

        # Save output JSON file
        with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(aggregated_json_results, f, indent=4)

        # Save output Excel file
        workbook.save(OUTPUT_EXCEL_PATH)

        logger.info(f"Comparison complete. Output written to {OUTPUT_EXCEL_PATH} and {OUTPUT_JSON_PATH}")

    except Exception as e:
        logger.error(f"An error occurred during comparison: {e}")

if __name__ == "__main__":
    main()