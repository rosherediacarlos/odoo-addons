# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

from odoo import fields, models, _


class ProductProduct(models.Model):
	_inherit = 'product.product'

	is_telephone_rate_product = fields.Boolean(
		string='Telephone rate product',
	)
	
	
