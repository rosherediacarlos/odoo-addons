# -*- coding: utf-8 -*-
# (c) 2019 Carlos Ros <cros@praxya.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class GeneralLedgerReportWizard(models.TransientModel):
    _inherit = "general.ledger.report.wizard"

    account_analytic_id =  fields.Many2one(
        string='Account Analytic',
        comodel_name='account.analytic.account',
    )

    show_account_child =  fields.Boolean(
        string='Cuentas Hijas',
    )  

   