# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from openerp import api, fields, models, _
from openerp.exceptions import UserError, AccessError
import csv
import base64
import io as StringIO
import xlrd
from openerp.tools import ustr

   
class import_supplier_info_wizard(models.TransientModel):
    _name="import.supplier.info.wizard"

    import_type = fields.Selection([
        ('csv','CSV File'),
        ('excel','Excel File')
        ],default="csv",string="Import File Type",required=True)
    file = fields.Binary(string="File",required=True)   
    
    product_model = fields.Selection([
        ('pro_var','Product Variants'),
        ('pro_tmpl','Product Template')        
        ], default = "pro_var", string="Product Model", required = True)   
    
    product_by = fields.Selection([
        ('name','Name'),
        ('int_ref','Internal Reference'),
        ('barcode','Barcode')
        ],default="name", string = "Product By", required = True)     

    @api.multi
    def show_success_msg(self,counter,skipped_line_no):
        
        #to close the current active wizard        
        action = self.env.ref('sh_all_in_one_import.sh_import_supplier_info_action').read()[0]
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
    def import_supplier_info_apply(self):
        supplier_info_obj = self.env['product.supplierinfo']
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

                            if row[0] not in (None,"") and row[1] not in (None,""): 
                                vals={}
                                
                                field_nm = 'name'
                                if self.product_by == 'name':
                                    field_nm = 'name'
                                elif self.product_by == 'int_ref':
                                    field_nm = 'default_code'
                                elif self.product_by == 'barcode':
                                    field_nm = 'barcode'
                                
                                
                                product_obj = False
                                product_field_nm = 'product_id'
                                if self.product_model == 'pro_var':
                                    product_obj = self.env["product.product"]
                                    product_field_nm = 'product_id'                                    
                                else:
                                    product_obj = self.env["product.template"]   
                                    product_field_nm = 'product_tmpl_id'                                                                         
                                
                                
                                search_product = product_obj.search([(field_nm,'=',row[0] )], limit = 1)
                                if search_product:
                                    vals.update({product_field_nm : search_product.id})
                                    if product_field_nm == 'product_id' and search_product.product_tmpl_id:
                                        vals.update({'product_tmpl_id' : search_product.product_tmpl_id.id})
                                else:
                                    skipped_line_no[str(counter)]= " - Product not found. " 
                                    counter = counter + 1 
                                    continue                            
                                
                                search_vendor = self.env['res.partner'].search([('name','=',row[1] )], limit = 1)
                                if search_vendor and search_vendor.supplier == True:
                                    vals.update({'name' : search_vendor.id})                                
                                else:
                                    skipped_line_no[str(counter)]= " - Vendor not found or is not a supplier. " 
                                    counter = counter + 1 
                                    continue   
                                
                                if row[2] not in (None,""):
                                    vals.update({'product_name' : row[2] })
                                    
                                if row[3] not in (None,""):
                                    vals.update({'product_code' : row[3] })      
                                
                                if row[4] not in (None,""):
                                    vals.update({'delay' : row[4] })                                      
                                else:
                                    vals.update({'delay' : 1 })   
                                    
                                if row[5] not in (None,""):
                                    vals.update({'min_qty' : row[5] })                                      
                                else:
                                    vals.update({'min_qty' : 0.00 })       
                                    
                                if row[6] not in (None,""):
                                    vals.update({'price' : row[6] })                                      
                                else:
                                    vals.update({'price' : 0.00 })    
                                    
                                supplier_info_obj.create(vals)         
                                counter = counter + 1                                                                                           
                                                                                                       
                            else:
                                skipped_line_no[str(counter)] = " - Product or Vendor is empty. "  
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
                            
                            if sheet.cell(row,0).value not in (None,"") and sheet.cell(row,1).value not in (None,""): 
                                vals={}
                                
                                field_nm = 'name'
                                if self.product_by == 'name':
                                    field_nm = 'name'
                                elif self.product_by == 'int_ref':
                                    field_nm = 'default_code'
                                elif self.product_by == 'barcode':
                                    field_nm = 'barcode'
                                
                                
                                product_obj = False
                                product_field_nm = 'product_id'
                                if self.product_model == 'pro_var':
                                    product_obj = self.env["product.product"]
                                    product_field_nm = 'product_id'                                    
                                else:
                                    product_obj = self.env["product.template"]   
                                    product_field_nm = 'product_tmpl_id'                                                                         
                                
                                
                                search_product = product_obj.search([(field_nm,'=',sheet.cell(row,0).value )], limit = 1)
                                if search_product:
                                    vals.update({product_field_nm : search_product.id})
                                    if product_field_nm == 'product_id' and search_product.product_tmpl_id:
                                        vals.update({'product_tmpl_id' : search_product.product_tmpl_id.id})
                                else:
                                    skipped_line_no[str(counter)]= " - Product not found. " 
                                    counter = counter + 1 
                                    continue                            
                                
                                search_vendor = self.env['res.partner'].search([('name','=',sheet.cell(row,1).value )], limit = 1)
                                if search_vendor and search_vendor.supplier == True:
                                    vals.update({'name' : search_vendor.id})                                
                                else:
                                    skipped_line_no[str(counter)]= " - Vendor not found or is not a supplier. " 
                                    counter = counter + 1 
                                    continue   
                                
                                if sheet.cell(row,2).value not in (None,""):
                                    vals.update({'product_name' : sheet.cell(row,2).value })
                                    
                                if sheet.cell(row,3).value not in (None,""):
                                    vals.update({'product_code' : sheet.cell(row,3).value })      
                                
                                if sheet.cell(row,4).value not in (None,""):
                                    vals.update({'delay' : sheet.cell(row,4).value })                                      
                                else:
                                    vals.update({'delay' : 1 })   
                                    
                                if sheet.cell(row,5).value not in (None,""):
                                    vals.update({'min_qty' : sheet.cell(row,5).value })                                      
                                else:
                                    vals.update({'min_qty' : 0.00 })       
                                    
                                if sheet.cell(row,6).value not in (None,""):
                                    vals.update({'price' : sheet.cell(row,6).value })                                      
                                else:
                                    vals.update({'price' : 0.00 })    
                                    
                                supplier_info_obj.create(vals)         
                                counter = counter + 1                                                                                           
                                                                                                       
                            else:
                                skipped_line_no[str(counter)] = " - Product or Vendor is empty. "  
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