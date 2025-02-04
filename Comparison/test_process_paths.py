import unittest
from Process_ONE import main  # Import your function
import os

# Get the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class TestProcessPaths(unittest.TestCase):

    def test_singleResponse(self):
        mapping_file_path = os.path.join(BASE_DIR, "config", "mapping.xlsx")
        legacy_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","bulkResponse", "legacyResponse1.json")
        payer_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","singleResponse", "Payer_02100144.json")
        result = main(mapping_file_path, legacy_file_path, payer_file_path)


    def test_singleResponse2(self):
        mapping_file_path = os.path.join(BASE_DIR, "config", "mapping.xlsx")
        legacy_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","bulkResponse", "legacyResponse1.json")
        payer_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","singleResponse", "Payer_02100143.json")

        result = main(mapping_file_path, legacy_file_path, payer_file_path)


    def test_bulkResponse(self):
        mapping_file_path = os.path.join(BASE_DIR, "config", "mapping.xlsx")
        legacy_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","bulkResponse", "legacyResponse1.json")
        payer_file_path = os.path.join(BASE_DIR, "target", "jsonResponse","bulkResponse", "payerResponse2.json")

        result = main(mapping_file_path, legacy_file_path, payer_file_path)



if __name__ == "__main__":
    unittest.main()