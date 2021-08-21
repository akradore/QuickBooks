# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from openerp import api, fields, models, _
from datetime import datetime
from openerp.exceptions import UserError, AccessError
import csv
import base64
import io as StringIO
import xlrd
from openerp.tools import ustr
class import_bsl_wizard(models.TransientModel):
    _name="import.bsl.wizard"

    import_type = fields.Selection([
        ('csv','CSV File'),
        ('excel','Excel File')
        ],default="csv",string="Import File Type",required=True)
    file = fields.Binary(string="File",required=True)

    @api.multi
    def show_success_msg(self,counter,skipped_line_no):
        
        #to close the current active wizard        
        action = self.env.ref('sh_all_in_one_import.sh_import_bsl_action').read()[0]
        action = {'type': 'ir.actions.act_window_close'} 
        
        #open the new success message box    
        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False                                   
        context = dict(self._context or {})
        dic_msg = str(counter) + " Records imported successfully"
        if skipped_line_no:
            dic_msg = dic_msg + "\nNote:"
        for k,v in skipped_line_no.items():
            dic_msg = dic_msg + "\nRow No " + k + " " + v + " "
        context['message'] = dic_msg            
        
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
    def import_bsl_apply(self):

        absl_obj = self.env['account.bank.statement.line']
        #perform import lead
        if self and self.file and self.env.context.get("sh_abs_id",False):
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

                            if row[0] != '' and row[1] != '': 

                                final_date = None
                                cd = row[0]                
                                cd = str(datetime.strptime(cd, '%Y-%m-%d').date())
                                final_date = cd  
                                    
                                search_partner_id = False
                                if row[2] != '':
                                    search_partner = self.env["res.partner"].search([('name','=',row[2])], limit = 1)
                                    if search_partner:
                                        search_partner_id = search_partner.id
                                    else:
                                        skipped_line_no[str(counter)]= " - Partner not found. " 
                                        counter = counter + 1
                                        continue                                        
                                                            
                                vals={
                                    'date'         : final_date,
                                    'name'         : row[1],
                                    'partner_id'   : search_partner_id,
                                    'ref'          : row[3],
                                    'amount'       : row[4],
                                    'statement_id' : self.env.context.get("sh_abs_id")
                                    }
                                created_bsl = absl_obj.create(vals)
                                counter = counter + 1
                            else:
                                skipped_line_no[str(counter)] = " - Date or Label is empty. "  
                                counter = counter + 1      
                        except Exception as e:
                            skipped_line_no[str(counter)] = " - Value is not valid " + ustr(e)   
                            counter = counter + 1 
                            continue          
                             
                except Exception:
                    raise UserError(_("Sorry, Your csv file does not match with our format"))
                 
                if counter > 1:
                    completed_bsl = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_bsl, skipped_line_no)
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
                            
                            if sheet.cell(row,0).value != '' and sheet.cell(row,1).value != '': 
                                final_date = None
                                cd = sheet.cell(row,0).value                
                                cd = str(datetime.strptime(cd, '%Y-%m-%d').date())
                                final_date = cd  
                                    
                                search_partner_id = False
                                if sheet.cell(row,2).value != '':
                                    search_partner = self.env["res.partner"].search([('name','=',sheet.cell(row,2).value)], limit = 1)
                                    if search_partner:
                                        search_partner_id = search_partner.id
                                    else:
                                        skipped_line_no[str(counter)]= " - Partner not found. " 
                                        counter = counter + 1
                                        continue                                        
                                                            
                                vals={
                                    'date'         : final_date,
                                    'name'         : sheet.cell(row,1).value,
                                    'partner_id'   : search_partner_id,
                                    'ref'          : sheet.cell(row,3).value,
                                    'amount'       : sheet.cell(row,4).value,
                                    'statement_id' : self.env.context.get("sh_abs_id")
                                    }
                                created_bsl = absl_obj.create(vals)
                                counter = counter + 1
                            else:
                                skipped_line_no[str(counter)]=" - Date or Label is empty. "  
                                counter = counter + 1      
                        except Exception as e:
                            skipped_line_no[str(counter)] = " - Value is not valid " + ustr(e)   
                            counter = counter + 1 
                            continue   
       
                except Exception:
                    raise UserError(_("Sorry, Your excel file does not match with our format"))
 
                if counter > 1:
                    completed_lead = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_lead, skipped_line_no)
                    return res             