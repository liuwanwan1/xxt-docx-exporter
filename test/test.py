import unittest


class RichConsoleTests(unittest.TestCase):
    def test_recorded_console_exports_printed_text(self):
        try:
            from rich.console import Console
        except ModuleNotFoundError:
            self.skipTest("rich is not installed")

        console = Console(record=True)
        console.print("Hello, World!")

        self.assertIn("Hello, World!", console.export_text())


if __name__ == "__main__":
    unittest.main()
