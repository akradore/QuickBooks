# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from openerp import models,fields,api
from datetime import datetime 
from openerp.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'
 
    analytic_account_id = fields.Many2one("account.analytic.account",string="Analytic Account")

class ProjectConfigSettings(models.TransientModel):
    _inherit = 'project.config.settings'
    
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)   
    analytic_account_id =fields.Many2one("account.analytic.account",related='company_id.analytic_account_id',string="Analytic Account",default=lambda self : self.env.user.company_id.analytic_account_id)
        
class AccountAnalyticLine(models.Model):
    _inherit='account.analytic.line'

    start_date = fields.Datetime("Start Date")
    end_date = fields.Datetime("End Date")    

class TaskTimeAccountLine(models.Model):
    _name = 'task.time.account.line'

    @api.multi
    def _get_default_start_time(self):
        active_model = self.env.context.get('active_model')
        
        if active_model =='project.task':
            active_id =  self.env.context.get('active_id')        
            if active_id:
                task_search = self.env['project.task'].search([('id','=',active_id)],limit=1)
                 
                return task_search.start_time
    
    @api.multi
    def _get_default_end_time(self):
        active_model = self.env.context.get('active_model')
        
        if active_model =='project.task':
            active_id =  self.env.context.get('active_id')        
            if active_id:
                task_search = self.env['project.task'].search([('id','=',active_id)],limit=1)
                 
                return task_search.end_time

    @api.multi
    def _get_default_duration(self):
        active_model = self.env.context.get('active_model')
        
        if active_model =='project.task':
            active_id =  self.env.context.get('active_id')        
            if active_id:
                task_search = self.env['project.task'].search([('id','=',active_id)],limit=1)
                return  float(task_search.total_time)

    name = fields.Char("Description",required = True)
    start_date = fields.Datetime("Start Date", default = _get_default_start_time , readonly=True)
    end_date = fields.Datetime("End Date",default = _get_default_end_time , readonly=True)    
    duration = fields.Float("Duration (HH:MM)",default = _get_default_duration , readonly=True)

    @api.multi
    def end_task(self):         

        context = dict(self.env.context or {})       
        
        active_model = context.get('active_model',False)                     
        active_id = context.get('active_id',False)
                             
        vals = {'name':self.name,'unit_amount':self.duration,'amount':self.duration,'date': datetime.now()}
        
        if active_model=='project.task':
            if active_id:
                 
                task_search =self.env['project.task'].search([('id','=',active_id)],limit=1)               
                if task_search:

                    vals.update({'start_date':task_search.start_time })
                    vals.update({'end_date':task_search.end_time })
                    vals.update({'is_timesheet':True })
                    
                    if task_search.project_id:
                        project_id = task_search.project_id.id
                     
                        if project_id:                       
                            act_id = self.env['project.project'].sudo().browse(task_search.project_id.id).analytic_account_id
                            if act_id :
                                vals.update({'account_id':act_id.id})
                    
                    else :
                        analytic_account_search = self.env.user.company_id.analytic_account_id
                        if analytic_account_search:
                            if analytic_account_search.id:
                                vals.update({'account_id':analytic_account_search.id })
                        else :
                            raise UserError('Please set Default Analytic Account for Timesheet, from Project -> Settings')
                     
                    task_search.sudo().write({'start_time':None})
                          
        usr_id = context.get('uid',False)
        if usr_id:
            vals.update({'user_id': usr_id })
            
        line_obj = self.env['account.analytic.line'].sudo().create(vals)
        self.sudo()._cr.commit()
        return
    
class ProjectTask(models.Model):    
    _inherit = 'project.task'
    
    start_time = fields.Datetime("Start Time",copy=False)
    end_time = fields.Datetime("End Time",copy=False)
    total_time = fields.Char("Total Time",copy=False)
    
    @api.multi
    def action_task_start(self):
        self.start_time = datetime.now()
        
    @api.multi
    def action_task_end(self):         
        self.sudo().end_time = datetime.now()

        start = datetime.strptime(str(self.start_time), '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(str(self.end_time), '%Y-%m-%d %H:%M:%S')

        tot_sec = ( end - start).total_seconds()
        tot_hours = round( (tot_sec / 3600.0),2)       
        
        self.sudo().total_time = tot_hours                
        return {
            'name': "End Task",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'task.time.account.line',
            'target':'new',
        }        
    