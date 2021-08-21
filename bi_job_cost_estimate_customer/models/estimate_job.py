# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, tools, _
import openerp.addons.decimal_precision as dp
import math

class JobEstimate(models.Model):
    _name = "job.estimate"
    _rec_name = 'number'
    
    @api.model
    def create(self , vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('job.sequence') or '/'
        return super(JobEstimate, self).create(vals)
    
    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id
            
    @api.multi
    def job_confirm(self):
        res = self.write({'state':'confirmed'})
        return res
    
    @api.multi
    def reset_draft(self):
        res = self.write({'state':'draft'})
        return res
    
    @api.multi
    def action_cancel(self):
        res = self.write({'state':'cancel'})
        return res
    
    @api.multi
    def approve_job_estimate(self):
        res = self.write({'state':'approved'})
        return res
    
    @api.multi
    def reject_job_estimate(self):
        res = self.write({'state':'cancel'})
        return res

    @api.multi
    def create_quotation(self):
        SO_val = {
            'partner_id': self.partner_id.id or False,
            'state': 'draft',
            'date_order' : self.date,
            'user_id' : self.sales_person_id.id,
            'company_id' : self.company_id.id,
            'analytic_account_id' : self.analytic_id.id,
        }
        sale_order_id = self.env['sale.order'].create(SO_val)
        for job_material_line in self.material_estimation_ids:
            material_line_vals = {
                'product_id': job_material_line.product_id.id,
                'name': job_material_line.product_id.name,
                'product_uom_qty': job_material_line.quantity,
                'product_uom': job_material_line.uom_id.id,
                'price_unit' : job_material_line.unit_price,
                'discount' : job_material_line.discount,
                'order_id': sale_order_id.id,
            }
            order_line_obj = self.env['sale.order.line'].create(material_line_vals)
        
        for job_labour_line in self.labour_estimation_ids:
            labour_line_vals = {
                'product_id': job_labour_line.product_id.id,
                'name': job_labour_line.product_id.name,
                'product_uom_qty': job_labour_line.quantity,
                'product_uom': job_labour_line.uom_id.id,
                'price_unit' : job_labour_line.unit_price,
                'discount' : job_labour_line.discount,
                'order_id': sale_order_id.id,
            }
            order_line_obj = self.env['sale.order.line'].create(labour_line_vals)
            
        for job_overhead_line in self.overhead_estimation_ids:
            overhead_line_vals = {
                'product_id': job_overhead_line.product_id.id,
                'name': job_overhead_line.product_id.name,
                'product_uom_qty': job_overhead_line.quantity,
                'product_uom': job_overhead_line.uom_id.id,
                'price_unit' : job_overhead_line.unit_price,
                'discount' : job_overhead_line.discount,
                'order_id': sale_order_id.id,
            }
            order_line_obj = self.env['sale.order.line'].create(overhead_line_vals)
            
        res = self.write({
                          'sale_quotation_id' : sale_order_id.id,
                          'state':'done'
                          })
        return res
    
    @api.multi
    def action_quotation_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('bi_job_cost_estimate_customer', 'job_estimate_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'job.estimate',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        a = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        return a
        
    @api.depends('material_estimation_ids.subtotal','labour_estimation_ids.subtotal','overhead_estimation_ids.subtotal')
    def _calculate_total(self):
        total_job_cost = 0.0
        for order in self:
            for line in order.material_estimation_ids:
                material_price =  (line.quantity * line.unit_price) - (line.quantity * line.unit_price) * (line.discount or 0.0) / 100.0
                order.mtab_total_material_estimate += material_price
                order.ltab_total_material_estimate += material_price
                order.otab_total_material_estimate += material_price
                total_job_cost += material_price
        
            for line in order.labour_estimation_ids:
                labour_price =  (line.quantity * line.unit_price) - (line.quantity * line.unit_price) * (line.discount or 0.0) / 100.0
                order.mtab_total_labour_estimate += labour_price
                order.ltab_total_labour_estimate += labour_price
                order.otab_total_labour_estimate += labour_price
                total_job_cost += labour_price
            
            for line in order.overhead_estimation_ids:
                overhead_price =  (line.quantity * line.unit_price) - (line.quantity * line.unit_price) * (line.discount or 0.0) / 100.0
                order.mtab_total_overhead_estimate += overhead_price
                order.ltab_total_overhead_estimate += overhead_price
                order.otab_total_overhead_estimate += overhead_price
                total_job_cost += overhead_price
        
        order.mtab_total_job_estimate = total_job_cost
        order.ltab_total_job_estimate = total_job_cost
        order.otab_total_job_estimate = total_job_cost
            
            
    partner_id = fields.Many2one('res.partner','Customer',required=True)
    number = fields.Char(string='Number', readonly=True,copy =False)
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('approved','Approved'),('done','Quotation Created'),('cancel','Cancel')],'Status',default="draft")#,('send','Estimate Sent')
    payment_term_id = fields.Many2one('account.payment.term','Payment Terms')
    customer_ref = fields.Char('Customer Reference')
    date = fields.Date('Date')
    company_id = fields.Many2one('res.company','Company')
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    project_id = fields.Many2one('project.project','Project')
    analytic_id =fields.Many2one('account.analytic.account','Analytic Account')
    job_type_id = fields.Many2many('job.estimate.category', column1='partner_id',column2='category_id', string='Job Type')
    material_estimation_ids = fields.One2many('material.estimate','material_id','Material Estimation')
    labour_estimation_ids = fields.One2many('labour.estimate','labour_id','Labour Estimation')
    overhead_estimation_ids = fields.One2many('overhead.estimate','overhead_id','Overhead Estimation')
    description = fields.Text('Description')
    # for Material Tab
    mtab_total_material_estimate = fields.Float(compute='_calculate_total',string='Total Material Estimate',default=0.0,readonly=True)
    mtab_total_labour_estimate = fields.Float(compute='_calculate_total',string='Total Labour Estimate',default=0.0,readonly=True)
    mtab_total_overhead_estimate = fields.Float(compute='_calculate_total',string='Total Overhead Estimate',default=0.0,readonly=True)
    mtab_total_job_estimate = fields.Float(compute='_calculate_total',string='Total Job Estimate',default=0.0,readonly=True)
    
    #for Labour Tab
    ltab_total_material_estimate = fields.Float(compute='_calculate_total',string='Total Material Estimate',default=0.0,readonly=True)
    ltab_total_labour_estimate = fields.Float(compute='_calculate_total',string='Total Labour Estimate',default=0.0,readonly=True)
    ltab_total_overhead_estimate = fields.Float(compute='_calculate_total',string='Total Overhead Estimate',default=0.0,readonly=True)
    ltab_total_job_estimate = fields.Float(compute='_calculate_total',string='Total Job Estimate',default=0.0,readonly=True)
    
    # for Overhead tab
    otab_total_material_estimate = fields.Float(compute='_calculate_total',string='Total Material Estimate',default=0.0,readonly=True)
    otab_total_labour_estimate = fields.Float(compute='_calculate_total',string='Total Labour Estimate',default=0.0,readonly=True)
    otab_total_overhead_estimate = fields.Float(compute='_calculate_total',string='Total Overhead Estimate',default=0.0,readonly=True)
    otab_total_job_estimate = fields.Float(compute='_calculate_total',string='Total Job Estimate',default=0.0,readonly=True)
    
    origin = fields.Char('Source Document')
    sales_person_id = fields.Many2one('res.users','Salesperson')
    sales_team_id = fields.Many2one('crm.team','Sales Team')
    sale_quotation_id = fields.Many2one('sale.order','Sales Quotation',readonly=True)    

