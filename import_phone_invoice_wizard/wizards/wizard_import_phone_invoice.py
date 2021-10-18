# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

import logging
import base64
import io
from io import StringIO
from datetime import date

from odoo import api, models, fields,_
from odoo.exceptions import ValidationError
import datetime


_logger = logging.getLogger(__name__)


class WizardImportPhoneInvoice(models.TransientModel):
	_name = "wizard.import.phone.invoice"
	
	#for create Detall invoice add "detall" and program "create_phone_detall_invoice"
	invoice_type = fields.Selection(
		selection=[
			('simple', 'Simple Invoice'),
		],
		default="simple",
		required=True,
		string="Type of invoice"
	)

	file_data = fields.Binary('File', required=True)
	
	date_invoice = fields.Date(
		string='invoice date',
		default=fields.Date.context_today,
	)

	def show_import_invocies(self,invoice_ids):
		"""
		this function need invoice_ids (ids list)
		to launch an Odoo action for the model 'account.invoice' to show the invoices have been created
		"""
		action = self.env.ref('account.action_invoice_tree1').read()[0]
		if len(invoice_ids) > 1:
			action['domain'] = [('id', 'in', tuple(invoice_ids))]
		elif len(invoice_ids) == 1:
			form_view = [(self.env.ref('account.invoice_form').id, 'form')]
			if 'views' in action:
				action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
			else:
				action['views'] = form_view
			action['res_id'] = invoice_ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action

	def start_import_invoice(self):
		"""
		This function is launched when pres import button
		"""
		decoded_data = base64.decodebytes(self.file_data)
		try:
			file = StringIO(decoded_data.decode('utf-8'))
		except Exception:
			file = StringIO(decoded_data.decode('iso-8859-1'))

		invoice_ids = self.import_invoice(file)
		action = self.show_import_invocies(invoice_ids.ids)

		return action

	def import_invoice(self, file):
		"""
		This function prepare file data for create invoices
		"""
		invoice_obj = self.env['account.invoice']
		phone_map_obj = self.env['phone.import.map']

		invoice_ids = invoice_obj

		dict_data = {}
		lines_data = []

		#variable for file lines
		lines = file.read().split("\r\n")

		#This variable is for get line phone for generte un diccionario grouping lines with mobile phone number
		actual_phone = 0

		for line in lines:
			#Get code for line
			if bool(line[0:3]):
				code = int(line[0:3])
			else:
				 continue

			#search map for import line data
			phone_map_id = phone_map_obj.search([('name','=',code)])
			
			if not bool(phone_map_id):
				continue
			#Check if line start with number 3
			if bool(line[0] == '3'):
				phone = line[37:46]
		
				actual_phone = phone

				lines_data.append(phone_map_id.phone_data_330_code(line))

				if not dict_data.get(actual_phone,False):
					dict_data.update({
						actual_phone: {code: lines_data}
					})
				else:
					if not dict_data.get(actual_phone).get(code,False):
						dict_data.get(actual_phone).update({
							code: lines_data
						})
					else:
						dict_data.get(actual_phone).get(code).append(lines_data)

				lines_data = []

		#Check diferent type of invoice
		if bool(self.invoice_type == 'simple'):
			invoice_ids = self.create_phone_invoice(dict_data)
		elif bool(self.invoice_type == 'detall'):
			invoice_ids = self.create_phone_detall_invoice(dict_data)

		return invoice_ids

	def get_partner_phone_obj(self,phone):
		"""
		Get the rate and partner for each mobil phone
		"""
		partner_phone_obj = self.env['res.partner.phone']
		
		partner_phone_id = partner_phone_obj.search([('phone','=', phone)])
		return partner_phone_id

	def generate_invoice_lines(self,partner_phone_id,invoice_data):
		"""
		Generate a invoice lines
			- the first line is used as a product the rate selected in the list of rates and telephones (res.partner, phone) of the 'res.partner'.
			- The following line has a generic product, and the price of this product is determined by record 340 of the txt file issued by Telefonica.
		"""
		product_id = partner_phone_id.product_id
		tax_id = self.env.ref('l10n_es.1_account_tax_template_s_iva21b')
		account_analytic_id = self.env.ref('atzeneta_import_invoice_wizard.account_analytic_account_phone_and_service')

		if product_id.property_account_income_id:
			account_id = product_id.property_account_income_id
		else:
			account_id = self.env.ref('l10n_es.1_account_common_7000')
		
		product_line = {
			'product_id': product_id.id,
			'price_unit': float(product_id.list_price),
			'quantity': float(1.0),
			'uom_id': product_id.uom_id.id,
			'name': product_id.display_name,
			'account_analytic_id': account_analytic_id.id if account_analytic_id else False,
			'account_id': account_id.id if account_id else False,
			'invoice_line_tax_ids': [(6,0,tax_id.ids)] if tax_id else False,
		}
		lines = [(0,0,product_line)]
		amount = 0.0
		for line in invoice_data:
			if bool(line == 330):
				continue
			import_map_id = self.env['phone.import.map'].search([('name','=',str(line))])
			import_map_line_id = import_map_id.import_map_line_ids.filtered(lambda x:x.line_key == 'amount')
			amount_ranges = import_map_line_id.length.split(',')
			for data_line in invoice_data[line]:
				for call_data_line in data_line.get('call_data'):
					string_amount = call_data_line.get('amount')[:int(amount_ranges[0])] + '.' + call_data_line.get('amount')[int(amount_ranges[0]):]
					amount += float(string_amount)

		if bool(amount):
			product_id = self.env.ref('atzeneta_import_phone_invoice_wizard.product_product_servicio_llamdas')
			extra_line = {
				'product_id': product_id.id,
				'price_unit': amount,
				'quantity': float(1.0),
				'uom_id': product_id.uom_id.id,
				'name': product_id.display_name,
				'account_analytic_id': account_analytic_id.id if account_analytic_id else False,
				'account_id': account_id.id if account_id else False,
				'invoice_line_tax_ids': [(6,0,tax_id.ids)] if tax_id else False,
			}
			lines.append((0,0,extra_line))
		
		return lines

	def generate_line_section_phone(self,phone):
		"""
		This function creates a section invoice.line to separate the billable linmes from each phone line
		"""
		line = {
			'display_type': 'line_section',
			'price_unit': float(0.0),
			'quantity': float(0.0),
			'name': _('Invoice Phone:').format(phone),
		}
		return line

	def generate_header_invoice(self,partner_id, product_id):
		"""
		Generate dict with the basic and required fields for 'acccount.invoice'
		"""
		journal_id = self.env.ref('atzeneta_import_phone_invoice_wizard.account_jorunal_customer_telefonica')
		payment_mode_id = self.env.ref('atzeneta_import_invoice_wizard.account_payment_mode_credito')

		if not bool(partner_id) or not bool(product_id):
			return False
		
		return {
			'company_id': partner_id.company_id.id,
			'import_date': date.today(),
			'currency_id': product_id.currency_id.id if product_id.currency_id else False,
			'journal_id': journal_id.id if journal_id else False,
			'reference_type': 'none',
			'date_invoice':  self.date_invoice if self.date_invoice else False,
			'date_due':  self.date_invoice if self.date_invoice else False,
			'payment_mode_id': payment_mode_id.id if payment_mode_id else False, #modo_pago
			'partner_id': partner_id.id,
			'type': 'out_invoice',
			'state': 'open',
			'fiscal_position_id': partner_id.property_account_position_id.id if partner_id.property_account_position_id else False,
		}

	def create_phone_detall_invoice(self,invoice_dict):
		"""
		This function is defined for inherit and create a detall invoice for "Telefonia txt file"
		Need that this function return invoice 'account.invoice' ids, becouse when finish read file and create invoices,
		show all created invoices for the read file.

		Exist function generate_header_invoice for generate a dictionary with the invoice data, 
		later can create 'account.invoice.line' with the detail data.
		"""
		invoice_obj = self.env['account.invoice']
		return invoice_obj

	def create_phone_invoice(self,invoice_dict):
		"""
		Function to create dict for simple 'account.invoice'
		"""
		#obj instances
		invoice_obj = self.env['account.invoice']
		invoice_ids = invoice_obj
		
		#variables
		invoice_sequence = 1
		for line in invoice_dict:
			invoice_data = invoice_dict.get(line)
			
			if not bool(invoice_data):
				continue
			
			partner_phone_id = self.get_partner_phone_obj(line)
			if not bool(partner_phone_id):
				continue
			
			partner_invoice_id = invoice_ids.filtered(lambda x: x.partner_id == partner_phone_id.partner_id)

			lines = self.generate_invoice_lines(partner_phone_id,invoice_data)
			if not bool(lines):
				continue
			
			lines.insert(0,(0,0,self.generate_line_section_phone(line)))

			if bool(partner_invoice_id):
				partner_invoice_id.update({'invoice_line_ids':lines})
			else:		
				invocie_dict = self.generate_header_invoice(partner_phone_id.partner_id,partner_phone_id.product_id)
				if not bool(invocie_dict):
					continue
			
				origin = ''
				if bool(invoice_data.get(330)[0]) and bool(invoice_data.get(330)[0].get('invoice_number')):
					origin = invoice_data.get(330)[0].get('invoice_number')

				invocie_dict.update({
					'invoice_line_ids': lines,
					'origin': origin
				})

				invoice_id = invoice_obj.create(invocie_dict)
				invoice_ids |= invoice_id
		return invoice_ids
