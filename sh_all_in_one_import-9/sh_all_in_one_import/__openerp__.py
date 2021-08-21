# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "All In One Import - Partner, Product, Sales, Purchase, Accounts, Inventory, BOM, CRM, Project",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
    "summary": "This module is useful to import data from CSV/excel file.",
    "description": """
    
This module is useful to import data from CSV/excel file.


 All In One Import - Sales, Purchase, Account, Inventory, BOM, CRM Odoo
 Import Partner From Csv, Import Partner From Excel, Import Partner From XLS, Import Partner From XLSX, Import Product From Csv, Import Product From Excel, Import Product From XLS, Import Product From XLSX,  Import Sales From Csv, Import Sale Order From Excel, Import Quotation From XLS, Import so From XLSX, Import Purchase From Csv, Import Purchase Order From Excel, Import Request For Quotation From XLS, Import RFQ From XLSX, Import Account From Csv, Import Invoice From Excel, Import Invoice From XLS, Import Account From XLSX, Import Inventory From Csv, Import Stock From Excel, Import Inventory From XLS, Import Stock From XLSX, Import BOM From Csv, Import Bill Of Material From Excel, Import BOM From XLS, Import Bill Of Material From XLSX, Import CRM From Csv, Import CRM From Excel, Import Lead From XLS, Import Lead From XLSX, Import Bill Of Material From XLSX, Import CRM From Csv, Import CRM From Excel, Import Lead From XLS, Import Lead From XLSX,  Import Project From XLSX, Import Project From Csv, Import Task From Excel, Import Reordering Rules From XLS, Import Lead From XLSX Odoo. 
 Import Partner From Csv, Import Product From Excel,  Import Sale Order From Csv ,Import Purchase Order From Excel Module,Import Account From Csv, Import Invoice From Excel,Import Inventory From Xls, Import Stock From Xlsx, Import Bill Of Material From CSV, Import CRM From Csv, Import Lead From XLS,Import Project From XLSX, Import Task From Excel, Import Reordering Rules From XLS Odoo.

Import Customers/Suppliers
Import Product Template
Import Product Variant
Import Product Image
Import Sale Order
Import Sale Order Lines
Import Stock Inventory
Import Stock Inventory With Lot/Serial Number
Import Reordering Rules
Import Purchase Order
Import Purchase Order Lines
Import Vendor Details in Product
Import Invoice
Import Invoice/Bill Lines
Import bank statement lines
Import Bill of Materials
Import Task
Import Lead
Import Employee Image
Import Employee Timesheet
Import Internal Transfer
Import Customer Image


                    """,
    "version":"9.0.1",
    "depends" : [
            "base",
            "sh_message",
            "account",
            "mrp",
            "stock",
            "product",
            "crm",
            "sale",
            "purchase",  
            "project",  
            "hr",
            "hr_timesheet",  
            "hr_attendance"                  
        ],
    "application" : True,
    "data" : [
            'sh_import_ail/security/import_ail_security.xml',
            'sh_import_ail/wizard/import_ail_wizard.xml',
            'sh_import_ail/views/account_view.xml',
            
            'sh_import_bom/security/import_bom_security.xml',
            'sh_import_bom/wizard/import_bom_wizard.xml',
            'sh_import_bom/views/mrp_view.xml',     
              
            'sh_import_bsl/security/import_bsl_security.xml',
            'sh_import_bsl/wizard/import_bsl_wizard.xml',
            'sh_import_bsl/views/account_view.xml',   
              
            'sh_import_inv/security/import_inv_security.xml',
            'sh_import_inv/wizard/import_inv_wizard.xml',
            'sh_import_inv/views/account_view.xml',   
              
            'sh_import_inventory/security/import_inventory_security.xml',
            'sh_import_inventory/wizard/import_inventory_wizard.xml',
            'sh_import_inventory/views/stock_view.xml',    
              
            'sh_import_inventory_with_lot_serial/security/import_inventory_with_lot_serial_security.xml',
            'sh_import_inventory_with_lot_serial/wizard/import_inventory_with_lot_serial_wizard.xml',
            'sh_import_inventory_with_lot_serial/views/stock_view.xml',   
              
            'sh_import_lead/security/import_lead_security.xml',
            'sh_import_lead/wizard/import_lead_wizard.xml',
            'sh_import_lead/views/crm_view.xml',   
              
            'sh_import_partner/security/import_partner_security.xml',
            'sh_import_partner/wizard/import_partner_wizard.xml',
            'sh_import_partner/views/sale_view.xml',   
              
            'sh_import_po/security/import_po_security.xml',
            'sh_import_po/wizard/import_po_wizard.xml',
            'sh_import_po/views/purchase_view.xml',    
              
            'sh_import_pol/security/import_pol_security.xml',
            'sh_import_pol/wizard/import_pol_wizard.xml',
            'sh_import_pol/views/purchase_view.xml',          
              
            'sh_import_product_img/security/import_product_img_security.xml',
            'sh_import_product_img/wizard/import_product_img_wizard.xml',
            'sh_import_product_img/views/sale_view.xml',   
              
            'sh_import_product_tmpl/security/import_product_tmpl_security.xml',
            'sh_import_product_tmpl/wizard/import_product_tmpl_wizard.xml',
            'sh_import_product_tmpl/views/sale_view.xml',     
              
            'sh_import_project_task/security/import_project_task_security.xml',
            'sh_import_project_task/wizard/import_task_wizard.xml',
            'sh_import_project_task/views/project_view.xml',  
              
            'sh_import_reordering_rules/security/import_reordering_rule_security.xml',
            'sh_import_reordering_rules/wizard/import_reordering_rule_wizard.xml',
            'sh_import_reordering_rules/views/stock_view.xml',   
              
            'sh_import_so/security/import_so_security.xml',
            'sh_import_so/wizard/import_so_wizard.xml',
            'sh_import_so/views/sale_view.xml',  
              
            'sh_import_sol/security/import_sol_security.xml',
            'sh_import_sol/wizard/import_sol_wizard.xml',
            'sh_import_sol/views/sale_view.xml',    
              
            'sh_import_supplier_info/security/import_supplier_info_security.xml',
            'sh_import_supplier_info/wizard/import_supplier_info_wizard.xml',
            'sh_import_supplier_info/views/purchase_view.xml',  
            
            'sh_import_emp_img/security/import_emp_img_security.xml',
            'sh_import_emp_img/wizard/import_emp_img_wizard.xml',
            'sh_import_emp_img/views/hr_view.xml',    
            
            'sh_import_emp_timesheet/security/import_emp_timesheet_security.xml',
            'sh_import_emp_timesheet/wizard/import_emp_timesheet_wizard.xml',
            'sh_import_emp_timesheet/views/timesheet_view.xml',   
            
            'sh_import_int_transfer/security/import_int_transfer_security.xml',
            'sh_import_int_transfer/wizard/import_int_transfer_wizard.xml',
            'sh_import_int_transfer/views/stock_view.xml', 
            
            'sh_import_partner_img/security/import_partner_img.xml',
            'sh_import_partner_img/wizard/import_partner_img_wizard.xml',
            'sh_import_partner_img/views/sale_view.xml',                                                                                                                                                                                      
            
            ],         
    'external_dependencies' : {
        'python' : ['xlrd'],
    },                  
    "images": ["static/description/background.png",],              
    "auto_install":False,
    "installable" : True,
    "price": 80,
    "currency": "EUR"   
}




