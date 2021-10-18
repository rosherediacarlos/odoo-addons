# -*- coding: utf-8 -*-
# (c) 2021 Praxya - Christian Doñate <cdonate@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, exceptions, api, _


class HrVacationsReportWizard(models.TransientModel):
    _name = "hr.vacations.report.wizard"

    turnos_vacaciones = fields.Many2many('hr.vacations')

    @api.model
    def default_get(self, fields):
        res = super(HrVacationsReportWizard, self).default_get(fields)
        res.update({'turnos_vacaciones':self._context['active_ids']})
        return res

    def crear_informe(self):
        return {'type': 'ir.actions.report','report_name': 'hr_vacations.hr_vacations_report_view','report_type':"qweb-pdf"}