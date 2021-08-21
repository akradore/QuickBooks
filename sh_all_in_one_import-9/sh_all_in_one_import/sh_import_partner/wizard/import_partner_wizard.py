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
import requests
import codecs

class import_partner_wizard(models.TransientModel):
    _name="import.partner.wizard"

    import_type = fields.Selection([
        ('csv','CSV File'),
        ('excel','Excel File')
        ],default="csv",string="Import File Type",required=True)
    file = fields.Binary(string="File",required=True)
    is_customer = fields.Boolean(string = "Is a Customer", default = True)
    is_supplier = fields.Boolean(string = "Is a Vendor")
    

    @api.multi
    def show_success_msg(self,counter,skipped_line_no):
        
        #to close the current active wizard        
        action = self.env.ref('sh_all_in_one_import.sh_import_partner_action').read()[0]
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
    def import_partner_apply(self):

        partner_obj = self.env['res.partner']
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

                            if row[1] != '': 
                                vals={}
                                
                                if row[5] != '':
                                    search_state = self.env['res.country.state'].search([('name','=',row[5])], limit = 1)
                                    if search_state:
                                        vals.update({'state_id' : search_state.id})
                                    else:
                                        skipped_line_no[str(counter)]= " - State not found. " 
                                        counter = counter + 1    
                                        continue
                                
                                if row[7] != '':
                                    search_country = self.env["res.country"].search([('name','=',row[7])], limit = 1)
                                    if search_country:
                                        vals.update({'country_id' : search_country.id})                                        
                                    else:
                                        skipped_line_no[str(counter)]= " - Country not found. " 
                                        counter = counter + 1
                                        continue   
                                
                                if row[13] != '' and row[0].strip() != 'Company':
                                    search_title = self.env["res.partner.title"].search([('name','=',row[13])], limit = 1)
                                    if search_title:
                                        vals.update({'title' : search_title.id})
                                    else:
                                        skipped_line_no[str(counter)]= " - Title not found. " 
                                        counter = counter + 1
                                        continue 
                                
                                vals.update({'function' : row[8]})
                                vals.update({'company_type' : 'person'}) 
                                if row[0].strip() == 'Company':
                                    vals.update({'company_type' : 'company'})   
                                    vals.pop('title', None)   
                                    vals.pop('function',None)                              
                                
                                if self.is_customer:
                                    vals.update({'customer' : True})
                                else:
                                    vals.update({'customer' : False})                                    
                                
                                if self.is_supplier:
                                    vals.update({'supplier' : True})
                                else:
                                    vals.update({'supplier' : False})   
                                    
                                    
                                if row[15].strip() not in (None,""):
                                    image_path = row[15].strip()
                                    if "http://" in image_path or "https://" in image_path:
                                        try:
                                            r = requests.get(image_path)
                                            if r and r.content:
                                                image_base64 = base64.encodestring(r.content) 
                                                vals.update({'image': image_base64})
                                            else:
                                                skipped_line_no[str(counter)] = " - URL not correct or check your image size. "                                            
                                                counter = counter + 1                                                
                                                continue
                                        except Exception as e:
                                            skipped_line_no[str(counter)] = " - URL not correct or check your image size " + ustr(e)   
                                            counter = counter + 1 
                                            continue                                              
                                        
                                    else:
                                        try:
                                            with open(image_path, 'rb') as image:
                                                image.seek(0)
                                                binary_data = image.read()
                                                image_base64 = codecs.encode(binary_data, 'base64')     
                                                if image_base64:
                                                    vals.update({'image': image_base64})
                                                else:
                                                    skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this user. "                                            
                                                    counter = counter + 1                                                
                                                    continue                                                                       
                                        except Exception as e:
                                            skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this user " + ustr(e)   
                                            counter = counter + 1 
                                            continue                                 

                                vals.update({
                                    'name'          : row[1],
                                    'street'        : row[2],
                                    'street2'       : row[3],
                                    'city'          : row[4],
                                    'zip'           : row[6],
                                    'phone'         : row[9],
                                    'mobile'        : row[10],
                                    'email'         : row[11],
                                    'website'       : row[12],
                                    'comment'       : row[14],
                                    })


                                partner_obj.create(vals)
                                counter = counter + 1
                            else:
                                skipped_line_no[str(counter)] = " - Name is empty. "  
                                counter = counter + 1      
                        except Exception as e:
                            skipped_line_no[str(counter)] = " - Value is not valid " + ustr(e)   
                            counter = counter + 1 
                            continue          
                             
                except Exception:
                    raise UserError(_("Sorry, Your csv file does not match with our format"))
                 
                if counter > 1:
                    completed_records = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_records, skipped_line_no)
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
                            
                            if sheet.cell(row,1).value != '': 
                                vals={}
                                
                                if sheet.cell(row,5).value != '':
                                    search_state = self.env['res.country.state'].search([('name','=',sheet.cell(row,5).value )], limit = 1)
                                    if search_state:
                                        vals.update({'state_id' : search_state.id})
                                    else:
                                        skipped_line_no[str(counter)]= " - State not found. " 
                                        counter = counter + 1    
                                        continue
                                
                                if sheet.cell(row,7).value != '':
                                    search_country = self.env["res.country"].search([('name','=',sheet.cell(row,7).value)], limit = 1)
                                    if search_country:
                                        vals.update({'country_id' : search_country.id})                                        
                                    else:
                                        skipped_line_no[str(counter)]= " - Country not found. " 
                                        counter = counter + 1
                                        continue   
                                
                                if sheet.cell(row,13).value != '' and sheet.cell(row,0).value != 'Company':
                                    search_title = self.env["res.partner.title"].search([('name','=',sheet.cell(row,13).value)], limit = 1)
                                    if search_title:
                                        vals.update({'title' : search_title.id})
                                    else:
                                        skipped_line_no[str(counter)]= " - Title not found. " 
                                        counter = counter + 1
                                        continue 
                                
                                vals.update({'function' : sheet.cell(row,8).value})
                                vals.update({'company_type' : 'person'}) 
                                if sheet.cell(row,0).value == 'Company':
                                    vals.update({'company_type' : 'company'})   
                                    vals.pop('title', None)   
                                    vals.pop('function',None)                              
                                
                                if self.is_customer:
                                    vals.update({'customer' : True})
                                else:
                                    vals.update({'customer' : False})                                    
                                
                                if self.is_supplier:
                                    vals.update({'supplier' : True})
                                else:
                                    vals.update({'supplier' : False})   
                                    
                                    
                                if sheet.cell(row,15).value not in (None,""):
                                    image_path = sheet.cell(row,15).value
                                    if "http://" in image_path or "https://" in image_path:
                                        try:
                                            r = requests.get(image_path)
                                            if r and r.content:
                                                image_base64 = base64.encodestring(r.content) 
                                                vals.update({'image': image_base64})
                                            else:
                                                skipped_line_no[str(counter)] = " - URL not correct or check your image size. "                                            
                                                counter = counter + 1                                                
                                                continue
                                        except Exception as e:
                                            skipped_line_no[str(counter)] = " - URL not correct or check your image size " + ustr(e)   
                                            counter = counter + 1 
                                            continue                                              
                                        
                                    else:
                                        try:
                                            with open(image_path, 'rb') as image:
                                                image.seek(0)
                                                binary_data = image.read()
                                                image_base64 = codecs.encode(binary_data, 'base64')     
                                                if image_base64:
                                                    vals.update({'image': image_base64})
                                                else:
                                                    skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this user. "                                            
                                                    counter = counter + 1                                                
                                                    continue                                                                       
                                        except Exception as e:
                                            skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this user " + ustr(e)   
                                            counter = counter + 1 
                                            continue                                 

                                vals.update({
                                    'name'          : sheet.cell(row,1).value,
                                    'street'        : sheet.cell(row,2).value,
                                    'street2'       : sheet.cell(row,3).value,
                                    'city'          : sheet.cell(row,4).value,
                                    'zip'           : sheet.cell(row,6).value,
                                    'phone'         : sheet.cell(row,9).value,
                                    'mobile'        : sheet.cell(row,10).value,
                                    'email'         : sheet.cell(row,11).value,
                                    'website'       : sheet.cell(row,12).value,
                                    'comment'       : sheet.cell(row,14).value,
                                    })


                                partner_obj.create(vals)
                                counter = counter + 1
                            else:
                                skipped_line_no[str(counter)] = " - Name is empty. "  
                                counter = counter + 1      
                        except Exception as e:
                            skipped_line_no[str(counter)] = " - Value is not valid " + ustr(e)   
                            counter = counter + 1 
                            continue          
                             
                except Exception:
                    raise UserError(_("Sorry, Your excel file does not match with our format"))
                 
                if counter > 1:
                    completed_records = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_records, skipped_line_no)
                    return res