# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from openerp import models,fields,api

class sale_order(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def sh_import_sol(self):
        if self:
            action = self.env.ref('sh_all_in_one_import.sh_import_sol_action').read()[0]
            return action             
            