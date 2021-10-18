# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

from odoo import fields, models,api
import datetime

class PhoneImportMap(models.Model):
	_name = 'phone.import.map'

	
	name = fields.Char(
		string='Header code',
	)
	
	import_map_line_ids = fields.One2many(
		string='Lines',
		comodel_name='phone.import.map.line',
		inverse_name='import_map_id',
		ondelete='cascade',
	)

	@api.multi
	def unlink(self):
		for map in self:
			if bool(map.import_map_line_ids):
				map.import_map_line_ids.unlink()
				
			res = super(PhoneImportMap, map).unlink()
			return res

	def phone_data_330_code(self,line):
		repeat_line_ids = self.env['phone.import.map.line']

		dict_data = {}
		
		initial = 0
		final = 0
		repeat_line_ids = self.import_map_line_ids.filtered('number_repeat')
		repeat = max(set(repeat_line_ids.mapped('number_repeat')))
		# longitud = longitud(repeat_line_ids)
		primera_vez = False
		for map_line in self.import_map_line_ids:

			length,decimal = map_line.length_decimal()
			
			final = initial + int(length)+int(decimal)
			
		
			if bool(map_line.number_repeat) and not bool(primera_vez):
				primera_vez = True
				repeat_array, initial, final = map_line.repeat_line_generate_array(repeat,repeat_line_ids,final,initial,line)
				dict_data['call_data'] = repeat_array
				
			if not bool(map_line.number_repeat):
				data = map_line.check_format_line(line[initial:final])
				dict_data[map_line.line_key] = data

			initial = final
			
		return dict_data
	
class PhoneImportMapLine(models.Model):
	_name = 'phone.import.map.line'	
	
	name = fields.Char(
		string='Description',
	)

	import_map_id = fields.Many2one(
		string='Import map id',
		comodel_name='phone.import.map',
	)
	
	length = fields.Char(
		string='Length',
	)

	value = fields.Char(
		string='Value',
	)

	position = fields.Integer(
		string='Position',
	)

	format_id = fields.Many2one(
		string='Format',
		comodel_name='phone.import.map.format',
		ondelete='cascade',
	)
	
	number_repeat = fields.Integer(
		string='Repeat',
	)

	line_key = fields.Char(
		string='Key',
	)
	
	def check_format_line(self,data):
		if bool(self.format_id.name.lower() == 'n'):
			data_format = int(data)
		elif bool(self.format_id.name.lower() == 'aaaammdd'):
			data_format = datetime.datetime.strptime(data, '%Y%m%d').date()
		else:
			data_format = str(data).strip()

		return data_format


	def length_decimal(self):
		if ',' in self.length:
			length = self.length.split(',')[0]
			decimal = self.length.split(',')[-1]
		else:
			length = self.length
			decimal = 0

		return length, decimal
	
	def repeat_line_generate_array(self,repeat,repeat_line_ids,final,initial, txt_line):
		repeat_array = []
		for line_repeat in range(repeat):
			line_dict = {}
			for repeat_line in repeat_line_ids:
				length,decimal = repeat_line.length_decimal()

				final = initial + int(length)+int(decimal)
				data_format = self.check_format_line(txt_line[initial:final])
				line_dict[repeat_line.line_key] = data_format

				initial = final
			repeat_array.append(line_dict)
		return repeat_array, initial, final
	
class PhoneImportMapFormat(models.Model):
	_name = 'phone.import.map.format'

	text_format = fields.Char(
		string='Format',
	)

	name = fields.Char(
		string='Type',
	)
	
	