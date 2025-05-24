import os
import re
import tempfile
import unittest
from pathlib import Path


def extract_domains(input_text: str):
    """
    Возвращает set доменов,  из easylist.
    """
    domains = set()
    pattern = re.compile(r"^([^#|/$@:\s]+)")
    for line in input_text.splitlines():
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        m = pattern.match(line)
        if m:
            domains.add(m.group(1).lower())
    return domains


class TestAdHostsExtractor(unittest.TestCase):
    def test_empty_and_comments(self):
        data = "\n! comment line\n   \n"
        self.assertEqual(extract_domains(data), set())

    def test_simple_rules(self):
        data = """
            example.com
            # это комментарий
            ads.example.net/banner.jpg
            sub.domain.org/path?query
            /notadomain
        """
        doms = extract_domains(data)
        self.assertIn("example.com", doms)
        self.assertIn("ads.example.net", doms)
        self.assertIn("sub.domain.org", doms)
        self.assertNotIn("notadomain", doms)  # невалидный

    def test_integration_writing_file(self):
        # создаём временный входной файл
        sample = "foo.com\nbar.org/baz\n! skip\n"
        with tempfile.TemporaryDirectory() as tmp:
            in_path = os.path.join(tmp, "easylist.txt")
            out_path = os.path.join(tmp, "ad_hosts.txt")
            with open(in_path, "w", encoding="utf-8") as f:
                f.write(sample)
            # запускаем вашу логику по записи
            domains = extract_domains(sample)
            with open(out_path, "w", encoding="utf-8") as fout:
                for host in sorted(domains):
                    fout.write(host + "\n")
            # проверяем
            content = Path(out_path).read_text(encoding="utf-8").splitlines()
            self.assertEqual(sorted(domains), content)


if __name__ == "__main__":
    unittest.main()
