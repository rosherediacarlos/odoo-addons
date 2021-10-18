# -*- coding: utf-8 -*-
# (c) 2020 Juan Carlos Montoya  <jcmontoya@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

from odoo import api, fields, models


class PosOrder(models.Model):
	_inherit = "pos.order"

	account_analytic_id =  fields.Many2one(
		string='Cuenta analitica',
		comodel_name='account.analytic.account',
	)
	
	
	@api.model
	def create(self, values):
		if values.get('sale_journal'):
			# set name based on the sequence specified on the config
			journal_id = self.env['account.journal'].browse(values['sale_journal'])
			if bool(journal_id) and bool(journal_id.account_analytic_id):
				values['account_analytic_id'] = session.config_id.sequence_id._next()
			
		return super(PosOrder, self).create(values)

	@api.model
	def _order_fields(self, ui_order):
		res = super(PosOrder, self)._order_fields(ui_order)
		manipulador = ui_order.get("manipulador", False)
		if manipulador:
			res.update({'manipulador': manipulador})
		return res

	def _create_invoice(self):
		new_invoice = super(PosOrder, self)._create_invoice()
		statement = self.statement_ids.filtered(lambda x: x.journal_id.use_credit)
		if statement:
			domain = [('fixed_journal_id', '=', statement[0].journal_id.id)]
			payment_mode = self.env["account.payment.mode"].search(domain)
			if payment_mode:
				new_invoice.write({'payment_mode_id': payment_mode.id})

		return new_invoice

	def _action_create_invoice_line(self, line=False, invoice_id=False):
		res = super(PosOrder, self)._action_create_invoice_line(line, invoice_id)
		if bool(res.invoice_id) and bool(res.invoice_id.journal_id) and bool(res.invoice_id.journal_id.account_analytic_id):
			res.write({
				'account_analytic_id': res.invoice_id.journal_id.account_analytic_id.id,
			})
		return res

	def _reconcile_payments(self):
		for order in self:
			payment_journal_id = order.statement_ids.mapped('journal_id')
			# credit_journal_id = self.env.ref('pos_debt_notebook.debt_journal_22')
			sepa_journal_id = self.env.ref('atz_pos.account_jorunal_compra_sepa_suministros')
			transferencia_journal_id = self.env.ref('atz_pos.account_jorunal_cuenta_corriente_suministros')
			
			if not sepa_journal_id in payment_journal_id or not transferencia_journal_id in payment_journal_id:
				super(PosOrder,order)._reconcile_payments()