# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

from odoo import fields, models


class InvoiceImportError(models.Model):
    _name = 'invoice.import.error'

    line_number = fields.Char(
        string='Número línea',
    )
    
    import_date = fields.Date(
        string='Fecha importación',
    )

    description = fields.Text(
        string='Descripción',
    )
    
    
