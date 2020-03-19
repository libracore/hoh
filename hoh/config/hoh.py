from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("CRM"),
            "icon": "fa fa-money",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Customer",
                       "label": _("Customer"),
                       "description": _("Customer")
                   }
            ]
        },
        {
            "label": _("Artikelstamm"),
            "icon": "octicon octicon-file-submodule",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Skizze",
                       "label": _("Skizze"),
                       "description": _("Skizze")
                   },
                   {
                       "type": "doctype",
                       "name": "Dessin",
                       "label": _("Dessin"),
                       "description": _("Dessin")
                   },
                   {
                       "type": "doctype",
                       "name": "Bemusterung",
                       "label": _("Bemusterung"),
                       "description": _("Bemusterung")
                   },
                   {
                       "type": "doctype",
                       "name": "Musterkarte",
                       "label": _("Musterkarte"),
                       "description": _("Musterkarte")
                   },
                   {
                       "type": "doctype",
                       "name": "Item",
                       "label": _("Item"),
                       "description": _("Item")
                   },
                   {
                       "type": "doctype",
                       "name": "BOM",
                       "label": _("BOM"),
                       "description": _("BOM")
                   }
            ]
        },
        {
            "label": _("Vertrieb"),
            "icon": "fa fa-money",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Sales Order",
                       "label": _("Sales Order"),
                       "description": _("Sales Order")
                   },
                   {
                       "type": "doctype",
                       "name": "Delivery Note",
                       "label": _("Delivery Note"),
                       "description": _("delivery Note")
                   },
                   {
                       "type": "doctype",
                       "name": "Sales Invoice",
                       "label": _("Sales Invoice"),
                       "description": _("Sales Invoice")
                   }
            ]
        },
        {
            "label": _("Einkauf"),
            "icon": "fa fa-money",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Purchase Order",
                       "label": _("Purchase Order"),
                       "description": _("Purchase Order")
                   },
                   {
                       "type": "doctype",
                       "name": "Purchase Receipt",
                       "label": _("Purchase Receipt"),
                       "description": _("Purchase Receipt")
                   },
                   {
                       "type": "doctype",
                       "name": "Purchase Invoice",
                       "label": _("Purchase Invoice"),
                       "description": _("Purchase Invoice")
                   }
            ]
        },
        {
            "label": _("Finanzbuchhaltung"),
            "icon": "octicon octicon-repo",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Kassa",
                       "label": _("Kassa"),
                       "description": _("Kassa")
                   },
                   {
                       "type": "doctype",
                       "name": "Buchhaltungsperiode",
                       "label": _("Buchhaltungsperiode"),
                       "description": _("Buchhaltungsperiode")
                   },
                   {
                       "type": "doctype",
                       "name": "Payment Reminder",
                       "label": _("Payment Reminder"),
                       "description": _("Payment Reminder")
                   },
                   {
                       "type": "doctype",
                       "name": "Direct Debit Proposal",
                       "label": _("Direct Debit Proposal"),
                       "description": _("Direct Debit Proposal")
                   },
                   {
                       "type": "doctype",
                       "name": "Payment Proposal",
                       "label": _("Payment Proposal"),
                       "description": _("Payment Proposal")
                   },
                   {
                       "type": "page",
                       "name": "bank_wizard",
                       "label": _("Bank Wizard"),
                       "description": _("Bank Wizard")
                   }
            ]
        },
        {
            "label": _("Hilfstabellen"),
            "icon": "octicon octicon-list-ordered",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Dessinnummer",
                       "label": _("Dessinnummer"),
                       "description": _("Dessinnummer")
                   },
                   {
                       "type": "doctype",
                       "name": "Garnstaerke",
                       "label": _("Garnstaerke"),
                       "description": _("Garnstaerke")
                   },
                   {
                       "type": "doctype",
                       "name": "Farbe",
                       "label": _("Farbe"),
                       "description": _("Farbe")
                   },
                   {
                       "type": "doctype",
                       "name": "Bezeichnung",
                       "label": _("Bezeichnung"),
                       "description": _("Bezeichnung")
                   },
                   {
                       "type": "doctype",
                       "name": "Pflegesymbol",
                       "label": _("Pflegesymbol"),
                       "description": _("Pflegesymbol")
                   },
                   {
                       "type": "doctype",
                       "name": "Material",
                       "label": _("Material"),
                       "description": _("Material")
                   },
                   {
                       "type": "doctype",
                       "name": "Stickmaschine",
                       "label": _("Stickmaschine"),
                       "description": _("Stickmaschine")
                   },
                   {
                       "type": "doctype",
                       "name": "Paillettenart",
                       "label": _("Paillettenart"),
                       "description": _("Paillettenart")
                   },
                   {
                       "type": "doctype",
                       "name": "Rapport",
                       "label": _("Rapport"),
                       "description": _("Rapport")
                   }
            ]
        }
    ]
