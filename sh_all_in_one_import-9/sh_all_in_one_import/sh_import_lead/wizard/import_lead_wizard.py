# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from openerp import api, fields, models, _
from datetime import datetime
from openerp.exceptions import UserError, AccessError
import csv
import base64
import io as StringIO
import xlrd

class import_lead_wizard(models.TransientModel):
    _name="import.lead.wizard"

    import_type = fields.Selection([
        ('csv','CSV File'),
        ('excel','Excel File')
        ],default="csv",string="Import File Type",required=True)
    file = fields.Binary(string="File",required=True)

    
    @api.multi
    def show_success_msg(self,counter,skipped_line_no):
        
        #to close the current active wizard        
        action = self.env.ref('sh_all_in_one_import.sh_import_lead_action').read()[0]
        action = {'type': 'ir.actions.act_window_close'} 
        
        #open the new success message box    
        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False                                   
        context = dict(self._context or {})
        dic_msg = '\n'.join("{}: {}".format(k, v) for k, v in skipped_line_no.items())
        context['message'] = str(counter) + " Leads created successfully " + str(dic_msg)
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
            }   

    
    @api.multi
    def import_lead_apply(self):

        crm_lead_obj = self.env['crm.lead']
        #perform import lead
        if self and self.file:
            #For CSV
            if self.import_type == 'csv':
                counter = 1
                skipped_line_no = {}
                try:
                    file = str(base64.decodestring(self.file).decode('utf-8'))
                    myreader = csv.reader(file.splitlines())
                    skip_header=True
                    
                    for row in myreader:
                        try:
                            if skip_header:
                                skip_header=False
                                counter = counter + 1
                                continue
                            if row[0] != '': 
                                
                                search_state_id = False
                                if row[5] != '':
                                    search_state = self.env['res.country.state'].search([('name','=',row[5])], limit = 1)
                                    if search_state:
                                        search_state_id = search_state.id
                                    else:
                                        skipped_line_no[str(counter)]= " - State not found. " 
                                        counter = counter + 1    
                                        continue
                                search_country_id = False
                                if row[7] != '':
                                    search_country = self.env["res.country"].search([('name','=',row[7])], limit = 1)
                                    if search_country:
                                        search_country_id = search_country.id
                                    else:
                                        skipped_line_no[str(counter)]= " - Country not found. " 
                                        counter = counter + 1
                                        continue
                                search_user_id = False
                                if row[12] != '':
                                    search_user = self.env["res.users"].search([('name','=',row[12])], limit = 1)
                                    if search_user:
                                        search_user_id = search_user.id
                                    else:
                                        skipped_line_no[str(counter)]= " - Salesperson not found. " 
                                        counter = counter + 1
                                        continue                                        
                                                           
                                vals={
                                    'name'          : row[0],
                                    'partner_name'  : row[1],
                                    'street'        : row[2],
                                    'street2'       : row[3],
                                    'city'          : row[4],
                                    'state_id'      : search_state_id,
                                    'zip'           : row[6],
                                    'country_id'    : search_country_id,
                                    'email_from'    : row[8],
                                    'function'      : row[9],
                                    'phone'         : row[10],
                                    'mobile'        : row[11],
                                    'user_id'       : search_user_id,
                                    'description'   : row[13],
                                    'type'          : 'lead',
                                    }
                                created_lead = crm_lead_obj.create(vals)
                                counter = counter + 1
                            else:
                                skipped_line_no[str(counter)]=" - Lead name is empty. "  
                                counter = counter + 1      
                        except Exception:
                            skipped_line_no[str(counter)]=" - Value is not valid. "   
                            counter = counter + 1 
                            continue          
                            
                except Exception:
                    raise UserError(_("Sorry, Your csv file does not match with our format"))
                
                if counter > 1:
                    completed_lead = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_lead, skipped_line_no)
                    return res

            
            #For Excel
            if self.import_type == 'excel':
                counter = 1
                skipped_line_no = {}                  
                try:
                    wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
                    sheet = wb.sheet_by_index(0)     
                    skip_header = True    
                    for row in range(sheet.nrows):
                        try:
                            if skip_header:
                                skip_header = False
                                counter = counter + 1
                                continue
                            if sheet.cell(row,0).value != '':                                    
                                
                                search_state_id = False
                                if sheet.cell(row,5).value != '':
                                    search_state = self.env['res.country.state'].search([('name','=',sheet.cell(row,5).value)], limit = 1)
                                    if search_state:
                                        search_state_id = search_state.id
                                    else:
                                        skipped_line_no[str(counter)]= " - State not found. " 
                                        counter = counter + 1    
                                        continue
                                search_country_id = False
                                if sheet.cell(row,7).value != '':
                                    search_country = self.env["res.country"].search([('name','=',sheet.cell(row,7).value)], limit = 1)
                                    if search_country:
                                        search_country_id = search_country.id
                                    else:
                                        skipped_line_no[str(counter)]= " - Country not found. " 
                                        counter = counter + 1
                                        continue
                                search_user_id = False
                                if sheet.cell(row,12).value != '':
                                    search_user = self.env["res.users"].search([('name','=',sheet.cell(row,12).value)], limit = 1)
                                    if search_user:
                                        search_user_id = search_user.id
                                    else:
                                        skipped_line_no[str(counter)]= " - Salesperson not found. " 
                                        counter = counter + 1
                                        continue                              
                                vals={
                                    'name'          : sheet.cell(row,0).value,
                                    'partner_name'  : sheet.cell(row,1).value,
                                    'street'        : sheet.cell(row,2).value,
                                    'street2'       : sheet.cell(row,3).value,
                                    'city'          : sheet.cell(row,4).value,
                                    'state_id'      : search_state_id,
                                    'zip'           : sheet.cell(row,6).value,
                                    'country_id'    : search_country_id,
                                    'email_from'    : sheet.cell(row,8).value,
                                    'function'      : sheet.cell(row,9).value,
                                    'phone'         : sheet.cell(row,10).value,
                                    'mobile'        : sheet.cell(row,11).value,
                                    'user_id'       : search_user_id,
                                    'description'   : sheet.cell(row,13).value,
                                    'type'          : 'lead',
                                    }
                                created_lead = crm_lead_obj.create(vals)
                                counter = counter + 1
                            else:
                                skipped_line_no[str(counter)]=" - Lead name is empty. "  
                                counter = counter + 1      
                        except Exception:
                            skipped_line_no[str(counter)]=" - Value is not valid. "   
                            counter = counter + 1 
                            continue  
      
                except Exception:
                    raise UserError(_("Sorry, Your excel file does not match with our format"))

                if counter > 1:
                    completed_lead = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_lead, skipped_line_no)
                    return res             