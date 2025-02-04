import argparse
import json
import os
import pandas as pd
from openpyxl import load_workbook
import re  # Import regex for prefix removal

class Status:
    def __init__(self):
        self.StatusCode = ""
        self.Length = 0
        self.Payer = None

# Get the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_mapping(file_path):
    mapping = {}
    df = pd.read_excel(file_path, header=None)
    for index, row in df.iterrows():
        if index == 0:
            continue  # Skip header row
        if pd.isna(row[0]) or pd.isna(row[1]):
            print(f"Skipping row {index} due to missing cells")
            continue
        mapping[row[0]] = row[1]
    print("Mapping File Data:", mapping)
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

            # ✅ Return first value if list has elements, else return None
            return values[0] if values else None
        else:
            return None

    return find_node_value(json_node.get(key, {}), keys, level + 1)



def normalize_value(value):
    """Removes non-numeric characters from a string."""
    if isinstance(value, list) and value:
        value = value[0]  # Take the first element if it's a list
    if isinstance(value, str):
        return re.sub(r'[^0-9]', '', value)  # Remove non-numeric characters
    return value

def compare_using_mapping(response1_doc, response2_doc, mapping):
    status = Status()
    matched_count = 0
    total_keys = len(mapping)
    payer_value = None

    for old_key, new_key in mapping.items():
        old_value = find_node_value(response1_doc, old_key.split("/"),0)
        new_value = find_node_value(response2_doc, new_key.split("/"),0)

        old_value = normalize_value(old_value)
        new_value = normalize_value(new_value)

        if old_value == new_value:
            matched_count += 1
            if new_key == "claimIdentifiers/payerClaimControlNumber":
                payer_value = old_value or new_value
                print(f"Comparing {old_key}: {old_value} with {new_key}: {new_value}")

    status.Length = total_keys
    status.StatusCode = "MATCHED" if matched_count == total_keys else f"PARTIAL_MATCH"
    status.Payer = payer_value
    return status


def create_json_file(payer_id, file_name, json_content):
    base_directory = os.path.join(BASE_DIR, "target", "filteredRecord")
    payer_directory = os.path.join(base_directory, payer_id)
    os.makedirs(payer_directory, exist_ok=True)
    output_path = os.path.join(payer_directory, file_name)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_content, f, indent=4)
    print(f"File created: {output_path}")

def main(mapping_file_path, legacy_file_path, payer_file_path):


    mapping = read_mapping(mapping_file_path)

    with open(legacy_file_path, "r", encoding="utf-8") as f:
        legacy_response = json.load(f)
    with open(payer_file_path, "r", encoding="utf-8") as f:
        payer_response = json.load(f)

    legacy_response_array = legacy_response.get("searchResult", {}).get("searchOutput", {}).get("claims", [])
    payer_response_array = payer_response.get("data", [])

    if not isinstance(legacy_response_array, list) or not isinstance(payer_response_array, list):
        print("Expected both responses to contain arrays")
        return

    for legacy_record in legacy_response_array:
        for payer_record in payer_response_array:
            status = compare_using_mapping(legacy_record, payer_record, mapping)
            if status.StatusCode == "MATCHED":
                print("Match Found! Payer ID:", status.Payer)

                final_response1 = {"searchResult": {"searchOutput": {"claims": [legacy_record]}}}
                final_response2 = {"data": [payer_record]}

                payer_id = status.Payer or "UnknownPayer"
                create_json_file(payer_id, f"Legacy_{payer_id}.json", final_response1)
                create_json_file(payer_id, f"Payer_{payer_id}.json", final_response2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON data and compare using mapping")
    parser.add_argument("mapping_file", help="Path to mapping.xlsx file")
    parser.add_argument("legacy_file", help="Path to legacy response JSON file")
    parser.add_argument("payer_file", help="Path to payer response JSON file")

    args = parser.parse_args()

    main(args.mapping_file, args.legacy_file, args.payer_file)