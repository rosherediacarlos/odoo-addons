# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros <cros@praxya.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat


class JournalLedgerReportWizard(models.TransientModel):
    _inherit = 'journal.ledger.report.wizard'

    account_analytic_id =  fields.Many2one(
        string='Cuenta anailtica',
        comodel_name='account.analytic.account',
    )

    show_account_child =  fields.Boolean(
        string='Cuentas Hijas',
    )

    def _prepare_report_journal_ledger(self):
        res = super(JournalLedgerReportWizard,self)._prepare_report_journal_ledger()

        if bool(self.account_analytic_id):
            res['account_analytic_id'] = self.account_analytic_id.id
            res['show_account_child'] = self.show_account_child

        return res
    