# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from openerp import models,fields,api

class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    @api.multi
    def sh_import_pol(self):
        if self:
            action = self.env.ref('sh_all_in_one_import.sh_import_pol_action').read()[0]
            return action             
            