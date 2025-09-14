import json

with open('templates/push_templates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(data)