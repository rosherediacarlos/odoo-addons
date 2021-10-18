# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
import mysql.connector
from mysql.connector import errorcode

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
	"""
	Mapeado de campos entre los campos de la base de datos de la balanza y odoo
		- Balanza: Odoo.
		- name: product.name,
		- code: product.id,
		- saleform: uom_id (Booleano, Marcado kg desmarcado Unidades)
		- weight: product.quantity_available por almacen en concreto de la bascula.
		- units: product.quantity_available por almacen en concreto de la bascula.
		Los campos units o weight se rellenan dependiendo de la unidad de medida.
	"""
	_inherit = "stock.quant"

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
	
	def compute_valor(self, product_id=False, warehouse_id=False):
		quantity = 0
		if bool(product_id) and bool(warehouse_id):
			location_id = warehouse_id.lot_stock_id
			product_quant_ids = location_id.quant_ids.filtered(lambda x: x.product_id.id == product_id.id)
			quantity = sum(product_quant_ids.mapped('quantity')) - sum(product_quant_ids.mapped('reserved_quantity'))
		return quantity

	def insert_new_stock_in_balance(self, qty, conexion=False, product_id=False, configuration_model=False):
		if not product_id:
			return False
		
		cursor = self.open_cursor(conexion)

		uom = product_id.balance_uom()
		quantity = 'weight'
		quantityValue = '%.3f' % qty
		if not bool(uom):
			quantity = 'units'
			quantityValue = '%i' % qty
		
		query = """INSERT INTO stock (code, name, saleform, %s)
				values (%i,'%s',%i,%s);""" % (quantity, product_id.id, product_id.name,uom, quantityValue)

		cursor.execute(query)

		if bool(bool(cursor.rowcount) and cursor.rowcount != -1):
			_logger.info("Insert stock in balance for product {}".format(product_id.id))
		
		conexion.commit()
		self.env.cr.commit()

	def update_product_in_balance(self,qty, conexion=False,product_id=False, configuration_model=False):
		if not product_id:
			return False
		
		cursor = self.open_cursor(conexion)

		uom = product_id.balance_uom()
		quantity = 'weight'
		quantityValue = '%.3f' % qty
		if not bool(uom):
			quantity = 'units'
			quantityValue = '%i' % qty
		
		query = """UPDATE stock
		SET %s = %s
		WHERE code = %i;""" % (quantity, quantityValue, product_id.id)
		
		cursor.execute(query)

		if bool(bool(cursor.rowcount) and cursor.rowcount != -1):
			_logger.info("Update stock in balance for product {}".format(product_id.id))

		conexion.commit()
		self.env.cr.commit()
		
	def exist_stock_for_product(self, conexion=False, product_id=False):
		if not product_id:
			return False

		cursor = self.open_cursor(conexion)

		query = """SELECT code
			FROM stock
			WHERE code = %i""" % product_id.id
		
		cursor.execute(query)

		if not bool(len(cursor._rows)):
			self.close_cursor(cursor)
			return False

		self.close_cursor(cursor)

		return True

	@api.multi
	def _check_balance_products_stock(self, conexion=False, product_id=False,warehouse_id=False):

		if not product_id:
			return False
		
		qty = self.compute_valor(product_id, warehouse_id)
		exist_in_balance = self.exist_stock_for_product(conexion,product_id)
		if not bool(exist_in_balance):
			self.insert_new_stock_in_balance(qty,conexion,product_id)
		else:
			self.update_product_in_balance(qty,conexion,product_id)