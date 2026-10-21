import unittest
from unittest.mock import patch

from config import validate_config


class ConfigValidationTests(unittest.TestCase):
    def test_missing_api_key_has_actionable_chinese_message(self):
        with patch("config.API_KEY", None):
            with self.assertRaises(ValueError) as error:
                validate_config()

        self.assertIn("未检测到阿里云百炼 API Key", str(error.exception))
        self.assertIn("DASHSCOPE_API_KEY", str(error.exception))

    def test_configured_api_key_passes_validation(self):
        with patch("config.API_KEY", "test-key"):
            validate_config()


if __name__ == "__main__":
    unittest.main()
