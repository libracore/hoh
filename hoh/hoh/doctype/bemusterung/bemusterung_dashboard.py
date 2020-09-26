from __future__ import unicode_literals
from frappe import _

def get_data():
    return {
        'fieldname': 'bemusterung',
        'transactions': [
            {
                'label': _('Kalkulation'),
                'items': ['Kalkulation']
            },
            {
                'label': _('Online Catalogue'),
                'items': ['Online Catalogue Like Trace']
            }
        ]
    }
