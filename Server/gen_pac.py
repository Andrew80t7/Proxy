
import os
import json

INPUT = 'ad_hosts.txt'
OUTPUT = 'adblock.pac'

# читаем список
domains = []
with open(INPUT, encoding='utf-8') as f:
    for line in f:
        host = line.strip()
        if host and not host.startswith('#'):
            domains.append(host)

# начинаем формировать PAC
lines = []
lines.append("function FindProxyForURL(url, host) {")
lines.append("    var adDomains = %s;" % json.dumps(domains, ensure_ascii=False, indent=4))
lines.append("")
lines.append("    for (var i = 0; i < adDomains.length; i++) {")
lines.append("        if (shExpMatch(host, adDomains[i]) || shExpMatch(host, '*.' + adDomains[i])) {")
lines.append('            return "PROXY 127.0.0.1:9";')
lines.append("        }")
lines.append("    }")
lines.append("")
lines.append('    return "PROXY 127.0.0.1:8080";')
lines.append("}")

# записываем файл
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print(f"PAC-файл с {len(domains)} доменами сгенерирован в {os.path.abspath(OUTPUT)}")
