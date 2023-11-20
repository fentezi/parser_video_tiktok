import asyncio
import unittest
from unittest.mock import patch, Mock
from main import kill_all_chrome_processes
import psutil


class TestKillAllChromeProcesses(unittest.TestCase):
    @patch('psutil.process_iter')
    @patch('psutil.pid_exists')
    def test_kill_all_chrome_processes_no_permission(self, mock_pid_exists, mock_process_iter):
        # Set up mocks
        mock_process = Mock()
        mock_process.name.return_value = 'chrome.exe'
        mock_process.pid = 123
        mock_process_iter.return_value = [mock_process]
        mock_pid_exists.side_effect = psutil.AccessDenied("No permission")

        # Test the function
        asyncio.run(kill_all_chrome_processes())

        # Assertions
        mock_process_iter.assert_called_once_with(['pid', 'name'])
        mock_pid_exists.assert_called_once_with(mock_process.pid)

    # Add more test cases as needed


if __name__ == '__main__':
    unittest.main()
