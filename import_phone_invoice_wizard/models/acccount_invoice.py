# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/a

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    import_date = fields.Date(
        string='Fecha importación',
    )
    

    
    
    
