# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from openerp import api, fields, models, _
from openerp.exceptions import UserError, AccessError
import csv
import base64
import io as StringIO
import xlrd
from openerp.tools import ustr
   
class import_inventory_wizard(models.TransientModel):
    _name="import.inventory.wizard"
    
    
    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        else:
            raise UserError(_('You must define a warehouse for the company: %s.') % (company_user.name,))    

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
    
    location_id = fields.Many2one("stock.location", string = "Location", domain="[('usage','not in', ['supplier','production'])]", required = True, default=_default_location_id )
    name = fields.Char(string="Inventory Reference", required = True)
    
    @api.multi
    def show_success_msg(self,counter,skipped_line_no):
        
        #to close the current active wizard        
        action = self.env.ref('sh_all_in_one_import.sh_import_inventory_action').read()[0]
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
    def import_inventory_apply(self):
        stock_inventory_obj = self.env['stock.inventory']
        stock_inventory_line_obj = self.env['stock.inventory.line']
        #perform import lead
        if self and self.file and self.location_id and self.name:
            #For CSV
            if self.import_type == 'csv':
                counter = 1
                skipped_line_no = {}
                try:
                    file = str(base64.decodestring(self.file).decode('utf-8'))
                    myreader = csv.reader(file.splitlines())
                    skip_header=True
                    created_inventory = False
                    inventory_vals = {
                            'name'        : self.name,
                            'location_id' : self.location_id.id,
                            'filter'      : 'partial'
                            
                        }
                    created_inventory = stock_inventory_obj.create(inventory_vals)  
                    if created_inventory:
                        created_inventory.prepare_inventory()                                       
                     
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
                                        vals.update({'product_qty' : row[1] })
                                    else:
                                        vals.update({'product_qty' : 0.0 })                                        
                                        
                                    if row[2].strip() not in (None,""):
                                        search_uom = self.env['product.uom'].search([('name','=', row[2].strip() )], limit = 1)
                                        if search_uom:
                                            vals.update({'product_uom_id' : search_uom.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Unit of Measure not found. "                                         
                                            counter = counter + 1
                                            continue                                        
                                    elif search_product.uom_id:
                                        vals.update({'product_uom_id' : search_product.uom_id.id })                                         
                                    else:
                                        skipped_line_no[str(counter)] = " - Unit of Measure not defined for this product. "                                         
                                        counter = counter + 1
                                        continue                                               
                                    
                                    if created_inventory:
                                        vals.update({'location_id' : created_inventory.location_id.id })                                          
                                        vals.update({'inventory_id' : created_inventory.id })
                                        stock_inventory_line_obj.create(vals)
                                    else:
                                        skipped_line_no[str(counter)] = " - Inventory could not be created. "                                         
                                        counter = counter + 1
                                        continue    
                                        
                                        
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
                             
                    if created_inventory:
                        created_inventory.action_done()                   
                
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
                    created_inventory = False
                    inventory_vals = {
                            'name'        : self.name,
                            'location_id' : self.location_id.id,
                            'filter'      : 'partial'
                            
                        }
                    created_inventory = stock_inventory_obj.create(inventory_vals)  
                    if created_inventory:
                        created_inventory.prepare_inventory()                      
                    
                     
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
                                        vals.update({'product_qty' : sheet.cell(row,1).value })
                                    else:
                                        vals.update({'product_qty' : 0.0 })                                        
                                        
                                    if sheet.cell(row,2).value.strip() not in (None,""):
                                        search_uom = self.env['product.uom'].search([('name','=', sheet.cell(row,2).value.strip() )], limit = 1)
                                        if search_uom:
                                            vals.update({'product_uom_id' : search_uom.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Unit of Measure not found. "                                         
                                            counter = counter + 1
                                            continue                                        
                                    elif search_product.uom_id:
                                        vals.update({'product_uom_id' : search_product.uom_id.id })                                         
                                    else:
                                        skipped_line_no[str(counter)] = " - Unit of Measure not defined for this product. "                                         
                                        counter = counter + 1
                                        continue                                               
                                    
                                    if created_inventory:
                                        vals.update({'location_id' : created_inventory.location_id.id })                                          
                                        vals.update({'inventory_id' : created_inventory.id })
                                        stock_inventory_line_obj.create(vals)
                                    else:
                                        skipped_line_no[str(counter)] = " - Inventory could not be created. "                                         
                                        counter = counter + 1
                                        continue    
                                        
                                        
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
                             
                    if created_inventory:
                        created_inventory.action_done()                   
                
                except Exception as e:
                    raise UserError(_("Sorry, Your excel file does not match with our format " + ustr(e) ))
                 
                if counter > 1:
                    completed_records = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_records, skipped_line_no)
                    return res