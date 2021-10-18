# -*- coding: utf-8 -*-
# (c) 2020 Juan Carlos Montoya  <jcmontoya@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

from odoo import fields, models, api, http

from odoo.http import request


class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	manipulador = fields.Char(string='Manipulador')

class AccountPaymentMode(models.Model):
	_inherit = 'account.payment.mode'

	@api.model
	def getDataFromXMLID(self, payment_id, supplier_id, bool_invoice):
		sepa_journal_id = self.sudo().env.ref('atz_pos.account_jorunal_compra_sepa_suministros').id
		transferencia_journal_id = self.sudo().env.ref('atz_pos.account_jorunal_cuenta_corriente_suministros').id

		correct = True
		if payment_id in [sepa_journal_id,transferencia_journal_id]:
			if bool(supplier_id) and bool(bool_invoice):
				correct = False
				
		return correct

class AtzenetaPosController(http.Controller):
	
	@http.route('/api/atzeneta/payment_mode_client_and_invoice', type='json', auth='user')
	def payment_mode_client_and_invoice(self):
		res = request.env["account.payment.mode"].sudo().getDataFromXMLID(payment_id=request.jsonrequest['payment_id'], supplier_id=request.jsonrequest['supplier_id'], bool_invoice=request.jsonrequest['bool_invoice'])
		return {
			'result': res
		}