class MaterialEstimate(models.Model):
    _name = "material.estimate"

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if not self.product_id:
            return res
        self.uom_id = self.product_id.uom_id.id
        self.quantity = 1.0
        self.unit_price = self.product_id.list_price
        
    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id
            
    @api.onchange('quantity', 'unit_price','discount')
    def onchange_quantity(self):
        price = 0.0
        for line in self:
            price =  (line.quantity * line.unit_price) - (line.quantity * line.unit_price) * (line.discount or 0.0) / 100.0
            line.subtotal = price
            
    material_id = fields.Many2one('job.estimate','Material')
    type = fields.Selection([('material','Material'),('labour','Labour'),('overhead','Overhead')],string='Type')
    product_id = fields.Many2one('product.product','Product')
    description = fields.Text('Description')
    quantity = fields.Float('Quantity',default=0.0)
    uom_id = fields.Many2one('product.uom','Unit Of Measure')
    unit_price = fields.Float('Unit Price',defaut=0.0)
    discount = fields.Float('Discount (%)',default=0.0)
    subtotal = fields.Float('Sub Total',defalut=0.0)
    currency_id = fields.Many2one('res.currency', compute='get_currency_id', string="Currency")
    
class LabourEstimate(models.Model):
    _name = "labour.estimate"

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if not self.product_id:
            return res
        self.uom_id = self.product_id.uom_id.id
        self.quantity = 1.0
        self.unit_price = self.product_id.list_price
        
    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id
            
    @api.onchange('quantity', 'unit_price','discount')
    def onchange_quantity(self):
        price = 0.0
        for line in self:
            price =  (line.quantity * line.unit_price) - (line.quantity * line.unit_price) * (line.discount or 0.0) / 100.0
            line.subtotal = price
            
    labour_id = fields.Many2one('job.estimate','Labour')
    type = fields.Selection([('material','Material'),('labour','Labour'),('overhead','Overhead')],string='Type')
    product_id = fields.Many2one('product.product','Product')
    description = fields.Text('Description')
    quantity = fields.Float('Quantity',default=0.0)
    uom_id = fields.Many2one('product.uom','Unit Of Measure')
    unit_price = fields.Float('Unit Price',defaut=0.0)
    discount = fields.Float('Discount (%)',default=0.0)
    subtotal = fields.Float('Sub Total',defalut=0.0)
    currency_id = fields.Many2one('res.currency', compute='get_currency_id', string="Currency")
    
class OverheadEstimate(models.Model):
    _name = "overhead.estimate"
    
    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if not self.product_id:
            return res
        self.uom_id = self.product_id.uom_id.id
        self.quantity = 1.0
        self.unit_price = self.product_id.list_price
        
    @api.multi
    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id
            
    @api.onchange('quantity', 'unit_price','discount')
    def onchange_quantity(self):
        price = 0.0
        for line in self:
            price =  (line.quantity * line.unit_price) - (line.quantity * line.unit_price) * (line.discount or 0.0) / 100.0
            line.subtotal = price
            
    overhead_id = fields.Many2one('job.estimate','Overhead')
    type = fields.Selection([('material','Material'),('labour','Labour'),('overhead','Overhead')],string='Type')
    product_id = fields.Many2one('product.product','Product')
    description = fields.Text('Description')
    quantity = fields.Float('Quantity',default=0.0)
    uom_id = fields.Many2one('product.uom','Unit Of Measure')
    unit_price = fields.Float('Unit Price',defaut=0.0)
    discount = fields.Float('Discount (%)',default=0.0)
    subtotal = fields.Float('Sub Total',defalut=0.0)
    currency_id = fields.Many2one('res.currency', compute='get_currency_id', string="Currency")
            
class JobEstimateCategory(models.Model):
    _name = 'job.estimate.category'

    name = fields.Char(string='Job Name', required=True)
            
