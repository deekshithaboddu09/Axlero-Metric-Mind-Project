import unittest

from semantic_request_boundary import validate_request


class TestSemanticRequestBoundary(unittest.TestCase):

    def test_valid_revenue_request(self):
        request = {
            "question": "Show total revenue by region",
            "measure": "total revenue",
            "dimensions": ["region"],
            "filters": [],
        }
        self.assertEqual(validate_request(request)["status"], "valid")

    def test_valid_margin_filter(self):
        request = {
            "question": "Show total margin for Europe",
            "measure": "total margin",
            "dimensions": [],
            "filters": [
                {
                    "dimension": "region",
                    "operator": "equals",
                    "value": "Europe",
                }
            ],
        }
        self.assertEqual(validate_request(request)["status"], "valid")

    def test_unknown_measure_rejected(self):
        request = {
            "question": "Show profit",
            "measure": "unknown profit",
            "dimensions": [],
            "filters": [],
        }
        self.assertEqual(validate_request(request)["status"], "error")

    def test_unknown_dimension_rejected(self):
        request = {
            "question": "Show revenue by city",
            "measure": "total revenue",
            "dimensions": ["city"],
            "filters": [],
        }
        self.assertEqual(validate_request(request)["status"], "error")

    def test_missing_question_rejected(self):
        request = {
            "measure": "total revenue",
            "dimensions": [],
            "filters": [],
        }
        self.assertEqual(validate_request(request)["status"], "error")

    def test_missing_measure_rejected(self):
        request = {
            "question": "Show revenue",
            "dimensions": [],
            "filters": [],
        }
        self.assertEqual(validate_request(request)["status"], "error")


if __name__ == "__main__":
    unittest.main()