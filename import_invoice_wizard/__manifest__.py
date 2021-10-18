# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
{
    'name': "Atzeneta - Importar Facturas",

    'summary': """ 
        Añade un wizard para importar facturas desde un csv
        """,

    'description': """   
    """,

    'author': "Praxya",
    'website': "http://www.praxya.com",

    'category': 'Invoice',
    'version': '0.7',

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
        'wizards/wizard_import_invoice.xml',
        'views/account_invoice.xml',
        'views/invoice_import_error_view.xml',
        'data/account_analytic_account.xml',
        'data/account_account.xml',
        'data/product_product.xml',
        'data/account_journal.xml',
        'data/account_payment_mode.xml',
        'data/res_partner.xml',
    ],
}
