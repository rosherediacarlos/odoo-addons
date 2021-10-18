# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

from odoo import fields, models


class ResPartner(models.Model):
	_inherit = 'res.partner'

	phone_list_ids = fields.One2many(
		string='Phone list',
		comodel_name='res.partner.phone',
		inverse_name='partner_id',
	)
	
	
