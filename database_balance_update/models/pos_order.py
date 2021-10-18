# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
import mysql.connector
from mysql.connector import errorcode

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
	_inherit = "pos.order"

	ticket_number = fields.Integer(
		string='Numero de Ticket',
	)

	@api.onchange('statement_ids', 'lines')
	def _onchange_amount_all(self):
		super(PosOrder,self)._onchange_amount_all()
		for order in self:
			if bool(order.config_id.iface_tax_included == 'total'):
				order.amount_total = order.amount_tax


	def _prepare_invoice(self):
		res = super(PosOrder,self)._prepare_invoice()
		if bool(self.account_move):
			res['move_id'] =  self.account_move.id
		return res

	def generate_order_dict(self, session_id, dict_lines, date, number,location):
		pricelist_obj = self.env['product.pricelist']
		
		partner_id = self.env.ref('database_balance_update.partner_cliente_contado')
		pricelist_id = pricelist_obj.search([])[0]
		pos_order_dict = {}
		if bool(partner_id):
			pos_order_dict = {
				'ticket_number':number,
				'lines': dict_lines,
				'partner_id': partner_id.id,
				'date_order': date,
				'location_id': location.id if location else False,
				'session_id': session_id.id,
				'config_id': session_id.config_id.id,
				'amount_return': 0.0,
				'amount_paid': 0.0,
				'amount_tax': 0.0,
				'amount_total':0.0,
			}
		
		return pos_order_dict

	def create_payment(self):
		wizard_obj = self.env['pos.make.payment']
		journal_obj = self.env['account.journal']

		self.env.context = dict(self.env.context)
		self.env.context.update({'active_id': self.id})

		journal_id = journal_obj.search([('code','=','CSH1')])
		if not bool(journal_id):
			journal_id = self.session_id.config_id.journal_ids.ids[0]

		payment_id = wizard_obj.with_context(self.env.context).create({
			'session_id':self.session_id.id,
			'journal_id':journal_id.id,
			'amount':float(self.amount_total),
			'payment_date':self.date_order,
		})
		if bool(payment_id):
			payment_id.check()

class PosOrderLine(models.Model):
	"""
	Mapeado de campos entre los campos de la base de datos de la balanza y odoo para la tabla 'ltickets'
		- Balanza: Odoo.
		- item: product_id.id,
		- VATCode: tax_ids.id,
		- weight: qty,
		- price: price_unit,
		- lineType: state (0-cancel 1-confirm)	
	"""
	_inherit = "pos.order.line"

	def generate_pos_order_lines_dict(self, hticket_id, conexion=False):
		cursor = self.env['pos.session'].open_cursor(conexion)

		query = ("""SELECT * 
		FROM ltickets 
		where IdHTicket = %i""") % hticket_id
		
		cursor.execute(query)

		lines = []

		for lticket in cursor:
			line_dict = self.create_line_dict(lticket)
			if bool(line_dict):
				lines.append((0,0,line_dict))

		self.env['pos.session'].close_cursor(cursor)
		return lines
	
	def create_line_dict(self,db_dict):
		product_obj = self.env['product.product']
		tax_obj = self.env['account.tax']

		if not bool(db_dict.get('Item')) or not bool(db_dict.get('lineType')):
			return False
		
		product_id = product_obj.sudo().browse(int(db_dict.get('Item'))).exists()
		if not bool(product_id):
			return False

		line_dict = {
			'product_id': product_id.id,
			'name': product_id.display_name,
			'product_uom': product_id.uom_id.id,
			'price_unit': product_id.lst_price,
			'name':self.env['ir.sequence'].next_by_code('pos.order.line'),
			'price_subtotal': float(db_dict.get('Amount')) if bool(db_dict.get('Amount')) else 0.0,
			'price_subtotal_incl':0.0,

		}	
		if bool(db_dict.get('VATCode')):
			tax_id = tax_obj.sudo().search([('code','=',int(db_dict.get('VATCode',0)))])
			if not bool(tax_id) and bool(product_id):
				tax_id = product_id.taxes_id[0]
			if bool(tax_id):
				line_dict['tax_ids'] = [(6,0, tax_id.ids)]
				
		
		if bool(db_dict.get('Weight')):
			line_dict['qty'] = float(db_dict.get('Weight'))
		
		if bool(db_dict.get('Price')):
			line_dict['price_unit'] = float(db_dict.get('Price'))

		return line_dict
	
	