# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
import mysql.connector
from mysql.connector import errorcode

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
	"""
	Para obtener las lineas agrupadas por cabecera necesitamos la id de la cabecera del ticket,
	La tabla es 'htickets'
		- id: para relacionar la cabecera con las lineas
		- DatTim: date_order
		- Number: ticket_number
	"""
	_inherit = "sale.order"

	ticket_number = fields.Integer(
		string='Numero de Ticket',
	)
	
	def open_cursor(self,conexion):
		"""
		Función para abrir un cursor de la conexión de la base de datos de la balanza,
		"""
		cursor = conexion.cursor(dictionary=True, buffered=True)
		return cursor

	def close_cursor(self,cursor):
		"""
		Función para abrir un cursor de la conexión de la base de datos de la balanza,
		"""
		cursor.close()
	
	def browse_sale_order(self, id_ticket):
			sale_id = self.search([
				('ticket_number','=',id_ticket),
				('state','in',('sale','done'))])
			return sale_id
	
	
	def generate_order_dict(self, dict_lines, date, number, warehouse_id):
		pricelist_obj = self.env['product.pricelist']
		
		partner_id = self.env.ref('database_balance_update.partner_cliente_contado')
		pricelist_id = pricelist_obj.search([])[0]
		sale_dict = {}
		if bool(partner_id):
			sale_dict = {
				'ticket_number':number,
				'state': 'draft',
				'order_line': dict_lines,
				'partner_id': partner_id.id,
				'date_order': date,
				'currency_id': partner_id.currency_id,
				'pricelist_id': pricelist_id.id,
				'warehouse_id': warehouse_id.id,
			}
		
		return sale_dict

	def obtain_header_ticket_ids(self,warehouse_id, date_start,date_end, conexion=False):
		order_line_obj = self.env['sale.order.line']

		cursor = self.open_cursor(conexion)

		query = """SELECT id,DatTim,Number 
		FROM htickets
		where DatTim >= '%s 00:00:00'
		and DatTim <= '%s 23:59:59'""" % (date_start,date_end)
		
		cursor.execute(query)

		dict_lines = []
		hticket_old = 0
		for hticket in cursor:
			hticket_id = hticket.get('id')
			exist_sale_id = self.browse_sale_order(hticket_id)
			if bool(exist_sale_id):
				continue
			dict_lines = order_line_obj.generate_sale_order(hticket_id,conexion)

			if bool(dict_lines):

				date = hticket.get('DatTim')
				number = hticket.get('Number')
				sale_dict = self.generate_order_dict(dict_lines,date,number,warehouse_id)
				if bool(sale_dict):
					try:
						sale_id = self.create(sale_dict)
						sale_id.action_confirm()
						_logger.info("create sale order for ticket {} so name {}".format(number,sale_id.name))
						self.env.cr.commit()
					except Exception as e:
						_logger.info("an error occurred while creating the sales order")

		self.close_cursor(cursor)

class SaleOrder(models.Model):
	"""
	Mapeado de campos entre los campos de la base de datos de la balanza y odoo para la tabla 'ltickets'
		- Balanza: Odoo.
		- item: product_id.id,
		- VATCode: taxes_ids.id,
		- weight: cantidad,
		- lineDiscount: discount,
		- price: unit_price,
		- saleForm: unidad_medida,
		- lineType: state (0-cancel 1-confirm)	
	"""
	_inherit = "sale.order.line"
	
	def open_cursor(self,conexion):
		"""
		Función para abrir un cursor de la conexión de la base de datos de la balanza,
		"""
		cursor = conexion.cursor(dictionary=True, buffered=True)
		return cursor

	def close_cursor(self,cursor):
		"""
		Función para abrir un cursor de la conexión de la base de datos de la balanza,
		"""
		cursor.close()

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
		}	
		if bool(db_dict.get('VATCode')):
			tax_id = tax_obj.sudo().browse(int(db_dict.get('VATCode'))).exists()
			if not bool(tax_id) and bool(product_id):
				tax_id = product_id.taxes_id[0]
			if bool(tax_id):
				line_dict['tax_id'] = [(6,0, tax_id.ids)]
		
		if bool(db_dict.get('Weight')):
			line_dict['product_uom_qty'] = float(db_dict.get('Weight'))
		
		if bool(db_dict.get('Price')):
			line_dict['precio_unitario'] = float(db_dict.get('Price'))
			line_dict['price_unit'] = float(db_dict.get('Price'))

		return line_dict


	def generate_sale_order(self, hticket_id, conexion=False):
		cursor = self.open_cursor(conexion)

		query = ("""SELECT * 
		FROM ltickets 
		where IdHTicket = %i""") % hticket_id
		
		cursor.execute(query)

		lines = []

		for lticket in cursor:
			line_dict = self.create_line_dict(lticket)
			if bool(line_dict):
				lines.append((0,0,line_dict))

		self.close_cursor(cursor)
		return lines

	def exist_category_in_balance(self, conexion=False):
		"""
		Funcion que genera la consulta 'msysql' 
		para comprobar si existe una categoria con el id de Odoo.
		"""
		cursor = self.open_cursor(conexion)

		query = ("""SELECT code
			FROM families 
			WHERE code = {}""").format(self.id)
		
		cursor.execute(query)

		if not bool(len(cursor._rows)):
			self.close_cursor(cursor)
			return False

		self.close_cursor(cursor)

		return True

	@api.multi
	def _check_balance_categories(self, conexion=False):
		"""
		Función para comprobar si existe o no el elemento 
		en la base de datos para actualizarlo o crearlo.
		"""
		self.ensure_one()
		exist_in_balance = self.exist_category_in_balance(conexion)
		if not bool(exist_in_balance):
			self.insert_caterogy_in_balance(conexion)
		else:
			self.update_caterogy_in_balance(conexion)
		# TODO: Implementar
	
