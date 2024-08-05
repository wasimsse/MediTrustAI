import unittest
from src.fine_tune_model import fine_tune_model

class TestFineTuneModel(unittest.TestCase):

    def test_fine_tune(self):
        fine_tune_model("google/palm-2", "your_dataset_name", "test_output")
        # Add assertions to validate the fine-tuning process

if __name__ == "__main__":
    unittest.main()
