from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'dessin',
		'transactions': [
			{
				'label': _('Dessins'),
				'items': ['Dessin']
			}
		]
	}
