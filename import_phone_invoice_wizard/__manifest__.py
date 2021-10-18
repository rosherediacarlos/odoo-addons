# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
{
    'name': "Atzeneta - Importar Facturas Telefonía",

    'summary': """ 
        Añade un wizard para importar facturas telefonía desde un csv
        """,

    'description': """   
    """,

    'author': "Praxya",
    'website': "http://www.praxya.com",

    'category': 'Invoice',
    'version': '0.2',

    'depends': [
        'account', #Odoo
        'sale', #Odoo
        'purchase', #Odoo
        'account_invoice_force_number', #OCA https://github.com/OCA/account-invoicing
        'web_notify' #OCA https://github.com/OCA/web
    ],

    # always loaded
    'data': [      
        'security/ir.model.access.csv',
		'data/phone_import_map_format_data.xml',
		'data/phone_import_map_data_330.xml',
		'data/phone_import_map_data_340.xml',
		'data/product_product.xml',
		'data/account_journal.xml',
        'wizards/wizard_import_phone_invoice.xml',
        'views/res_partner.xml',
		'views/phone_import_map_view.xml',
		'views/phone_import_map_format_view.xml',
        'views/res_partner_phone_view.xml',
        # 'data/account_payment_mode.xml',
        # 'data/res_partner.xml',
    ],
}
