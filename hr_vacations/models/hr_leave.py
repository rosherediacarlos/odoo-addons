# -*- coding: utf-8 -*-
# (c) 2021 Praxya - Christian Doñate <cdonate@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    turn_id = fields.Many2one('hr.vacations.turn', string='Turno')
    turno_vacaciones_id = fields.Integer('hr.vacations')