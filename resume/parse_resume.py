from __future__ import annotations
import typing

import pprint
import json

if __name__ == '__main__':
    with open('resume_devinjcornell.json') as f:
        resume = json.load(f)
    c = resume["contact"]
    print(f"Contact\n\tName: {c['name']}\n\tEmail: {c['email']}\n\tPhone: {c['phone']}\n\nSections")

    for section in resume["sections"]:
        print(f"\t{section['name']} ({len(section['entries'])} entries)")
        #print()

