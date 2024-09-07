import os
import json

phrases = {}
with open(f'{os.path.dirname(__file__)}/phrases.json', 'r', encoding="utf-8") as file:
    phrases = json.load(file)
