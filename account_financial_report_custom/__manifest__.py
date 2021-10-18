# -*- coding: utf-8 -*-
# (c) 2019 Carlos Ros <cros@praxya.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Financial Report Custom",
    "version": "11.0.1.0",
    "author": "Praxya",
    "website": "https://praxya.com",
    "license": "AGPL-3",
    "category": "Tools",
    'summary': """
       Este modulo personaliza la vista de los informes de contabilidad.
    """,
    "depends": [
        'account_financial_report',#OCA https://github.com/OCA/account-financial-reporting.git
        'account_analytic_parent' #OCA https://www.github.com/OCA/account-analytic.git
    ],

    'data': [
        'views/report_template.xml',
        'views/journal_ledger.xml',
        'views/trial_balance_report_view.xml',
        'wizard/trial_balance_wizard.xml',
        'wizard/journal_ledger_wizard_view.xml',
		'wizard/general_ledger_report_wizard_view.xml',
		'report/general_legder.xml'
    ],

    "installable": True,
}
