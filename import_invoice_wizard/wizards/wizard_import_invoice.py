# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-

from docutils.nodes import problematic
import logging
import os
import base64
import io
import csv
import urllib
from itertools import count

from odoo import api, models, fields
from odoo.exceptions import ValidationError
import datetime


_logger = logging.getLogger(__name__)


class WizardImportInvoice(models.TransientModel):
    _name = "wizard.import.invoice"
    
    file_type = fields.Selection(
        selection=[
            ('csv', 'Archivo CSV'),
        ],
        default="csv",
        required=True,
        string="Tipo de archivo"
    )

    file_data = fields.Binary('Archivo', required=True)

    date_invoice = fields.Date(
        string='Fecha factura',
        default=fields.Date.context_today,
    )

    def show_import_invocies(self,invoice_ids):
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
        decoded_data = base64.decodebytes(self.file_data)
        csv_file = io.TextIOWrapper(io.BytesIO(decoded_data), encoding='utf-8')
        csv_raw = csv.DictReader(csv_file, delimiter=';')
        row_count = sum(1 for row in csv_raw)
        csv_file = io.TextIOWrapper(io.BytesIO(decoded_data), encoding='utf-8')
        csv_raw = csv.DictReader(csv_file, delimiter=';')
        invoice_ids = self.import_invoice(csv_raw,row_count)
        action = self.show_import_invocies(invoice_ids)
        return action

    
    def import_invoice(self, csv, row_count):
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']

        invoice_ids = []
        n_line = 0
        n_errores = 0
        error = ''
        N_FECHA =1
        for i in range(len(csv.fieldnames)-1):
            name = csv.fieldnames[i]
            if name == "Fecha":
                name = "%s_%i" % (name, N_FECHA)
                N_FECHA = N_FECHA+1
                csv.fieldnames[i] = name
                csv._fieldnames[i] = name

        for line in csv:
            dict_line = dict(line)
            
            #variables for clean data.
            """
            - Fecha_1: fecha del surtidor
            - Fecha_2: fecha de la factura
            """
            date_factura = dict_line.get('Fecha_2', '').strip()
            date_surtidor = dict_line.get('Fecha_1', '').strip()
            pump = dict_line.get('Surtidor', '').strip()
            product_name = dict_line.get('Producto', '').strip()
            price = dict_line.get('Precio', '').strip().replace(',', '.')
            discount = dict_line.get('Descuento', '').strip().replace(',','.')
            liters = dict_line.get('Litros', '').strip().replace(',', '.')
            amount_untaxed = dict_line.get('Base_imponible', '').strip().replace(',', '.')
            total = dict_line.get('Montante', '').strip().replace(',', '.')
            registration = dict_line.get('Matricula', '').strip()
            payment_type = dict_line.get('Tipo_pago', '').strip()
            payment_mode = dict_line.get('Modo_pago', '').strip()
            bin = dict_line.get('BIN', '').strip()
            card = dict_line.get('Tarjeta', '').strip()
            state = dict_line.get('Estado', '').strip()
            document_type = dict_line.get('Tipo_documento', '').strip()
            serie = dict_line.get('Serie', '').strip()
            number = dict_line.get('Numero', '').strip()

            client_id = dict_line.get('Cliente_id', '').strip()
            name = dict_line.get('Nombre', '').strip()
            vat = dict_line.get('Nif', '').strip()
            street = dict_line.get('Direccion', '').strip()
            city = dict_line.get('Poblacion', '').strip()
            city_state = dict_line.get('Provincia', '').strip()
            cp = dict_line.get('CP', '').strip()
            partner_default_code = dict_line.get('id_externo', '').strip()
            card_code = dict_line.get('Codigo_tarjeta', '').strip()
            card_number = dict_line.get('numero_tarjeta', '').strip()

            n_line = n_line + 1

            if state in ['CANCELADA', 'cancelada'] and \
                 document_type in ['SIN DOCUMENTO','sin documento']:
                continue

            product_id = self.get_product(product_name)
            if not product_id:
                error = 'Producto no encontrado'
                n_errores = n_errores +1
                self.create_error_line(error,n_line)
                continue
            product_id = product_id[0]
            
            partner_id = self.get_partner(partner_default_code)
            if not partner_id:
                partner_id = self.env.ref('atzeneta_import_invoice_wizard.res_partner_surtidor_gasolina')
            partner_id = partner_id[0]

            account_id = self.env.ref('atzeneta_import_invoice_wizard.account_analytic_account_gasoil')
            if not bool(account_id):
                error = 'Cuenta analçitica de Gasolinera no encontrada'
                n_errores = n_errores+1
                self.create_error_line(error,n_line) 
                continue

            account_id = account_id[0]

            journal_id = self.get_journal(account_id)
            if not bool(journal_id):
                error = 'Diario no encontrado'
                n_errores = n_errores +1
                self.create_error_line(error,n_line) 
                
            journal_id = journal_id[0]

            tax_id = self.env.ref('l10n_es.1_account_tax_template_s_iva21b')
            if bool(tax_id):
                tax_id = tax_id[0]

            line_descripction = '{}'.format(product_id.display_name)
            if registration:
                line_descripction += '\n Matrícula: {}'.format(registration)
            if card_code:
                line_descripction += '\n Tarjeta: {}'.format(card_code)
            if date_surtidor:
                line_descripction += '\n fecha de repostaje: {}'.format(date_surtidor)

            origin = '{}{}'.format(serie,number)

            invoice_state = 'draft'
            move_name = False
            if document_type in ['FACTURA','factura']:
                invoice_state = 'paid'
                move_name = origin
            if payment_type.lower() == 'impagada':
                invoice_state = 'cancel'

            
            liters = float(liters)
            total = float(total)
            unit_price = self.compute_unit_price(liters,total)
            
            payment_id = self.get_payment(payment_type)

            invoice_line_values = self.complete_invoice_line_values(line_descripction,unit_price,liters,account_id,tax_id, product_id)
            
            fail_try = False
            try:
                format_date = datetime.datetime.strptime(date_factura, '%d/%m/%Y').date()
            except Exception:
                fail_try = True
                
            if fail_try:

                try:
                    format_date = datetime.datetime.strptime(date_surtidor, '%d/%m/%Y').date()
                except Exception:
                    format_date = self.date_invoice   

            partner_invoice_id = invoice_obj.search([
                ('partner_id', '=', partner_id.id),
                ('state','=', 'draft'),
                ('type','=','out_invoice'),
            ])
            if bool(partner_invoice_id) and not bool(invoice_state == 'cancel'):
                try:
                    invoice_line_values['invoice_id'] = partner_invoice_id.id
                    invoice_line_id = invoice_line_obj.create(invoice_line_values)
                    invoice_id = invoice_line_id.invoice_id
                    _logger.info("Created invoice line for line {} of {}".format(n_line, row_count))
                    invoice_ids.append(invoice_id.id)
                except Exception as e:
                    try:
                        error = '({}'.format(str(e).split('(')[-1])
                    except Exception:
                        error = e
                    n_errores = n_errores +1
                    self.create_error_line(error,n_line) 
                    continue

                self.env.cr.commit()
                continue

            invoice_values = self.complete_invoice_values(format_date, payment_id, journal_id,invoice_state, partner_id, product_id,invoice_line_values, origin,self.date_invoice)

            try:
                if bool(move_name):
                    invoice_number = invoice_obj.search([('number','=',move_name)])
                    if not bool(invoice_number):
                        invoice_values['move_name'] = move_name
                        invoice_values['number'] = move_name
                invoice_id = invoice_obj.create(invoice_values)
                _logger.info("Created invoice for line {} of {}".format(n_line, row_count))
                invoice_ids.append(invoice_id.id)
            except Exception as e:
                try:
                    error = '({}'.format(str(e).split('(')[-1])
                except Exception:
                    error = e
                n_errores = n_errores +1
                self.create_error_line(error,n_line) 
                continue

            self.env.cr.commit()
        
        self.send_toast(n_errores)
        return invoice_ids
    
    def send_toast(self, n_errores):
        message = 'Importación terminada'
        if bool(n_errores):
            message = 'Importación terminada, se han descartado' \
                ' {} líneas con errores'.format(n_errores)
        self.env.user.notify_default(message)

    def create_error_line(self, error, n_line):
        errorobj = self.env['invoice.import.error']
        errorobj.sudo().create({
            'import_date':self.date_invoice,
            'line_number': n_line,
            'description': error,
        })
        self.env.cr.commit()

    def compute_unit_price(self, liters, total):
        price_unit = 0.0
        
        if not bool(total) or not bool(liters):
            return price_unit
        
        price_unit = (total / 1.21) / liters

        return price_unit
    
    def get_payment(self, payment):
        dict_payment_xml_ids = {
            'medio_de_pago': 'atzeneta_import_invoice_wizard.account_payment_mode_medio_de_pago',
            'credito': 'atzeneta_import_invoice_wizard.account_payment_mode_credito',
            'dinero/bono': 'atzeneta_import_invoice_wizard.account_payment_mode_dinero_bono',
            'impagada': 'atzeneta_import_invoice_wizard.account_payment_mode_impagada',
            'tarjeta': 'atzeneta_import_invoice_wizard.account_payment_mode_tarjeta',
        }
        payment_xml_id = dict_payment_xml_ids.get(payment.lower())
        payment_id = self.env.ref(payment_xml_id)
        return payment_id
        
    def complete_invoice_line_values(self, name, price_unit, liters, analytic_id, tax_id, product_id,):
        if product_id.property_account_income_id:
            account_id = product_id.property_account_income_id
        else:
            account_id = self.env.ref('l10n_es.account_group_702')

        return {
            'product_id': product_id.id,
            'price_unit': float(price_unit),
            'quantity': float(liters),
            'uom_id': product_id.uom_id.id,
            'name': name,
            'account_analytic_id': analytic_id.id,
            'account_id': account_id.id,
            'invoice_line_tax_ids': [(6,0,tax_id.ids)] if tax_id else False,
        }
        
    def complete_invoice_values(self, date, payment_id, journal_id, state, partner_id, product_id, invoice_line_values, origin,widget_date):
        if journal_id.currency_id:
            currency_id = journal_id.currency_id
        elif product_id.currency_id:
            currency_id = product_id.currency_id
        else:
            currency_id = self.env.ref('base.EUR')
        
        account_position_id = False
        if partner_id.property_account_position_id:
            account_position_id = partner_id.property_account_position_id.id

        return {
            'company_id': journal_id.company_id.id or False,
            'import_date': widget_date,
            'currency_id': journal_id.currency_id.id or False,
            'journal_id': journal_id.id,
            'reference_type': 'none',
            'date_invoice': date,
            'payment_mode_id': payment_id.id or False, #modo_pago
            'partner_id': partner_id.id,
            'type': 'out_invoice',
            'state': state,
            'fiscal_position_id': account_position_id,
            'invoice_line_ids': [(0, 0, invoice_line_values)],
            'origin': origin,
        }

    def get_journal(self, account_id):
        return self.env['account.journal'].search([
            ('type','=','sale'),
            ('account_analytic_id','=',account_id.id)])

    def get_partner(self, default_code):
        return self.env['res.partner'].search([('ref','=',default_code)])

    def get_product(self, product_name):
        if product_name == 'GasoleoA':
            product_id = self.env.ref('atzeneta_import_invoice_wizard.product_product_gasoleo_a')
        elif product_name == 'GasoleoB':
            product_id = self.env.ref('atzeneta_import_invoice_wizard.product_product_gasoleo_b')
        elif product_name == 'SinPlomo95':
            product_id = self.env.ref('atzeneta_import_invoice_wizard.product_product_gasolina_95')
        return product_id