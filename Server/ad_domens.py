# ad_domains.py
import re
from typing import Set


def extract_domains(input_lines: list) -> Set[str]:
    """Извлекает домены из списка
     строк по правилам EasyList."""
    pattern = re.compile(r"^([^#|/$@:\s]+)")
    domains = set()

    for line in input_lines:
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        match = pattern.match(line)
        if match:
            domains.add(match.group(1).lower())

    return domains


def save_domains(domains: Set[str],
                 output_file: str) -> int:
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for domain in sorted(domains):
                f.write(f"{domain}\n")
        return len(domains)
    except IOError as e:
        raise RuntimeError(f"Ошибка записи файла: {e}")


def process_adblock_list(input_file: str,
                         output_file: str) -> None:
    """Основная функция обработки файла."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        domains = extract_domains(lines)
        count = save_domains(domains, output_file)
        print(f"Сохранено"
              f" {count} доменов в"
              f" {output_file}")

    except FileNotFoundError:
        raise RuntimeError("Входной файл не найден")
    except UnicodeDecodeError:
        raise RuntimeError("Ошибка декодирования файла")


if __name__ == "__main__":
    process_adblock_list("../easylist.txt",
                         "ad_hosts.txt")
