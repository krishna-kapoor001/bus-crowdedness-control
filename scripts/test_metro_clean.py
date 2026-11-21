import json
import re

METRO_REPLACEMENTS = {
    'Chhatarpur Metro Station': 'Chhatarpur Bus Stop',
    'Vishwa Vidyalaya Metro Station': 'Vishwa Vidyalaya Bus Stop',
    'Saket Metro Station': 'Saket Bus Stop',
    'Karol Bagh Metro Station': 'Karol Bagh Bus Stop',
    'Laxmi Nagar (Vikas Marg) / Laxmi Nagar Metro Station': 'Laxmi Nagar (Vikas Marg) Bus Stop',
    'Rajindera Place Metro Station': 'Rajendra Place Bus Stop',
    'Shadipur Dtc Colony Metro Station': 'Shadipur DTC Colony Bus Stop',
    'Saket A Block (Malviya Nagar Metro Station)': 'Saket A Block (Malviya Nagar Bus Stop)',
    'Karol Bagh Metro': 'Karol Bagh Bus Stand',
    'Saket Metro Sation / Said-Ul-Ajaib': 'Saket Said-Ul-Ajaib Bus Stop',
    'Jahangir Puri Metro Station': 'Jahangirpuri Bus Stop',
    'Rithala Metro Station': 'Rithala Bus Stop',
    'Shadi Pur Metro Station': 'Shadipur Bus Stop',
    'Dwarka More Metro Station': 'Dwarka Mor Bus Stand',
    'Lajpat Nagar Metro': 'Lajpat Nagar Bus Stand',
    'Chhatarpur Metro': 'Chhatarpur Bus Stand',
    'Punj Sons / Govind Puri Metro Station': 'Punj Sons / Govindpuri Bus Stop',
    'Andheria More / Chhatarpur Metro Station': 'Andheria Mor / Chhatarpur Bus Stop',
    'Jahangirpuri Metro Station Gt Road': 'Jahangirpuri GT Road Bus Stop',
    'Qutub Minar Metro Sation': 'Qutub Minar Bus Stop',
    'Metro Train Depot': 'Shastri Park Transit Depot',
    'Ip Depot Metro Station': 'IP Depot Bus Stand',
    'Shastri Park Metro Depot': 'Shastri Park Bus Depot'
}

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

for s in stops:
    old_name = s['name']
    if old_name in METRO_REPLACEMENTS:
        print(f"RENAME: '{old_name}' -> '{METRO_REPLACEMENTS[old_name]}'")
    elif 'metro' in old_name.lower():
        print(f"OTHER METRO: '{old_name}'")
