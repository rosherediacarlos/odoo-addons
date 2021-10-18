# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
import mysql.connector
from mysql.connector import errorcode
from paramiko import SSHClient
from scp import SCPClient
import imghdr
# import asyncio, asyncssh

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
	"""
	Mapeado de campos entre los campos de la base de datos de la balanza y odoo
		- Balanza: Odoo.
		- name: name,
		- shortname: name,
		- code: id,
		- family: categ_id.parent,
		- subfamily: categ_id.name,
		- price: list_price/lst_price,
		- vat: taxes_id.amount / 100,
		- ean13: barcode,
		- text: description_sale
		- saleform: uom_id (Booleano, Marcado kg desmarcado Unidades)
	
	"""
	_inherit = "product.product"
	
	@api.multi
	def create_image_attachment(self):
		image = False
		if bool(self.image):
			image = self.env['ir.attachment'].create({
				"datas_fname":"{}".format(self.id),
				"name":"Image - " + str(self.id),
				"store_fname": "{}".format(self.id),
				"datas":self.image,
				"mimetype":'application/png',
				"res_model":'product.template',
				"res_id": self.id,
				})
			self.env.cr.commit()
		return image
		

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
	
	def update_balance_icon(self, image, extension):
		if bool(image):
			ssh = SSHClient()
			ssh.load_system_host_keys()
			ssh.connect(hostname="192.168.1.102", username="pcscale", password="epelsa")
			scp = SCPClient(ssh.get_transport())
			scp.put(image._full_path(image.store_fname), '/home/pcscale/scale/resources/icons/item/{}.{}'.format(self.id,extension))
			scp.close()
		
	def balance_uom(self):
		saleform = True
		product_uom_id = self.uom_id
		unit_uom_id = self.env.ref('uom.product_uom_unit')
		if bool(unit_uom_id) and self.uom_id.id == unit_uom_id.id:
			saleform = False
		return saleform

	def product_tax(self,conexion=False):
		"""
		Función para obtener el codígo del impuesto. 
		Además llama la funcion _check_balance_tax para
		comprobar si este impuesto existe en la balanza. 
		Y crearlo o actualizarlo si es necesario.
		"""
		tax_code = ''
		tax_id = self.taxes_id
		if len(tax_id) > 1:
			tax_id = tax_id[0]
		
		tax_id._check_balance_tax(conexion)
		tax_code = tax_id.code

		return tax_code

	def product_categories(self):
		"""
		Función para obtener el nombre de la categoria y subcategoria si tiene
		"""
		categ_id = False
		sub_categ_id  = False
		if self.categ_id and not self.categ_id.parent_id:
			categ_id = self.categ_id.id

		elif self.categ_id and self.categ_id.parent_id: 	
			categ_id = self.categ_id.parent_id.id
			sub_categ_id  = self.categ_id.id
		
		return categ_id,sub_categ_id
	
	def insert_product_in_balance(self,pricelist_id, conexion=False):
		"""
		Funcion que genera la consulta 'msysql' 
		para insertar los valores necesarios para crear el producto necesario.
		"""
		cursor = self.open_cursor(conexion)

		categ_id, sub_categ_id = self.product_categories()
		price = self.list_price if bool(self.list_price) else self.lst_price
		tax_code = self.product_tax(conexion)
		uom = self.balance_uom()

		if bool(pricelist_id):
			item_ids = pricelist_id.item_ids.filtered(lambda x: x.product_id.id == self.id and min_quantity <= 1)
			if bool(item_ids):
				price = item_ids[0].fixed_price

		#Update image
		image = self.create_image_attachment()
		if bool(image):
			extension = imghdr.what(image._full_path(image.store_fname))
			# if bool(extension):
				#self.update_balance_icon(image, extension)
				
		image_name =  "{}.{}".format(self.id,extension) if bool(image) and bool(extension) else False
		
		query = ("""INSERT INTO items (code, name, shortname, text, price, ean13, family, subfamily, vat, saleform, icon)
					values ({},'{}','{}', '{}', {}, '{}',{},{},{},{},'{}');""").format(self.id, self.name, self.name[:60], self.description_sale, price,self.barcode or '', categ_id, sub_categ_id,tax_code,uom,image_name)

		cursor.execute(query)

		if bool(bool(cursor.rowcount) and cursor.rowcount != -1):
			_logger.info("Insert items {} in balance with code {}".format(self.name, self.id))
		
		conexion.commit()
		if bool(image):
			image.unlink()
		self.env.cr.commit()

	def update_product_in_balance(self, pricelist_id, conexion=False):
		"""
		Funcion que genera la consulta 'msysql' 
		para actualizar los valores del producto.
		"""	
		cursor = self.open_cursor(conexion)

		categ_id, sub_categ_id = self.product_categories()
		price = self.list_price if bool(self.list_price) else self.lst_price
		tax_code = self.product_tax(conexion)
		uom = self.balance_uom()

		if bool(pricelist_id):
			item_ids = pricelist_id.item_ids.filtered(lambda x: x.product_id.id == self.id and x.min_quantity <= 1)
			if bool(item_ids):
				price = item_ids[0].fixed_price

		#Update image
		image = self.create_image_attachment()
		if bool(image):
			extension = imghdr.what(image._full_path(image.store_fname))
			# if bool(extension):
				#self.update_balance_icon(image, extension)
				
		image_name =  "{}.{}".format(self.id,extension) if bool(image) and bool(extension) else False
		
		query = (""" UPDATE items
		SET name = '{}',
			shortname = '{}',
			text = '{}', 
			price = {}, 
			ean13 = '{}',
			family = {},
			subfamily = {},
			vat = {},
			saleform = {},
			icon = '{}'
		WHERE code = {}; 
		""").format(self.name, self.name[:60], self.description_sale, price, self.barcode or '', categ_id, sub_categ_id,tax_code,uom, image_name, self.id)
		
		cursor.execute(query)

		if bool(bool(cursor.rowcount) and cursor.rowcount != -1):
			_logger.info("Update items {} in balance{}".format(self.name, self.id))

		conexion.commit()
		if bool(image):
			image.unlink()
		self.env.cr.commit()
		
	def exist_product_in_balance(self, conexion=False):
		"""
		Funcion que genera la consulta 'msysql' 
		para comprobar si existe un producto con el id de Odoo.
		"""
		cursor = self.open_cursor(conexion)

		query = ("""SELECT code
			FROM items 
			WHERE code = {}""").format(self.id)
		
		cursor.execute(query)

		if not bool(len(cursor._rows)):
			self.close_cursor(cursor)
			return False

		self.close_cursor(cursor)

		return True

	@api.multi
	def _check_balance_products(self,pricelist_id, conexion=False):
		"""
		Función para comprobar si existe o no el elemento 
		en la base de datos para actualizarlo o crearlo.
		"""
		self.ensure_one()
		exist_in_balance = self.exist_product_in_balance(conexion)
		if not bool(exist_in_balance):
			self.insert_product_in_balance(pricelist_id,conexion)
		else:
			self.update_product_in_balance(pricelist_id,conexion)
		# TODO: Implementar
		

	@api.multi
	def update_balances_products(self, configuration_models=False):
		"""
		Esta función es la que llamamos desde la función del cron para procesar todo.
		"""
		quant_obj = self.env['stock.quant']
		if bool(len(self)):
			if not configuration_models:
				configuration_models = self.env['balanzas.settings'].sudo().search([])
			for configuration_model in configuration_models:
				conexion = configuration_model.connect_balance()
				if bool(conexion):
					for product in self:
						product._check_balance_products(configuration_model.pricelist_id,conexion)
						quant_obj._check_balance_products_stock(conexion,product,configuration_model.warehouse)
					configuration_model.close_conexion(conexion)