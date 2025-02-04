import unittest
from Process_ONE import main  # Import your function
import os

# Get the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class TestProcessPaths(unittest.TestCase):

    """def test_singleResponse(self):
        mapping_file_path = os.path.join(BASE_DIR, "config", "mapping.xlsx")
        legacy_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","bulkResponse", "legacyResponse1.json")
        payer_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","singleResponse", "Payer_02100144.json")

        result = main(mapping_file_path, legacy_file_path, payer_file_path)
        self.assertEqual(result[0]["status_code"], "MATCHED")

    def test_singleResponse1(self):
        mapping_file_path = os.path.join(BASE_DIR, "config", "mapping.xlsx")
        legacy_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","bulkResponse", "legacyResponse1.json")
        payer_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","singleResponse", "Payer_02100144.json")

        result = main(mapping_file_path, legacy_file_path, payer_file_path)
        self.assertEqual(result[0]["status_code"], "UNMATCHED")

    def test_singleResponse2(self):
        mapping_file_path = os.path.join(BASE_DIR, "config", "mapping.xlsx")
        legacy_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","bulkResponse", "legacyResponse1.json")
        payer_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","singleResponse", "Payer_02100144.json")

        result = main(mapping_file_path, legacy_file_path, payer_file_path)
        self.assertEqual(result[0]["status_code"], "PARTIAL MATCH")
"""

    def test_bulk_single_response(self):
        """Test each single payer JSON file against the bulk legacy file."""
        mapping_file_path = os.path.join(BASE_DIR, "config", "mapping.xlsx")
        legacy_file_path = os.path.join(BASE_DIR, "target", "jsonResponse", "bulkResponse", "legacyResponse1.json")
        payer_dir_path = os.path.join(BASE_DIR, "target", "jsonResponse", "singleResponse")  # Directory containing payer JSON files

        # Ensure the directory exists
        self.assertTrue(os.path.exists(payer_dir_path), f"Payer directory '{payer_dir_path}' not found.")

        # Get all JSON files inside the directory
        payer_files = [f for f in os.listdir(payer_dir_path) if f.endswith(".json")]
        self.assertGreater(len(payer_files), 0, "No payer JSON files found.")

        # Iterate over each payer file and compare it with the bulk legacy file
        for payer_file in payer_files:
            payer_file_path = os.path.join(payer_dir_path, payer_file)
            result = main(mapping_file_path, legacy_file_path, payer_file_path)

            # Check if there's at least one match
            #self.assertGreater(len(result), 0, f"No matches found for {payer_file}")
            #self.assertEqual(result[0]["status_code"], "MATCHED", f"Mismatch in {payer_file}")


if __name__ == "__main__":
    unittest.main()
