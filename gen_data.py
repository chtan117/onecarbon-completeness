import json

# Master source list: id -> (name, scope)
MASTER = {
    1: ("Stationary combustion \u2014 natural gas", "Scope 1"),
    2: ("Stationary combustion \u2014 diesel (stationary)", "Scope 1"),
    3: ("Stationary combustion \u2014 LPG (stationary)", "Scope 1"),
    4: ("Stationary combustion \u2014 fuel oil / HFO", "Scope 1"),
    6: ("Backup / standby generators \u2014 diesel", "Scope 1"),
    7: ("Backup / standby generators \u2014 LPG / gas", "Scope 1"),
    8: ("Process combustion \u2014 kilns, furnaces, reactors", "Scope 1"),
    9: ("Mobile combustion \u2014 diesel fleet (road vehicles)", "Scope 1"),
    10: ("Mobile combustion \u2014 petrol fleet (road vehicles)", "Scope 1"),
    11: ("Mobile combustion \u2014 biofuel fleet", "Scope 1"),
    12: ("Mobile combustion \u2014 forklifts / MHE (diesel/LPG)", "Scope 1"),
    13: ("Mobile combustion \u2014 marine vessels (diesel)", "Scope 1"),
    14: ("Mobile combustion \u2014 marine vessels (biofuel)", "Scope 1"),
    15: ("Mobile combustion \u2014 construction equipment", "Scope 1"),
    16: ("Mobile combustion \u2014 aviation fuel", "Scope 1"),
    17: ("Fugitive \u2014 HVAC refrigerant leakage (stationary)", "Scope 1"),
    18: ("Fugitive \u2014 mobile A/C refrigerant leakage", "Scope 1"),
    19: ("Fugitive \u2014 refrigeration units (cold storage/process)", "Scope 1"),
    20: ("Fugitive \u2014 fire suppression systems", "Scope 1"),
    21: ("Fugitive \u2014 SF\u2086 from electrical switchgear", "Scope 1"),
    24: ("Fugitive \u2014 wastewater treatment (if operated)", "Scope 1"),
    26: ("Process \u2014 semiconductor manufacturing (PFC/N\u2082O/SF\u2086)", "Scope 1"),
    27: ("Process \u2014 solvent / coating use (VOCs)", "Scope 1"),
    28: ("Solar PV \u2014 on-site generation (owned)", "Scope 1"),
    29: ("Purchased electricity \u2014 grid connected", "Scope 2"),
    32: ("Purchased cooling (district cooling)", "Scope 2"),
    33: ("Purchased compressed air (third party)", "Scope 2"),
    34: ("Purchased goods \u2014 raw materials", "Scope 3"),
    35: ("Purchased goods \u2014 packaging", "Scope 3"),
    36: ("Purchased services (incl. HR, IT, professional)", "Scope 3"),
    37: ("Purchased water \u2014 municipal supply", "Scope 3"),
    38: ("Capital goods \u2014 vehicles and fleet", "Scope 3"),
    39: ("Capital goods \u2014 plant and equipment", "Scope 3"),
    40: ("Capital goods \u2014 IT and office equipment", "Scope 3"),
    41: ("Well-to-tank (WTT) \u2014 diesel / petrol", "Scope 3"),
    42: ("Well-to-tank (WTT) \u2014 natural gas", "Scope 3"),
    43: ("T&D losses on purchased electricity", "Scope 3"),
    44: ("Upstream transport \u2014 inbound freight (road)", "Scope 3"),
    45: ("Upstream transport \u2014 inbound freight (sea/air)", "Scope 3"),
    46: ("Waste generated in operations \u2014 general waste", "Scope 3"),
    47: ("Waste generated in operations \u2014 hazardous waste", "Scope 3"),
    48: ("Waste generated in operations \u2014 e-waste", "Scope 3"),
    49: ("Business travel \u2014 air travel", "Scope 3"),
    50: ("Business travel \u2014 ground transport (taxi/train)", "Scope 3"),
    51: ("Business travel \u2014 hotel accommodation", "Scope 3"),
    52: ("Employee commuting \u2014 private vehicle", "Scope 3"),
    53: ("Employee commuting \u2014 public transport", "Scope 3"),
    54: ("Work-from-home energy use", "Scope 3"),
    55: ("Upstream leased assets", "Scope 3"),
    56: ("Downstream transport \u2014 outbound freight (road)", "Scope 3"),
    57: ("Downstream transport \u2014 outbound freight (sea/air)", "Scope 3"),
    59: ("Use of sold products", "Scope 3"),
    60: ("End-of-life treatment of sold products", "Scope 3"),
    61: ("Downstream leased assets (operated by tenants)", "Scope 3"),
}

GROUP_BY_SCOPE = {
    "Scope 1": "Your operations",
    "Scope 2": "Your energy",
    "Scope 3": "Your value chain",
}

BASELINE = [29, 43, 17, 6, 9, 10, 18, 41, 37, 36, 40, 46, 48, 49, 50, 51, 52, 53, 54]

SECTOR_EXTRA = {
    "Manufacturing": [1, 2, 3, 4, 8, 12, 19, 20, 21, 24, 32, 33, 34, 35, 38, 39, 44, 45, 47, 56, 57, 59, 60],
    "Office-based": [34, 39, 55],
    "F&B": [1, 3, 7, 19, 20, 24, 34, 35, 44, 45, 56, 57, 60],
    "Logistics": [11, 12, 19, 38, 42, 44, 45, 56, 57, 61],
    "Construction": [2, 6, 7, 12, 15, 21, 34, 38, 39, 44, 45, 47, 56, 57, 61],
    "Semiconductor": [26, 27, 21, 19, 32, 33, 24, 34, 35, 39, 47, 48, 44, 45, 56, 57],
}

SECTOR_OPTIONAL = {
    "Office-based": [61],
    "Logistics": [13, 14, 16],
    "Semiconductor": [6, 28],
}

OUT_OF_SCOPE_NOTE = (
    "This quick check doesn't screen every possible source \u2014 categories like "
    "franchises, financed emissions, and processing of products you sell are left "
    "out here. A full assessment covers these too."
)

def build_sector(ids, optional_ids):
    seen = set()
    items = []
    for sid in BASELINE + ids:
        if sid in seen:
            continue
        seen.add(sid)
        name, scope = MASTER[sid]
        items.append({
            "id": sid, "name": name, "scope": scope,
            "group": GROUP_BY_SCOPE[scope], "optional": False,
        })
    for sid in optional_ids:
        if sid in seen:
            continue
        seen.add(sid)
        name, scope = MASTER[sid]
        items.append({
            "id": sid, "name": name, "scope": scope,
            "group": GROUP_BY_SCOPE[scope], "optional": True,
        })
    return items

sectors = {}
for sector, extra in SECTOR_EXTRA.items():
    sectors[sector] = build_sector(extra, SECTOR_OPTIONAL.get(sector, []))

js = "// Auto-generated from OneCarbon_Completeness_Tool_Sector_Spec_v1.md \u2014 do not hand-edit, regen from gen_data.py\n"
js += "const SECTORS = " + json.dumps(sectors, indent=2, ensure_ascii=False) + ";\n"
js += "const OUT_OF_SCOPE_NOTE = " + json.dumps(OUT_OF_SCOPE_NOTE, ensure_ascii=False) + ";\n"

with open("static/sources.js", "w") as f:
    f.write(js)

for s, items in sectors.items():
    print(s, len(items), "sources")
