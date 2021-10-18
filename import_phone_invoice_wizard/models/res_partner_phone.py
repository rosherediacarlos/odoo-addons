# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

from odoo import fields, models


class ResPartnerPhone(models.Model):
	_name = 'res.partner.phone'

	partner_id = fields.Many2one(
		string='Customer',
		comodel_name='res.partner',
		ondelete='cascade'
	)
	
	phone = fields.Char(
		string='Phone',
	)

	product_id = fields.Many2one(
		string='Product',
		comodel_name='product.product',
		domain="[('is_telephone_rate_product', '=', True)]",
		ondelete='cascade'
	)
	
	
