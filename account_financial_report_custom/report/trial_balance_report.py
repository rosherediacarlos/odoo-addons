# -*- coding: utf-8 -*-
# (c) 2019 Carlos Ros <cros@praxya.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class GeneralLedgerReportCompute(models.TransientModel):
    _inherit = 'report_general_ledger'

    @api.model
    def create(self,vals):
        res = super(GeneralLedgerReportCompute,self).create(vals)
        return res
    
    def _get_account_sub_subquery_sum_amounts(
            self, include_initial_balance, date_included):
        """ Return subquery used to compute sum amounts on accounts """
        sub_subquery_sum_amounts = """
            SELECT
                a.id AS account_id,
                SUM(ml.debit) AS debit,
                SUM(ml.credit) AS credit,
                SUM(ml.balance) AS balance,
                c.id AS currency_id,
                CASE
                    WHEN c.id IS NOT NULL
                    THEN SUM(ml.amount_currency)
                    ELSE NULL
                END AS balance_currency
            FROM
                accounts a
            INNER JOIN
                account_account_type at ON a.user_type_id = at.id
            INNER JOIN
                account_move_line ml
                    ON a.id = ml.account_id
        """

        if date_included:
            sub_subquery_sum_amounts += """
                AND ml.date <= %s
            """
        else:
            sub_subquery_sum_amounts += """
                AND ml.date < %s
            """

        if not include_initial_balance:
            sub_subquery_sum_amounts += """
                AND at.include_initial_balance != TRUE AND ml.date >= %s
            """
        else:
            sub_subquery_sum_amounts += """
                AND at.include_initial_balance = TRUE
            """
        if self.filter_journal_ids:
            sub_subquery_sum_amounts += """
            AND
                ml.journal_id IN (%s)
            """ % ', '.join(map(str, self.filter_journal_ids.ids))

        if self.only_posted_moves:
            sub_subquery_sum_amounts += """
        INNER JOIN
            account_move m ON ml.move_id = m.id AND m.state = 'posted'
            """
        if self.filter_cost_center_ids:
            sub_subquery_sum_amounts += """
        INNER JOIN
            account_analytic_account aa
                ON
                    ml.analytic_account_id = aa.id
                    AND aa.id IN %s
            """
        if self.filter_analytic_tag_ids:
            sub_subquery_sum_amounts += """
        INNER JOIN
            move_lines_on_tags ON ml.id = move_lines_on_tags.ml_id
            """
        sub_subquery_sum_amounts += """
        LEFT JOIN
            res_currency c ON a.currency_id = c.id
        """

        if bool(self._context.get('account_analytic')):
            query = """WHERE
                ml.analytic_account_id = {}
            """ .format(self._context.get('account_analytic'))

            if bool(self._context.get('show_account_child')):
                account_id = self.env['account.analytic.account'].browse(self._context.get('account_analytic'))
                account_ids = account_id.get_account_children()
                account_ids |= account_id
                query = """WHERE ml.analytic_account_id in {}""".format(tuple(account_ids.ids))

            sub_subquery_sum_amounts += query

        sub_subquery_sum_amounts += """
        GROUP BY
            a.id, c.id
        """

        
        return sub_subquery_sum_amounts


class TrialBalanceReport(models.TransientModel):
    _inherit = 'report_trial_balance'


    def get_analytic(self):
        if bool(self._context.get('account_move_lines')):
            return self._context.get('account_move_lines')
        return False

    def calculate_total_initial_balance(self):
        if self.account_ids:
            if self.filter_account_ids and self.hierarchy_on != 'relation':
                total = sum(x.initial_balance for x in self.account_ids)

            else:
                total = sum(x.initial_balance for x
                            in self.account_ids.filtered(
                                lambda a: a.account_id
                                   and not a.account_group_id
                                   and len(a.code) > 4
                                   and not a.compute_account_ids))

        return total

    def calculate_total_debit(self):
        if self.account_ids:
            if self.filter_account_ids and self.hierarchy_on != 'relation':
                total = sum(x.debit for x in self.account_ids)

            else:
                total = sum(x.debit for x
                                in self.account_ids.filtered(
                                    lambda a: a.account_id
                                       and not a.account_group_id
                                       and len(a.code) > 4
                                       and not a.compute_account_ids))

        return total

    def calculate_total_credit(self):
        if self.account_ids:
            if self.filter_account_ids and self.hierarchy_on != 'relation':
                total = sum(x.credit for x in self.account_ids)

            else:
                total = sum(x.credit for x
                                in self.account_ids.filtered(
                                    lambda a: a.account_id
                                       and not a.account_group_id
                                       and len(a.code) > 4
                                       and not a.compute_account_ids))

        return total

    def calculate_total_period_balance(self):
        if self.account_ids:

            if self.filter_account_ids and self.hierarchy_on != 'relation':
                total = sum(x.period_balance for x in self.account_ids)

            else:
                total = sum(x.period_balance for x
                                in self.account_ids.filtered(
                                    lambda a: a.account_id
                                       and not a.account_group_id
                                       and len(a.code) > 4
                                       and not a.compute_account_ids))

        return total
