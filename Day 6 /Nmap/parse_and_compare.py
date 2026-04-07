import json
import yaml
import xmltodict

# ── Load JSON ──────────────────────────────────────────
with open('./raw_ping_reports/scan_results.json', 'r') as f:
    dict_json = json.load(f)

print("[+] Loaded JSON:")
print(f"    {dict_json}\n")

# ── Load YAML ──────────────────────────────────────────
with open('./raw_ping_reports/scan_results.yaml', 'r') as f:
    dict_yaml = yaml.safe_load(f)

print("[+] Loaded YAML:")
print(f"    {dict_yaml}\n")

# ── Load XML ───────────────────────────────────────────
with open('./raw_ping_reports/scan_results.xml', 'r') as f:
    raw_xml = f.read()

parsed_xml = xmltodict.parse(raw_xml)
dict_xml = dict(parsed_xml['scan_result'])

# Fix: xmltodict returns a single host as string, not list
if isinstance(dict_xml.get('live_hosts'), str):
    dict_xml['live_hosts'] = [dict_xml['live_hosts']]
elif dict_xml.get('live_hosts') is None:
    dict_xml['live_hosts'] = []

print("[+] Loaded XML:")
print(f"    {dict_xml}\n")

# ── Compare All 3 Dictionaries ─────────────────────────
print("=" * 45)
print("         COMPARISON RESULTS")
print("=" * 45)

json_vs_yaml = dict_json == dict_yaml
json_vs_xml  = dict_json == dict_xml
yaml_vs_xml  = dict_yaml == dict_xml

print(f"  JSON == YAML : {' Match' if json_vs_yaml else ' Mismatch'}")
print(f"  JSON == XML  : {'Match' if json_vs_xml  else ' Mismatch'}")
print(f"  YAML == XML  : {' Match' if yaml_vs_xml  else ' Mismatch'}")
print("=" * 45)

if json_vs_yaml and json_vs_xml and yaml_vs_xml:
    print("\n All 3 files contain identical data.")
else:
    print("\n Differences found — but this may be due to XML type handling.")
    print("    XML stores lists differently when there is only 1 host.")