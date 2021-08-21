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

   
class import_reordering_rules_wizard(models.TransientModel):
    _name="import.reordering.rules.wizard"

    import_type = fields.Selection([
        ('csv','CSV File'),
        ('excel','Excel File')
        ],default="csv",string="Import File Type",required=True)
    file = fields.Binary(string="File",required=True)   
    
    method = fields.Selection([
        ('create','Create New Reordering Rules'),
        ('update','Update Existing Reordering Rules')
        ],default = "create", string = "Method", required = True)
    
    product_by = fields.Selection([
        ('name','Name'),
        ('int_ref','Internal Reference'),
        ('barcode','Barcode')
        ],default="name", string = "Product By", required = True)     

    @api.multi
    def show_success_msg(self,counter,skipped_line_no):
        
        #to close the current active wizard        
        action = self.env.ref('sh_all_in_one_import.sh_import_reordering_rules_action').read()[0]
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
    def import_reordering_rule_apply(self):
        reordering_rule_obj = self.env['stock.warehouse.orderpoint']
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

                            if row[0] not in (None,""): 
                                vals={}
                                
                                field_nm = 'name'
                                if self.product_by == 'name':
                                    field_nm = 'name'
                                elif self.product_by == 'int_ref':
                                    field_nm = 'default_code'
                                elif self.product_by == 'barcode':
                                    field_nm = 'barcode'
                                
                                search_product = self.env['product.product'].search([(field_nm,'=',row[0])], limit = 1)
                                if search_product and search_product.type == 'product':
                                    vals.update({'product_id' : search_product.id})
                                    
                                    if row[1] not in (None,""):
                                        vals.update({'product_min_qty' : row[1] })
                                    else:
                                        vals.update({'product_min_qty' : 0.0 })                                        
                                        
                                    if row[2] not in (None,""):
                                        vals.update({'product_max_qty' : row[2] })
                                    else:
                                        vals.update({'product_max_qty' : 0.0 })
                                    
                                    if row[3] not in (None,""):
                                        vals.update({'qty_multiple' : row[3] })
                                    else:
                                        vals.update({'qty_multiple' : 1.0 })
                                        
                                    if self.method == 'create':
                                        reordering_rule_obj.create(vals)
                                    else:
                                        search_reordering_rule = reordering_rule_obj.search([('product_id','=',search_product.id )],limit = 1)
                                        if search_reordering_rule:
                                            search_reordering_rule.write(vals)
                                        else:
                                            skipped_line_no[str(counter)]= " - No Reordering Rule is found for this product " 
                                    counter = counter + 1 
                                else:
                                    skipped_line_no[str(counter)]= " - Product not found or it's not a Stockable Product. " 
                                    counter = counter + 1 
                                    continue                            
                            else:
                                skipped_line_no[str(counter)] = " - Product is empty. "  
                                counter = counter + 1      
                        
                        except Exception as e:
                            skipped_line_no[str(counter)] = " - Value is not valid " + ustr(e)   
                            counter = counter + 1 
                            continue          
                             
                except Exception as e:
                    raise UserError(_("Sorry, Your csv file does not match with our format " + ustr(e) ))
                 
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
                            
                            if sheet.cell(row,0).value not in (None,""): 
                                vals={}
                                
                                field_nm = 'name'
                                if self.product_by == 'name':
                                    field_nm = 'name'
                                elif self.product_by == 'int_ref':
                                    field_nm = 'default_code'
                                elif self.product_by == 'barcode':
                                    field_nm = 'barcode'
                                
                                search_product = self.env['product.product'].search([(field_nm,'=',sheet.cell(row,0).value)], limit = 1)
                                if search_product and search_product.type == 'product':
                                    vals.update({'product_id' : search_product.id})
                                    
                                    if sheet.cell(row,1).value not in (None,""):
                                        vals.update({'product_min_qty' : sheet.cell(row,1).value })
                                    else:
                                        vals.update({'product_min_qty' : 0.0 })                                        
                                        
                                    if sheet.cell(row,2).value not in (None,""):
                                        vals.update({'product_max_qty' : sheet.cell(row,2).value })
                                    else:
                                        vals.update({'product_max_qty' : 0.0 })
                                    
                                    if sheet.cell(row,3).value not in (None,""):
                                        vals.update({'qty_multiple' : sheet.cell(row,3).value })
                                    else:
                                        vals.update({'qty_multiple' : 1.0 })
                                        
                                    if self.method == 'create':
                                        reordering_rule_obj.create(vals)
                                    else:
                                        search_reordering_rule = reordering_rule_obj.search([('product_id','=',search_product.id )],limit = 1)
                                        if search_reordering_rule:
                                            search_reordering_rule.write(vals)
                                        else:
                                            skipped_line_no[str(counter)]= " - No Reordering Rule is found for this product " 
                                    counter = counter + 1 
                                else:
                                    skipped_line_no[str(counter)]= " - Product not found or it's not a Stockable Product. " 
                                    counter = counter + 1 
                                    continue                            
                            else:
                                skipped_line_no[str(counter)] = " - Product is empty. "  
                                counter = counter + 1      
                        
                        except Exception as e:
                            skipped_line_no[str(counter)] = " - Value is not valid " + ustr(e)   
                            counter = counter + 1 
                            continue          
                             
                except Exception as e:
                    raise UserError(_("Sorry, Your excel file does not match with our format " + ustr(e) ))
                 
                if counter > 1:
                    completed_records = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_records, skipped_line_no)
                    return res