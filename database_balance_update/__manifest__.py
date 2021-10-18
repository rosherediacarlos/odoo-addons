# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Database Balance Update",
    'summary': """Este modulo añade unas acciones planificadas (ir.cron) 
        las cuales se ejecutan diariamente para actualizar los datos en las base de datos de la balanza.""",
    "version": "0.3",
    "author": "Praxya",
    "website": "http://www.praxya.com/",
    "license": "AGPL-3",
    "category": "Uncategorized",
    "depends": [
        'base',
        'stock',
        'sale',
        'account',
		'balanzas',
        'product_template_tpv',
		'point_of_sale',
    ],
    'external_dependencies': {
        'python': [
			"mysql",
			"paramiko",
			"scp"
		],
		# 'bin': ['mysql-client'],
    },
    "data": [
        "data/ir_cron.xml",
		"data/res_partner.xml",
		"data/product_pricelist.xml",
		"wizards/wizard_import_invoice.xml",
		"views/account_tax_views.xml",
		# "views/sale_order.xml",
		"views/pos_order_views.xml",
		"views/point_of_sale_balance_views.xml",
		"views/balanza_settings_views.xml"
    ],
    "installable": True,
}
