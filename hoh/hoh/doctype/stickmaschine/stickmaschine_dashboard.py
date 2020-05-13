from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'stickmaschine',
		'transactions': [
			{
				'label': _('Dessins'),
				'items': ['Dessin', 'Item']
			},
            {
				'label': _('Manufacturing'),
				'items': ['Work Order']
			}
		]
	}
