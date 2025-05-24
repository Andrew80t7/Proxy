import unittest
import tempfile
from pathlib import Path
from Server.ad_domens import extract_domains, save_domains, process_adblock_list


class TestAdDomains(unittest.TestCase):
    def test_extract_domains(self):
        test_data = [
            "example.com",
            "! comment line",
            "   ",
            "ads.example.net/banner.jpg",
            "##.ad-container",
            "sub.domain.org/path?query",
            "/notadomain"
        ]

        result = extract_domains(test_data)
        expected = {"example.com",
                    "ads.example.net",
                    "sub.domain.org"}
        self.assertEqual(result, expected)

    def test_save_domains(self):
        test_domains = {"z.com", "a.com", "b.com"}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.txt"
            count = save_domains(test_domains, str(output_path))

            self.assertEqual(count, 3)
            self.assertTrue(output_path.exists())

            content = output_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(content, ["a.com",
                                       "b.com",
                                       "z.com"])

    def test_process_adblock_list(self):
        test_input = [
            "example.com",
            "! comment",
            "ads.example.net##banner",
            "  ",
            "sub.domain.org/path"
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            # Создаем временный входной файл
            input_path = Path(tmpdir) / "input.txt"
            input_path.write_text("\n".join(test_input), encoding="utf-8")

            # Запускаем обработку
            output_path = Path(tmpdir) / "output.txt"
            process_adblock_list(str(input_path), str(output_path))

            # Проверяем результат
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(content), 3)

    def test_error_handling(self):
        # Проверка несуществующего файла
        with self.assertRaises(RuntimeError):
            process_adblock_list("non_existent.txt",
                                 "output.txt")

        # Проверка ошибки записи
        with self.assertRaises(RuntimeError), \
                tempfile.TemporaryDirectory() as tmpdir:
            invalid_path = Path(tmpdir) / "nonexistent_folder/output.txt"
            save_domains({"test.com"}, str(invalid_path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
