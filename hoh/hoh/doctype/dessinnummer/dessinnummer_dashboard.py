from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'dessinnummer',
		'transactions': [
			{
				'label': _('Dessins'),
				'items': ['Dessin', 'Item']
			}
		]
	}
