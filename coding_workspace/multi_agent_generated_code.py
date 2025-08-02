import json
import csv

def extract_from_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return 'File not found'
    except json.JSONDecodeError:
        return 'Invalid JSON format'
    except PermissionError:
        return 'Permission denied'

def extract_from_csv(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return list(reader)
    except FileNotFoundError:
        return 'File not found'
    except csv.Error:
        return 'Invalid CSV format'
    except PermissionError:
        return 'Permission denied'

def extract_from_txt(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'File not found'
    except PermissionError:
        return 'Permission denied'

# Extensible for future file types
