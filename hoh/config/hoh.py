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
                       "name": "Kalkulation",
                       "label": _("Kalkulation"),
                       "description": _("Kalkulation")
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
                       "name": "Online Catalogue Request",
                       "label": _("Online Catalogue Request"),
                       "description": _("Online Catalogue Request")
                   },
                   {
                       "type": "doctype",
                       "name": "Angebot",
                       "label": _("Angebot"),
                       "description": _("Angebot")
                   },
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
            "label": _("Fertigung"),
            "icon": "fa fa-money",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Work Order",
                       "label": _("Work Order"),
                       "description": _("Work Order")
                   },
                   {
                       "type": "doctype",
                       "name": "Stock Entry",
                       "label": _("Stock Entry"),
                       "description": _("Stock Entry")
                   },
                   {
                       "type": "report",
                       "doctype": "Work Order",
                       "name": "Stickplan",
                       "label": _("Stickplan"),
                       "description": _("Stickplan"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Work Order",
                       "name": "Ausruestplan",
                       "label": _("Ausruestplan"),
                       "description": _("Ausruestplan"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Work Order",
                       "name": "Fertignote",
                       "label": _("Fertignote"),
                       "description": _("Fertignote"),
                       "is_query_report": True
                   }
            ]
        },
        {
            "label": _("Einkauf"),
            "icon": "fa fa-money",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Supplier",
                       "label": _("Supplier"),
                       "description": _("Supplier")
                   },
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
                   },
                   {
                       "type": "report",
                       "doctype": "Item",
                       "name": "Bestellbestand",
                       "label": _("Bestellbestand"),
                       "description": _("Bestellbestand"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Work Order",
                       "name": "Stoffbedarf",
                       "label": _("Stoffbedarf"),
                       "description": _("Stoffbedarf"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Work Order",
                       "name": "Halbfabrikatbedarf",
                       "label": _("Halbfabrikatbedarf"),
                       "description": _("Halbfabrikatbedarf"),
                       "is_query_report": True
                   }
            ]
        },
        {
            "label": _("Finanzbuchhaltung"),
            "icon": "octicon octicon-repo",
            "items": [
                   {
                       "type": "page",
                       "name": "bank_wizard",
                       "label": _("Bank Wizard"),
                       "description": _("Bank Wizard")
                   },
                   {
                       "type": "doctype",
                       "name": "Payment Proposal",
                       "label": _("Payment Proposal"),
                       "description": _("Payment Proposal")
                   },
                   {
                       "type": "doctype",
                       "name": "Payment Reminder",
                       "label": _("Payment Reminder"),
                       "description": _("Payment Reminder")
                   },
                   {
                       "type": "report",
                       "name": "General Ledger",
                       "doctype": "GL Entry",
                       "is_query_report": True,
                   },
                   {
                       "type": "doctype",
                       "name": "AT VAT Declaration",
                       "label": _("AT VAT Declaration"),
                       "description": _("AT VAT Declaration")
                   },
                   {
                       "type": "report",
                       "name": "Kontrolle MwSt AT",
                       "label": _("Kontrolle MwSt AT"),
                       "doctype": "Sales Invoice",
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Invoice",
                       "name": "Summary Message",
                       "label": _("Summary Message"),
                       "description": _("Summary Message"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Purchase Invoice",
                       "name": "Intrastat",
                       "label": _("Intrastat"),
                       "description": _("Intrastat"),
                       "is_query_report": True
                   }
            ]
        },
        {
            "label": _("Hilfstabellen"),
            "icon": "octicon octicon-list-ordered",
            "items": [
                   {
                       "type": "doctype",
                       "name": "HOH Settings",
                       "label": _("HOH Settings"),
                       "description": _("HOH Settings")
                   },
                   {
                       "type": "doctype",
                       "name": "Dessinnummer",
                       "label": _("Dessinnummer"),
                       "description": _("Dessinnummer")
                   },
                   {
                       "type": "doctype",
                       "name": "Kollektion",
                       "label": _("Kollektion"),
                       "description": _("Kollektion")
                   },
                   {
                       "type": "doctype",
                       "name": "Produktkategorie",
                       "label": _("Produktkategorie"),
                       "description": _("Produktkategorie")
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
                       "name": "Finish Step",
                       "label": _("Finish Step"),
                       "description": _("Finish Step")
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
                   },
                   {
                       "type": "doctype",
                       "name": "Lieferkondition",
                       "label": _("Lieferkondition"),
                       "description": _("Lieferkondition")
                   },
                   {
                       "type": "doctype",
                       "name": "Lieferart",
                       "label": _("Lieferart"),
                       "description": _("Lieferart")
                   }
            ]
        },
        {
            "label": _("Auswertungen"),
            "icon": "fa fa-chart",
            "items": [
                   {
                       "type": "report",
                       "doctype": "Item",
                       "name": "Stock Age Valuation",
                       "label": _("Stock Age Valuation"),
                       "description": _("Stock Age Valuation"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Item",
                       "name": "Numeric Stock Summary",
                       "label": _("Numeric Stock Summary"),
                       "description": _("Numeric Stock Summary"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Item",
                       "name": "Statistik Warenbewegung",
                       "label": _("Statistik Warenbewegung"),
                       "description": _("Statistik Warenbewegung"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Item",
                       "name": "Detail Warenbewegung",
                       "label": _("Detail Warenbewegung"),
                       "description": _("Detail Warenbewegung"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Order",
                       "name": "Sales Analytics",
                       "label": _("Sales Analytics"),
                       "description": _("Sales Analytics"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Invoice",
                       "name": "Abrechnung Vertriebsmitarbeiter",
                       "label": _("Abrechnung Vertriebsmitarbeiter"),
                       "description": _("Abrechnung Vertriebsmitarbeiter"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Bin",
                       "name": "Stock by Sales Price",
                       "label": _("Stock by Sales Price"),
                       "description": _("Stock by Sales Price"),
                       "is_query_report": True
                   }
            ]
        }
    ]
