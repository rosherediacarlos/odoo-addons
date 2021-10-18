# -*- coding: utf-8 -*-
# (c) 2021 Praxya - Christian Doñate <cdonate@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, exceptions, api, _
from datetime import date
from odoo.exceptions import ValidationError


class HrVacationsWizard(models.TransientModel):
	_name = "hr.vacations.wizard"

	year_id = fields.Many2one(string='Año',comodel_name='hr.vacations.year')
	employee_ids = fields.Many2many('hr.employee', string="Empleado")
	turn_id =  fields.Many2one('hr.vacations.turn', string='Turno')
	fecha_start = fields.Date(string='Fecha desde', related='turn_id.fecha_start', readonly=True)
	fecha_end = fields.Date(string='Fecha hasta', related='turn_id.fecha_end', readonly=True)
	dias = fields.Float(string='Días', compute="get_dias")

	@api.depends('fecha_start','fecha_end')
	def get_dias(self):
		for x in self:
			dias = 0
			if bool(x.fecha_end) and bool( x.fecha_start):
				dias = (x.fecha_end - x.fecha_start).days + 1
			x.dias = dias

	def btn_vacation(self):
		vals = {
			'year_id':self.year_id.id,
			'employee_ids':[(6,0, self.employee_ids.ids)],
			'turn_id':self.turn_id.id,
			'fecha_start':self.fecha_start,
			'fecha_end':self.fecha_end,
			'dias':self.dias}
		
		if not bool(self.turn_id):
			raise ValidationError('El turno debe ser mayor que 0.')

		if self.turn_id in self.env['hr.vacations'].search([('year_id','=', self.year_id.id)]).mapped('turn_id'):
			raise ValidationError('Ya existe ese turno de vacaciones.')
		

		self.env['hr.vacations'].create(vals)

		return {
			'name': 'Turnos de vacaciones',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.vacations',
			'target': 'current',
		}