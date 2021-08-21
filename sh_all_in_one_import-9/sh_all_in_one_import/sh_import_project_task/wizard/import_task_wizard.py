# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from openerp import api, fields, models, _
from datetime import datetime
from openerp.exceptions import UserError, AccessError
import csv
import base64
import io as StringIO
import xlrd

class import_task_wizard(models.TransientModel):
    _name="import.task.wizard"
    
    
    project_id=fields.Many2one("project.project",string="Project")
    import_type=fields.Selection([
        ('csv','CSV File'),
        ('excel','Excel File')
        ],default="csv",string="Import File Type",required=True)
    file=fields.Binary(string="File",required=True)
    user_id=fields.Many2one('res.users',string="Assigned to")
    #extension
    import_method=fields.Selection([
        ('default','By Default'),
        ('proj_user_wise','Project and user wise import')
        ],default="default",string="Import Method",required=True)
    
    @api.multi
    def show_success_msg(self,counter,skipped_line_no):
        
        #to close the current active wizard        
        action = self.env.ref('sh_all_in_one_import.sh_action_import_task').read()[0]
        action = {'type': 'ir.actions.act_window_close'} 
        
        #open the new success message box    
        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False                                   
        context = dict(self._context or {})
        dic_msg='\n'.join("{}: {}".format(k, v) for k, v in skipped_line_no.items())
        context['message']=str(counter) + " Tasks created successfully "+ str(dic_msg)
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
    def import_task_apply(self):

        project_task_obj=self.env['project.task']
        project_obj=self.env['project.project']
        user_obj=self.env['res.users']
        #perform import task using by default method...
        if self and self.file:
            #For CSV
            #default import
            if self.import_type == 'csv' and self.import_method == 'default':
                counter=0
                skipped_line_no={}
                try:
                    file = str(base64.decodestring(self.file).decode('utf-8'))
                    myreader = csv.reader(file.splitlines())
                    skip_header=True
                    
                    for row in myreader:
                        try:
                            if skip_header:
                                skip_header=False
                                continue
                            if row[2] != '':                        
                                
                                final_deadline_date=None
                                if row[4]!='':
                                    cd=row[4]                
                                    cd= str(datetime.strptime(cd, '%Y-%m-%d').date())
                                    final_deadline_date=cd                        
                                    
                                search_project_id=False
                                if row[0] != '':
                                    search_project=project_obj.search([('name','=',row[0])],limit=1)
                                    if search_project:
                                        search_project_id=search_project.id
                                    else:
                                        search_project_id=False                                        
                                        skipped_line_no[str(counter + 2)]= " - Project not found. " 
                                        counter=counter +1                                 
                                        continue
                                
                                search_user_id=False
                                if row[1] != '':
                                    search_user=user_obj.search([('name','=',row[1])],limit=1)
                                    if search_user:
                                        search_user_id=search_user.id
                                    else:
                                        search_user_id=False
                                                                          
                                vals={
                                    'name'          : row[2],
                                    'date_deadline' : final_deadline_date,
                                    'description'   : row[3],
                                    'project_id'    : search_project_id,
                                    'user_id'       : search_user_id,
                                    'planned_hours' : row[5],
                                    }
                                created_pt=project_task_obj.create(vals)
                                counter=counter +1
                            else:
                                skipped_line_no[str(counter + 2 )]=" - Task name is empty. "  
                                counter=counter +1      
                        except Exception:
                            skipped_line_no[str(counter + 2 )]=" - Value is not valid. "   
                            counter=counter +1 
                            continue          
                            
                except Exception:
                    raise UserError(_("Sorry, Your csv file does not match with our format"))
                
                if counter==0:
                    raise UserError(_("Something went wrong"))
                elif counter>=1:
                    completed_task=counter - len(skipped_line_no)
                    res=self.show_success_msg(completed_task,skipped_line_no)
                    return res

            
            
            
            #project and user wise import.
            if self.import_type == 'csv' and self.import_method == 'proj_user_wise' and self.user_id and self.project_id:
                counter=0
                skipped_line_no={}                
                try:
                    file = str(base64.decodestring(self.file).decode('utf-8'))
                    myreader = csv.reader(file.splitlines())
                    skip_header=True
                    
                    for row in myreader:
                        try:
                            if skip_header:
                                skip_header=False
                                continue
                            if row[0] != '':                        
                                final_deadline_date=None
                                if row[2]!='':
                                    cd=row[2]                
                                    cd= str(datetime.strptime(cd, '%Y-%m-%d').date())
                                    final_deadline_date=cd                        
                                vals={
                                    'name'          : row[0],
                                    'planned_hours' : row[1],
                                    'date_deadline' : final_deadline_date,
                                    'description'   : row[3],
                                    'project_id'    : self.project_id.id,
                                    'user_id'       : self.user_id.id,
                                    }
                                created_pt=project_task_obj.create(vals)
                                counter=counter +1
                            else:
                                skipped_line_no[str( counter + 2 )] = " - Task name is empty. "  
                                counter=counter +1
                                continue      
                        except Exception:
                            skipped_line_no[str( counter + 2 )] = " - Value is not valid. "   
                            counter=counter +1 
                            continue                                                                        
         
                except Exception:
                    raise UserError(_("Sorry, Your csv file does not match with our format"))
                
                if counter==0:
                    raise UserError(_("Something went wrong"))
                elif counter>=1:
                    completed_task=counter - len(skipped_line_no)
                    res=self.show_success_msg(completed_task,skipped_line_no)
                    return res       
            
            #For Excel
            #default import
            if self.import_type == 'excel' and self.import_method == 'default':
                counter=0
                skipped_line_no={}                  
                try:
                    wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
                    sheet = wb.sheet_by_index(0)     
                    skip_header=True    
                    for row in range(sheet.nrows):
                        try:
                            if skip_header:
                                skip_header=False
                                continue
                            if sheet.cell(row,2).value != '':                                    
                                
                                final_deadline_date=None
                                if sheet.cell(row,4).value !='':                            
                                    cd=sheet.cell(row,4).value                
                                    cd= str(datetime.strptime(cd, '%Y-%m-%d').date())
                                    final_deadline_date=cd                
                                
                                search_project_id=False
                                if sheet.cell(row,0).value != '':
                                    search_project=project_obj.search([('name','=', sheet.cell(row,0).value )],limit=1)
                                    if search_project:
                                        search_project_id=search_project.id
                                    else:
                                        search_project_id=False                                        
                                        skipped_line_no[str(counter + 2)]= " - Project not found. " 
                                        counter=counter +1                                 
                                        continue                            
                                                            
                                search_user_id=False
                                if sheet.cell(row,1).value != '':
                                    search_user=user_obj.search([('name','=',sheet.cell(row,1).value )],limit=1)
                                    if search_user:
                                        search_user_id=search_user.id
                                    else:
                                        search_user_id=False                               
                                vals={
                                    'name'          : sheet.cell(row,2).value,
                                    'date_deadline' : final_deadline_date,
                                    'description'   : sheet.cell(row,3).value,
                                    'project_id'    : search_project_id,
                                    'user_id'       : search_user_id,
                                    'planned_hours' : sheet.cell(row,5).value,                                    
                                    }
                                created_pt=project_task_obj.create(vals)
                                counter=counter +1
                            else:      
                                skipped_line_no[str(counter + 2 )]=" - Task name is empty. "  
                                counter=counter +1
                        except Exception:
                            skipped_line_no[str(counter + 2 )]=" - Value is not valid. "   
                            counter=counter +1 
                            continue   
                            
                                    
                            
                except Exception:
                    raise UserError(_("Sorry, Your excel file does not match with our format"))
                
                if counter==0:
                    raise UserError(_("Something went wrong"))
                elif counter>=1:
                    completed_task=counter - len(skipped_line_no)
                    res=self.show_success_msg(completed_task,skipped_line_no)
                    return res               
            
            #Project and user wise import
            if self.import_type=='excel' and self.import_method == 'proj_user_wise' and self.user_id and self.project_id:
                counter=0   
                skipped_line_no={}                               
                try:   
                    wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
                    sheet = wb.sheet_by_index(0)     
                    skip_header=True        
                    for row in range(sheet.nrows):
                        try:
                            if skip_header:
                                skip_header=False
                                continue
                            if sheet.cell(row,0).value != '':                
                                final_deadline_date=None
                                if sheet.cell(row,2).value !='':
                                    cd=sheet.cell(row,2).value                
                                    cd= str(datetime.strptime(cd, '%Y-%m-%d').date())
                                    final_deadline_date=cd
                                
                                
                                vals={
                                    'name'          : sheet.cell(row,0).value,
                                    'planned_hours' : sheet.cell(row,1).value,
                                    'date_deadline' : final_deadline_date,
                                    'description'   : sheet.cell(row,3).value,
                                    'project_id'    : self.project_id.id,
                                    'user_id'       : self.user_id.id,
                                    }
                                created_pt=project_task_obj.create(vals)
                                counter=counter +1                                                        
                            else:      
                                skipped_line_no[str(counter + 2 )]=" - Task name is empty. "  
                                counter=counter +1
                        except Exception:
                            skipped_line_no[str(counter + 2 )]=" - Value is not valid. "   
                            counter=counter +1 
                            continue                                            

                except Exception:
                    raise UserError(_("Sorry, Your excel file does not match with our format"))
                
                if counter==0:
                    raise UserError(_("Something went wrong"))
                elif counter>=1:
                    completed_task=counter - len(skipped_line_no)
                    res=self.show_success_msg(completed_task,skipped_line_no)
                    return res  
    
    