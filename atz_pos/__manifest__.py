# -*- coding: utf-8 -*-
{
    "name": "Atzeneta - POS",
    "version": "12.0.0.5",
    "author": "Praxya",
    "license": "AGPL-3",
    "category": 'Account',
    "summary": 'Añade funcionalidad Fito al POS',
    'website': 'www.praxya.es',
    'depends': [
        'account',
        'point_of_sale',
        'res_partner_clientes',
        'product_template_fields',
        'account_payment_partner',
    ],
    'data': [
		'data/account_journal.xml',
		'data/account_payment_mode.xml',
        'views/account_invoice.xml',
        'views/assets.xml',
        'views/account_journal_view.xml',
    ],
    'installable': True,
    'qweb': ['static/src/xml/pos.xml'],
}
