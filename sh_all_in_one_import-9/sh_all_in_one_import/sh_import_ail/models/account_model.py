# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from openerp import models,fields,api

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    @api.multi
    def sh_import_ail(self):
        if self:
            action = self.env.ref('sh_all_in_one_import.sh_import_ail_action').read()[0]
            return action             
            