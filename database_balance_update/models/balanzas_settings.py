# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, date, timedelta

import logging

from odoo import models, fields, api
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class BalanzasSettings(models.Model):
	_inherit = 'balanzas.settings'

	
	pos_config_id = fields.Many2one(
		string='Punto de Venta',
		comodel_name='pos.config',
		ondelete='cascade',
	)

	pricelist_id = fields.Many2one(
		string='Tarifa',
		comodel_name='product.pricelist',
	)
	
	@property
	@api.multi
	def product_categories(self):
		"""
		Función para obtener todas las categorias de Odoo
		"""
		# self.ensure_one()
		product_categ_obj = self.env['product.category'].sudo()
		categories_ids = product_categ_obj.search([])
		return categories_ids
	
	@property
	@api.multi
	def product_product(self):
		"""
		Función para obtener todos los productos en odoo,
		siempre que esten activos y marcado el campo de balanza
		"""
		# self.ensure_one()
		product_obj = self.env['product.product'].sudo()
		product_ids = product_obj.search([('active','=',True),('tpv','=', True)])
		return product_ids	
	
	def create_update_balance(self,location_id,vals=False,pos=False):
		pos_config_obj = self.env['pos.config']

		picking_type = self.env.ref('point_of_sale.picking_type_posout')
		pos_id = False

		pricelist_id = self.env.ref('database_balance_update.product_pricelist_pos')
		if bool(vals.get('pricelist_id')):
			pricelist_id = self.env['product.pricelist'].browse(vals.get('pricelist_id'))
		elif bool(self.pricelist_id):
			pricelist_id = self.pricelist_id

		if not bool(pos):
			
			pos_id = pos_config_obj.create({
				'name': 'TPV {}'.format(vals.get('name') or self.name),
				'iface_tax_included': 'total',
				'picking_type_id': picking_type.id,
				'stock_location_id':location_id.id,
				'module_account': True,
				'use_pricelist': True,
				'pricelist_id':pricelist_id.id if pricelist_id else False,
				'available_pricelist_ids':[(6,0,pricelist_id.ids)] if pricelist_id else False,
			})
		else:
			pos_vals = {}

			if bool(location_id):
				pos_vals = {
					'stock_location_id':location_id if location_id else False,
				}

			if bool(pricelist_id):
				pos_vals = {
					'available_pricelist_ids': [(4,pricelist_id.id)] if pricelist_id else False,
					'pricelist_id':pricelist_id.id if pricelist_id else False,
					
				}

			pos.update(pos_vals)
			pos_id = pos
		return pos_id


	def write(self, vals):
		
		pos_id = self.pos_config_id.id or vals.get('pos_config_id')

		if bool(vals.get('warehouse')) or vals.get('pricelist_id'):
			warehouse_id = self.env['stock.warehouse'].browse(vals.get('warehouse'))

			# if not bool(warehouse_id):
			# 	raise UserError('La balanza no tiene almacen')

			# if not bool(warehouse_id.lot_stock_id):
			# 	raise UserError('El almacen no tiene ubicación')

			pos = self.pos_config_id 
			if bool(vals.get('pos_config_id')):
				pos = self.env['stock.location'].browse(vals.get('pos_config_id'))

			pos_id = self.create_update_balance(warehouse_id.lot_stock_id, vals, pos)
			if bool(pos_id):
				vals.update({
					'pos_config_id': pos_id.id,
				})

		res = super(BalanzasSettings,self).write(vals)
		return res

	@api.model
	def create(self, vals):
		

		if bool(vals.get('warehouse')):
			warehouse_id = self.env['stock.warehouse'].browse(vals.get('warehouse'))

			if not bool(warehouse_id):
				raise UserError('La balanza no tiene almacen')

			if not bool(warehouse_id.lot_stock_id):
				raise UserError('El almacen no tiene ubicación')

			pos_id = self.create_update_balance(warehouse_id.lot_stock_id,vals)
			if bool(pos_id):
				vals.update({
					'pos_config_id': pos_id.id,
			})

		res = super(BalanzasSettings,self).create(vals)
		return res

	@api.model
	def connect_balance(self):
		"""
		Funcion para conectarse a la base de datos de la balanza.
			Los parametros para la configuración de la conexión estan dentro de modelo "balanzas.type" 
		"""
		_logger.info('Conecting to balance DB')
		try:
			cnx = mysql.connector.connect(user=self.typeBalanza.user, 
				password=self.typeBalanza.password,
				host=self.typeBalanza.balance_ip,
				database=self.typeBalanza.database_name)
			return cnx
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				_logger.info("Something is wrong with your user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				_logger.info("Database does not exist")
			else:
				_logger.info(err)
			return False
	
	def close_conexion(self, conexion):
		"""
		Función para cerrar la conexion a la base de datos.
		"""
		return conexion.close()

	def generate_sale_order_from_balance(self, date_start, date_end):
		warehouse_id = self.warehouse
		conexion = self.connect_balance()
		# self.env['sale.order'].sudo().obtain_header_ticket_ids(warehouse_id,date_start, date_end, conexion)
		# conexion = False
		self.generate_pos_orders(date_start, date_end, conexion)

	def generate_pos_orders(self, date_start, date_end, conexion):	
		session_obj = self.env['pos.session']
		pos_order_obj = self.env['pos.order']

		#variables
		user_id = self.env.user or self.env.ref('base.user_root')
		config_id = self.pos_config_id

		session_id = session_obj.create({
			'user_id': user_id.id,
			'config_id':config_id.id,
		})
		# self.env.cr.commit()
		#Open session from balance
		session_id.action_pos_session_open()
		#Get orders from balance
		session_id.obtain_header_ticket_ids(date_start, date_end, conexion)
		#Close sessions and orders
		session_id.action_pos_session_closing_control()



	def generate_sale_order_from_cron(self):
		"""
		Función creada para que sea llamada desde el cron de actualizar los pedidos de la balanaza en odoo,
		"""
		warehouse_obj = self.env['stock.warehouse']
		warehouse_ids = warehouse_obj.sudo().search([])

		date_start = datetime.now().date()
		date_end = datetime.now().date()
		#date = '2021-05-26'
		#date_start = date_end = datetime.strptime(date,'%Y-%m-%d').date()
		for warehouse in warehouse_ids:
			balanzas = self.sudo().search([('warehouse','=',warehouse.id)])
			for balanza in balanzas:
				balanza.generate_sale_order_from_balance(date_start, date_end)	

	def send_balance_product_caterogies(self):
		"""
		Función creada para que sea llamada desde el cron de actualizar categorias,
		"""
		warehouse_obj = self.env['stock.warehouse']
		warehouse_ids = warehouse_obj.sudo().search([])

		for warehouse in warehouse_ids:
			balanzas = self.sudo().search([('warehouse','=',warehouse.id)])
			for balanza in balanzas:
				balanza.product_categories.sudo().update_balances_categories(balanza)
	
	def send_balance_product_product(self):
		"""
		Función creada para que sea llamada desde el cron de actualizar productos,
		"""
		warehouse_obj = self.env['stock.warehouse']
		warehouse_ids = warehouse_obj.sudo().search([])

		for warehouse in warehouse_ids:
			balanzas = self.sudo().search([('warehouse','=',warehouse.id)])
			for balanza in balanzas:
				balanza.product_product.update_balances_products(balanza)

