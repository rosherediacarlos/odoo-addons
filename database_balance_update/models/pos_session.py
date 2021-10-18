# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
import mysql.connector
from mysql.connector import errorcode

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
	_inherit = "pos.session"
	
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
	
	def browse_pos_order(self, id_ticket):
		sale_id = self.env['pos.order'].search([
			('ticket_number','=',id_ticket)])
		return sale_id
	
	def obtain_header_ticket_ids(self,date_start,date_end, conexion=False):
		order_line_obj = self.env['pos.order.line']
		order_obj = self.env['pos.order']

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
			exist_sale_id = self.browse_pos_order(hticket_id)
			if bool(exist_sale_id):
				continue
			dict_lines = order_line_obj.generate_pos_order_lines_dict(hticket_id,conexion)

			if bool(dict_lines):

				date = hticket.get('DatTim')
				number = hticket.get('Number')
				location_id = self.config_id.stock_location_id
				pos_order_dict = order_obj.generate_order_dict(self,dict_lines,date,number,location_id)
				if bool(pos_order_dict):
					try:
						pos_order_id = order_obj.sudo().create(pos_order_dict)
						pos_order_id._onchange_amount_all()
						pos_order_id.lines._onchange_amount_line_all()

						pos_order_id.create_payment()
						pos_order_id.action_pos_order_done()
						
						# pos_order_id.action_confirm()
						_logger.info("create sale order for ticket {} so name {}".format(number,pos_order_id.name))
						
						self.env.cr.commit()
					except Exception as e:
						_logger.info("an error occurred while creating the sales order")

		self.close_cursor(cursor)