# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
import mysql.connector
from mysql.connector import errorcode
from decimal import Decimal

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
	"""
	Mapeado de campos entre los campos de la base de datos de la balanza y odoo para la tabla 'vats'
		- Balanza: Odoo.
		- name: name,
		- code: code,
		- percent: amount,	
	"""
	_inherit = "account.tax"

	code = fields.Integer(
		string='Código',
		size=1
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
	
	def insert_vats_in_balance(self, conexion=False):
		"""
		Funcion que genera la consulta 'msysql' para insertar los valores necesarios para crear el impuesto necesario.
		"""
		cursor = self.open_cursor(conexion)
		query = ("""INSERT INTO vats (code, name, percent)
					values ({},'{}','{}');""").format(Decimal(self.code), self.name, Decimal(self.amount))
		cursor.execute(query)
		if bool(bool(cursor.rowcount) and cursor.rowcount != -1):
			_logger.info("Insert vat {} in balance with code {}".format(self.name, Decimal(self.code)))
		conexion.commit()
	
	def update_vats_in_balance(self, conexion=False):
		"""
		Funcion que genera la consulta 'msysql' para actualizar los valores del impuesto.
		"""	
		cursor = self.open_cursor(conexion)
		query = ("""UPDATE vats
		SET name = '{}', percent = {}
		WHERE code = {}; 
		""").format(self.name, Decimal(str(self.amount)), Decimal(self.code))
		cursor.execute(query)
		if bool(bool(cursor.rowcount) and cursor.rowcount != -1):
			_logger.info("Update vat {} in balance".format(self.name))
		conexion.commit()

	def exist_tax_in_balance(self, conexion=False):
		"""
		Funcion que genera la consulta 'msysql' para comprobar si existe un impuesto con el campo codígo en Odoo.
		"""
		cursor = self.open_cursor(conexion)

		query = ("""SELECT code,name,percent
			FROM vats 
			WHERE code = {}""").format(self.code)
		
		cursor.execute(query)

		if not bool(len(cursor._rows)):
			self.close_cursor(cursor)
			return False

		self.close_cursor(cursor)

		return True

	@api.multi
	def _check_balance_tax(self, conexion=False):
		"""
		Función para comprobar si existe o no el elemento en la base de datos para actualizarlo o crearlo.
		"""
		self.ensure_one()
		if self.code:
			exist_in_balance = self.exist_tax_in_balance(conexion)
			if not bool(exist_in_balance):
				self.insert_vats_in_balance(conexion)
			else:
				self.update_vats_in_balance(conexion)
			