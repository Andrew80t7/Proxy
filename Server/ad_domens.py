import re

input_path= 'easylist.txt'
output_path = 'ad_hosts.txt'

domains = set()
pattern = re.compile(r'^([^#\|/$@:\s]+)')

with open(input_path, 'r', encoding='utf-8') as fin:
    for line in fin:
        line = line.strip()
        if not line or line.startswith('!'):
            continue
        m = pattern.match(line)
        if m:
            domains.add(m.group(1).lower())

with open(output_path, 'w', encoding='utf-8') as fout:
    for host in sorted(domains):
        fout.write(host + '\n')

print(f'Сохранено {len(domains)} доменов в {output_path}')
