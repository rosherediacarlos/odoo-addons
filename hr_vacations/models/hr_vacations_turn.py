# -*- coding: utf-8 -*-
# (c) 2021 Praxya - Miquel March <mmarch@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, exceptions, api, _
from datetime import date


class HrVacationsYear(models.Model):
	_name = "hr.vacations.year"
	_description = 'Año'
	_rec_name = 'year'

	def _default_year(self):
		today = fields.Date.context_today(self)
		current_year = fields.Date.from_string(today).year
		return current_year

	year = fields.Integer(string='Año', default=lambda self: self._default_year())
	turn_ids = fields.One2many(
		string='Turnos',
		comodel_name='hr.vacations.turn',
		inverse_name='year_id',
		ondelete='cascade'
	)
	count_turns = fields.Integer(
		string='Numero de turnos',
		compute='compute_number_turns' )

	@api.multi
	def unlink(self):
		self.turn_ids.unlink()
		res = super(HrVacationsYear, self).unlink()
		return res

	@api.multi
	def name_get(self):
		res = []
		for record in self:
			res.append((record.id, "%s" % (record.year)))
		return res

	@api.depends('turn_ids')
	def compute_number_turns(self):
		for record in self:
			record.count_turns = len(turn_ids.ids)


class HrVacationsTurn(models.Model):
	_name = "hr.vacations.turn"
	_description = 'Turno'
	_rec_name = 'turno'

	year_id = fields.Many2one(string='Año',comodel_name='hr.vacations.year', ondelete='cascade')
	turno = fields.Integer(string='Turno')
	fecha_start = fields.Date(string='Fecha desde', default=date.today())
	fecha_end = fields.Date(string='Fecha hasta', default=date.today())
	dias = fields.Float(string='Días', compute="get_dias")

	@api.multi
	def name_get(self):
		res = []
		for record in self:
			res.append((record.id, "%s" % (record.turno)))
		return res

	@api.depends('fecha_start','fecha_end')
	def get_dias(self):
		for x in self:
			dias = 0
			if bool(x.fecha_end) and bool( x.fecha_start):
				dias = (x.fecha_end - x.fecha_start).days + 1
			x.dias = dias

	@api.multi
	def unlink(self):
		res = super(HrVacationsTurn, self).unlink()
		return res

	@api.model
	def create(self, vals):
		res = super(HrVacationsTurn, self).create(vals)
		return res

	@api.multi
	def write(self, vals):
		res = super(HrVacationsTurn, self).write(vals)
		return res