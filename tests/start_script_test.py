import io
import unittest
from unittest.mock import patch
import asyncio

from web import start_script
class TestStartScript(unittest.TestCase):
    @patch("builtins.input", side_effect=["1", "5"])
    def test_start_script(self, mock_input):
        self.assertIsNone(asyncio.run(start_script()))

    @patch("builtins.input", side_effect=["2", "1", "3", "10", "20"])
    @patch("web.get_video_process")
    def test_start_script_option_2(self, mock_get_video_process, mock_input):
        asyncio.run(start_script())
        mock_get_video_process.assert_called_with(10, 20, 1, 3)

    @patch('builtins.input', side_effect=['3'])
    @patch('builtins.print')
    def test_start_script_invalid_input(self, mock_stdout, mock_input):
        asyncio.run(start_script())
        mock_stdout.assert_called_with('Ошибка ввода!')


if __name__ == "__main__":
    unittest.main()
