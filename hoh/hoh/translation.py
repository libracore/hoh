# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

import frappe

def part_translation(s, language):
    # fetch all translations
    translations = frappe.get_all("Color Translation", filters={'language': language}, fields=['original', 'translated'])
    # replace all parts
    for t in translations:
        s = s.replace(t['original'], t['translated'])
    return s
