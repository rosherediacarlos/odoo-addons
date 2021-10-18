# -*- coding: utf-8 -*-
# (c) 2021 Praxya - Christian Doñate <cdonate@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Vacations",
    "summary": "Crea turnos de vacaciones, añades dos elementos de menú en Ausencias/Responsables",
    "version": "1.02",
    "category": 'Human Resources',
    'website': 'http://www.praxya.com/',
    "author": "Praxya",
    "license": "AGPL-3",
    "depends": [
        'hr',
		'hr_holidays_leave_auto_approve'
    ],
    "data": [
        'security/ir.model.access.csv',
		'data/hr_leave_type_data.xml',
        'views/hr_leave_view.xml',
        'views/hr_vacations_view.xml',
		'views/hr_vacations_turn_view.xml',
        'reports/paperformat.xml',
        'reports/vacations.xml',
        'wizard/hr_vacations_wizard_view.xml',
        'wizard/hr_vacations_report_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
