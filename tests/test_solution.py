import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

import requests

from desafio.email_gen import generate_base, generate_emails
from desafio.csv_writer import write_csv
from desafio.fetch_data import fetch_users


class EmailTests(unittest.TestCase):
    def test_names(self):
        cases = {
            "John Doe": "jdoe",
            "Mrs. Dennis Schulist": "dschulist",
            "  mR John Doe  ": "jdoe",
            "Dr. Mrs. Jane Doe": "jdoe",
            "Dra. María Pérez": "mperez",
            "Nicholas Runolfsdottir V": "nrunolfsdottir",
            "John Doe Jr.": "jdoe",
            "Anne O'Neill": "aoneill",
            "Madonna": "madonna",
            "Drake Smith": "dsmith",
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(generate_base(name), expected)

    def test_duplicates_after_normalization(self):
        users = [{"name": name} for name in
                 ["John Doe", "Dr. Johana Doe", "Mrs. Jane Doe"]]
        generate_emails(users, "@democompany.com")
        self.assertEqual([u["corporate_email"] for u in users], [
            "jdoe@democompany.com", "jdoe1@democompany.com", "jdoe2@democompany.com"])
        self.assertEqual(users[1]["name"], "Dr. Johana Doe")

    def test_invalid_names(self):
        users = [{"name": name} for name in [None, "", "   ", "Dr.", "123", 123]]
        generate_emails(users, "@democompany.com")
        self.assertTrue(all(u["corporate_email"] == "" for u in users))


class IOTests(unittest.TestCase):
    def test_csv_preserves_special_characters(self):
        row = ['María "M", Pérez', "123", "m@example.com", "Empresa", "Bogotá", "mperez@democompany.com"]
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / "users.csv"
            write_csv([row], filename)
            with filename.open(newline="", encoding="utf-8") as stream:
                contents = list(csv.reader(stream))
            self.assertEqual(len(contents[0]), 6)
            self.assertEqual(contents[1], row)

    def test_csv_failure_is_not_silenced(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                write_csv([], Path(directory) / "missing" / "users.csv")

    @patch("desafio.fetch_data.requests.get")
    def test_api_success(self, get):
        get.return_value = Mock()
        get.return_value.json.return_value = [{"name": "John Doe"}]
        self.assertEqual(fetch_users("https://example.com/users"), [{"name": "John Doe"}])
        get.assert_called_once_with("https://example.com/users", timeout=10)

    @patch("desafio.fetch_data.requests.get")
    def test_api_timeout(self, get):
        get.side_effect = requests.exceptions.Timeout()
        self.assertIsNone(fetch_users("https://example.com/users"))

    @patch("desafio.fetch_data.requests.get")
    def test_invalid_api_payloads(self, get):
        for payload in [{}, ["invalid"], [{"company": None}], [{"address": []}]]:
            with self.subTest(payload=payload):
                get.return_value.json.return_value = payload
                self.assertIsNone(fetch_users("https://example.com/users"))


if __name__ == "__main__":
    unittest.main()
