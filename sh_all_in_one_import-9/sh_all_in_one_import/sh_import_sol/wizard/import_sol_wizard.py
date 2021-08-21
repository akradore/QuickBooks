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

class import_sol_wizard(models.TransientModel):
    _name="import.sol.wizard"

    import_type = fields.Selection([
        ('csv','CSV File'),
        ('excel','Excel File')
        ],default="csv",string="Import File Type",required=True)
    file = fields.Binary(string="File",required=True)   
    product_by = fields.Selection([
        ('name','Name'),
        ('int_ref','Internal Reference'),
        ('barcode','Barcode')
        ],default="name", string = "Product By", required = True) 

    @api.multi
    def show_success_msg(self,counter,skipped_line_no):
        
        #to close the current active wizard        
        action = self.env.ref('sh_all_in_one_import.sh_import_sol_action').read()[0]
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
    def import_sol_apply(self):
        sol_obj = self.env['sale.order.line']
        #perform import lead
        if self and self.file and self.env.context.get('sh_so_id',False):
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
                                vals={}
                                
                                field_nm = 'name'
                                if self.product_by == 'name':
                                    field_nm = 'name'
                                elif self.product_by == 'int_ref':
                                    field_nm = 'default_code'
                                elif self.product_by == 'barcode':
                                    field_nm = 'barcode'
                                
                                search_product = self.env['product.product'].search([(field_nm,'=',row[0])], limit = 1)
                                if search_product:
                                    vals.update({'product_id' : search_product.id})
                                    
                                    if row[1] != '':
                                        vals.update({'name' : row[1] })
                                        
                                    if row[2] != '':
                                        vals.update({'product_uom_qty' : row[2] })
                                    else:
                                        vals.update({'product_uom_qty' : 1 })
                                    
                                    if row[3] in (None,"") and search_product.uom_id:
                                        vals.update({'product_uom' : search_product.uom_id.id })
                                    else:
                                        search_uom = self.env['product.uom'].search([('name','=',row[3] )], limit = 1) 
                                        if search_uom:
                                            vals.update({'product_uom' : search_uom.id })
                                        else:
                                            skipped_line_no[str(counter)]= " - Unit of Measure not found. " 
                                            counter = counter + 1
                                            continue
                                    
                                    if row[4] in (None,""):
                                        vals.update({'price_unit' : search_product.lst_price })
                                    else:
                                        vals.update({'price_unit' : row[4] })
                                        
                                    if row[5].strip() in (None,"") and search_product.taxes_id:
                                        vals.update({'tax_id' : [(6, 0, search_product.taxes_id.ids)]})
                                    else:
                                        taxes_list = []
                                        some_taxes_not_found = False
                                        for x in row[5].split(','):
                                            x = x.strip()
                                            if x != '':
                                                search_tax = self.env['account.tax'].search([('name','=',x)], limit = 1)
                                                if search_tax:
                                                    taxes_list.append(search_tax.id)
                                                else:
                                                    some_taxes_not_found = True
                                                    skipped_line_no[str(counter)]= " - Taxes " + x +  " not found. "                                                 
                                                    break  
                                        if some_taxes_not_found:
                                            counter = counter + 1
                                            continue
                                        else:
                                            vals.update({'tax_id' : [(6, 0, taxes_list)]})
                                        
                                else:
                                    skipped_line_no[str(counter)]= " - Product not found. " 
                                    counter = counter + 1 
                                    continue
                                
                                vals.update({'order_id' : self.env.context.get('sh_so_id')})
                                
                                created_sol = sol_obj.create(vals)
                                counter = counter + 1
                            
                            else:
                                skipped_line_no[str(counter)] = " - Product is empty. "  
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
                            
                            if sheet.cell(row,0).value != '': 
                                vals={}
                                
                                field_nm = 'name'
                                if self.product_by == 'name':
                                    field_nm = 'name'
                                elif self.product_by == 'int_ref':
                                    field_nm = 'default_code'
                                elif self.product_by == 'barcode':
                                    field_nm = 'barcode'
                                
                                search_product = self.env['product.product'].search([(field_nm,'=',sheet.cell(row,0).value )], limit = 1)
                                if search_product:
                                    vals.update({'product_id' : search_product.id})
                                    
                                    if sheet.cell(row,1).value != '':
                                        vals.update({'name' : sheet.cell(row,1).value })
                                        
                                    if sheet.cell(row,2).value != '':
                                        vals.update({'product_uom_qty' : sheet.cell(row,2).value })
                                    else:
                                        vals.update({'product_uom_qty' : 1 })
                                    
                                    if sheet.cell(row,3).value in (None,"") and search_product.uom_id:
                                        vals.update({'product_uom' : search_product.uom_id.id })
                                    else:
                                        search_uom = self.env['product.uom'].search([('name','=',sheet.cell(row,3).value )], limit = 1) 
                                        if search_uom:
                                            vals.update({'product_uom' : search_uom.id })
                                        else:
                                            skipped_line_no[str(counter)]= " - Unit of Measure not found. " 
                                            counter = counter + 1
                                            continue
                                    
                                    if sheet.cell(row,4).value in (None,""):
                                        vals.update({'price_unit' : search_product.lst_price })
                                    else:
                                        vals.update({'price_unit' : sheet.cell(row,4).value })
                                        
                                    if sheet.cell(row,5).value.strip() in (None,"") and search_product.taxes_id:
                                        vals.update({'tax_id' : [(6, 0, search_product.taxes_id.ids)]})
                                    else:
                                        taxes_list = []
                                        some_taxes_not_found = False
                                        for x in sheet.cell(row,5).value.split(','):
                                            x = x.strip()
                                            if x != '':
                                                search_tax = self.env['account.tax'].search([('name','=',x)], limit = 1)
                                                if search_tax:
                                                    taxes_list.append(search_tax.id)
                                                else:
                                                    some_taxes_not_found = True
                                                    skipped_line_no[str(counter)]= " - Taxes " + x +  " not found. "                                                 
                                                    break  
                                        if some_taxes_not_found:
                                            counter = counter + 1
                                            continue
                                        else:
                                            vals.update({'tax_id' : [(6, 0, taxes_list)]})
                                        
                                else:
                                    skipped_line_no[str(counter)]= " - Product not found. " 
                                    counter = counter + 1 
                                    continue
                                
                                vals.update({'order_id' : self.env.context.get('sh_so_id')})
                                
                                created_sol = sol_obj.create(vals)
                                counter = counter + 1
                            
                            else:
                                skipped_line_no[str(counter)] = " - Product is empty. "  
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