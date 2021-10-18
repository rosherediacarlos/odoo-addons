# -*- coding: utf-8 -*-
# (c) 2021 Praxya - Miquel March <mmarch@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, exceptions, api, _
from datetime import date


class HrVacations(models.Model):
	_name = "hr.vacations"
	
	def _default_year(self):
		today = fields.Date.context_today(self)
		current_year = fields.Date.from_string(today).year
		return current_year

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


	@api.multi
	def unlink(self):
		for linea in self:
			linea.env['hr.leave'].search([('turno_vacaciones_id', '=', linea.id)]).filtered(lambda x: x.employee_id.id in linea.employee_ids.ids).unlink()
		res = super(HrVacations, self).unlink()
		return res

	@api.model
	def create(self, vals):
		res = super(HrVacations, self).create(vals)
		leave_type = self.env.ref('hr_vacations.hr_leave_type_vacaciones')
		for empleado in vals.get('employee_ids')[0][2]:
			values = {
				'holiday_status_id':vals.get('tipo'),
				'turno':vals.get('turno'),
				'date_from':vals.get('fecha_start'),
				'date_to':vals.get('fecha_end'),
				'number_of_days':vals.get('dias'),
				'employee_id':empleado,
				'turno_vacaciones_id':res.id,
				'holiday_status_id': leave_type.id
			}
			self.env['hr.leave'].create(values)
		return res

	@api.multi
	def write(self, vals):
		res = super(HrVacations, self).write(vals)
		if self.employee_ids:
			for empleado in self.employee_ids:
				values = {'holiday_status_id':self.tipo.id,'turno':self.turno,'date_from':self.fecha_start,'number_of_days':self.dias,'date_to':self.fecha_end,'employee_id':empleado.id,'turno_vacaciones_id':self.id}
				ausencia_empleado = self.env['hr.leave'].search([('turno_vacaciones_id', '=', self.id),('employee_id', '=', empleado.id)])

				if ausencia_empleado:
					ausencia_empleado.write(values)
				else:
					self.env['hr.leave'].create(values)
		self.env['hr.leave'].search([('turno_vacaciones_id', '=', self.id)]).filtered(lambda x: x.employee_id.id not in self.employee_ids.ids).unlink()
		return res