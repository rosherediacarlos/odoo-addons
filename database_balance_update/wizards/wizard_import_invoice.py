# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

from odoo import api, models, fields


class WizardUpdateBalanceData(models.TransientModel):
	_name = "wizard.update.balance.data"
	
	warehouse_id = fields.Many2one(
		required="True",
		string='Almacen',
		comodel_name='stock.warehouse',
		ondelete='restrict',
	)
	
	type = fields.Selection(
		string='Tipo importación',
		selection=[('all', 'Todas las basculas'), ('one', 'Solo los valores de una bascula')],
		default="all"
	)

	balance_id = fields.Many2one(
		comodel_name="balanzas.settings",
		string = "Almacen",
		domain="[('warehouse','=',warehouse_id)]")
	
	date_start = fields.Date(
		string='Fechas inicio',
		default=fields.Date.context_today,
	)

	date_end = fields.Date(
		string='Fecha fin',
		default=fields.Date.context_today,
	)
	
	
	def start_import_balance_data(self):
		balance_setting_obj = self.env['balanzas.settings']
		
		warehouse_id = self.warehouse_id
		type = self.type

		if type == 'all' and not self.balance_id:
			balance_ids = balance_setting_obj.search([('warehouse','=',warehouse_id.id)])
		else:
			balance_ids = self.balance_id

		for balance_id in balance_ids:
			
			balance_id.generate_sale_order_from_balance(self.date_start,self.date_end)
