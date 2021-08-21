# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

from openerp import models, fields, api, _
from openerp.tools.safe_eval import safe_eval


class BaseConfigSettings(models.TransientModel):
    _inherit = "base.config.settings"
    _description = "Base config for Twilio "

    def _check_twilio(self):
        result = self.env['ir.module.module'].search(
            [('name', '=', 'twilio_gateway')])
        if result:
            return True
        else:
            return False

    def _check_plivo(self):
        result = self.env['ir.module.module'].search(
            [('name', '=', 'plivo_gateway')])
        if result:
            return True
        else:
            return False

    def _check_clicksend(self):
        result = self.env['ir.module.module'].search(
            [('name', '=', 'clicksend_gateway')])
        if result:
            return True
        else:
            return False

    def _check_msg91(self):
        result = self.env['ir.module.module'].search(
            [('name', '=', 'msg91_gateway')])
        if result:
            return True
        else:
            return False

    def _check_mobily(self):
        result = self.env['ir.module.module'].search(
            [('name', '=', 'mobily_gateway')])
        if result:
            return True
        else:
            return False
            
    module_mobily_gateway = fields.Boolean(
        string='Install Mobily SMS Gateway', help='It will Install Mobily sms gateway automatically.')
    is_mobily_in_addon = fields.Boolean(default=_check_mobily)
    module_twilio_gateway = fields.Boolean(
        string='Install Twilio SMS Gateway', help='It will Install twilio sms gateway automatically.')
    is_twilio_in_addon = fields.Boolean(default=_check_twilio)

    module_plivo_gateway = fields.Boolean(
        string='Install Plivo SMS Gateway', help='It will Install plivo sms gateway automatically.')
    is_plivo_in_addon = fields.Boolean(default=_check_plivo)

    module_clicksend_gateway = fields.Boolean(
        string='Install Clicksend SMS Gateway', help='It will Install clicksend sms gateway automatically.')
    is_clicksend_in_addon = fields.Boolean(default=_check_clicksend)

    module_msg91_gateway = fields.Boolean(
        string='Install MSG91 SMS Gateway', help='It will Install MSG91 sms gateway automatically.')
    is_msg91_in_addon = fields.Boolean(default=_check_msg91)

    is_phone_code_enable = fields.Boolean(string="Are you managing country calling code with customer's mobile number ?",
                                          help="If not enabled then it will pick country calling code from the country selected in customer. In case customer has no country then it will pick country calling code from company's country.")

    @api.model
    def get_default_is_phone_code_enable(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        # use safe_eval on the result, since the value of the parameter is a
        # nonempty string
        return {
            'is_phone_code_enable': safe_eval(IrConfigParam.get_param('sms_notification.is_phone_code_enable', 'False')),
        }

    @api.multi
    def set_is_phone_code_enable(self):
        self.ensure_one()
        IrConfigParam = self.env['ir.config_parameter']
        # store the repr of the values, since the value of the parameter is a
        # required string
        IrConfigParam.set_param(
            'sms_notification.is_phone_code_enable', repr(self.is_phone_code_enable))
