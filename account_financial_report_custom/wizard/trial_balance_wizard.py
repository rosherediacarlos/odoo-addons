# -*- coding: utf-8 -*-
# (c) 2019 Carlos Ros <cros@praxya.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class TrialBalanceReportWizard(models.TransientModel):
    _inherit = "trial.balance.report.wizard"

    account_analytic_id =  fields.Many2one(
        string='Account Analytic',
        comodel_name='account.analytic.account',
    )

    show_account_child =  fields.Boolean(
        string='Cuentas Hijas',
    )  

    @api.multi
    def button_export_html(self):
        if not self.receivable_accounts_only and not self.payable_accounts_only and self.hierarchy_on != 'relation':

            account_ids = self.env['account.move.line'].search([
                    ('date', '<=', self.date_to),
                    ('date', '>=', self.date_from)
                ]).mapped('account_id')
            self.account_ids = [(6,0,account_ids.ids)]

        if bool(self.account_analytic_id):
            account_ids = self.env['account.move.line'].search([
                ('date', '<=', self.date_to),
                ('analytic_account_id','=',self.account_analytic_id.id),
                ('date', '>=', self.date_from)
            ]).mapped('account_id')

            if bool(account_ids):
                self.account_ids = [(6,0,account_ids.ids)]

        if self.hide_account_at_0:
            for account in self.account_ids:
                account_move_line_id = self.env['account.move.line'].search([
                    ('account_id', '=', account.id),
                    ('date', '<=', self.date_to),
                    ('date', '>=', self.date_from)
                ])
                if not account_move_line_id:
                    self.account_ids = [(2, account.id)]

        if bool(self.account_analytic_id):
            self.env.context = dict(self.env.context)
            self.env.context.update({'account_analytic': self.account_analytic_id.id})
            self.env.context.update({'show_account_child': self.show_account_child})
        res = super(TrialBalanceReportWizard, self).button_export_html()
        if bool(self.account_analytic_id):
            res['context']['account_move_lines'] = self.account_analytic_id.id
        return res
