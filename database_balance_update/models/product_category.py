# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
import mysql.connector
from mysql.connector import errorcode

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
	"""
	Mapeado de campos entre los campos de la base de datos de la balanza y odoo para la tabla 'families'
		- Balanza: Odoo.
		- name: name,
		- code: id,
		- label: name,	
	"""
	_inherit = "product.category"
	
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
	
	def insert_caterogy_in_balance(self, conexion=False):
		"""
		Funcion que genera la consulta 'msysql' 
		para insertar los valores necesarios para crear la categoria necesaria.
		"""
		cursor = self.open_cursor(conexion)
		query = ("""INSERT INTO families (code, name, label)
					values ({},'{}','{}');""").format(self.id, self.name, self.name)
		cursor.execute(query)
		if bool(bool(cursor.rowcount) and cursor.rowcount != -1):
			_logger.info("Insert families {} in balance with code {}".format(self.name, self.id))
		conexion.commit()
	
	def update_caterogy_in_balance(self, conexion=False):
		"""
		Funcion que genera la consulta 'msysql' 
		para actualizar los valores de la categoria.
		"""	
		cursor = self.open_cursor(conexion)
		query = (""" UPDATE families
		SET name = '{}', 
			label = '{}'
		WHERE code = {}; 
		""").format(self.name, self.name, self.id)
		cursor.execute(query)
		if bool(bool(cursor.rowcount) and cursor.rowcount != -1):
			_logger.info("Update families {} in balance{}".format(self.name, self.id))
		conexion.commit()
		
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
		

	@api.multi
	def update_balances_categories(self, configuration_models=False):
		"""
		Esta función es la que llamamos desde la función del cron para procesar todo.
		"""
		if bool(len(self)):
			if not configuration_models:
				configuration_models = self.env['balanzas.settings'].sudo().search([])
			for configuration_model in configuration_models:
				conexion = configuration_model.connect_balance()
				if bool(conexion):
					for category in self:
						category._check_balance_categories(conexion)
					
					configuration_model.close_conexion(conexion)