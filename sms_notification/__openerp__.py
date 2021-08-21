# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
#################################################################################
{
    "name":  "Sms Notification",
    "summary":  "This module allows you to send sms notification to your users for the order confirmation, delivery, refund, etc.",
    "category":  "Marketing",
    "version":  "1.2.0",
    "sequence":  1,
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    "website":  "https://store.webkul.com/Odoo-SMS-Notification.html",
    "description":  """
                    https://webkul.com/blog/odoo-sms-notification/
    """,
    "live_test_url":  "http://odoodemo.webkul.com/?module=sms_notification&version=9.0",
    "depends":  ['sale', 'stock'],
    "data":  [
        'security/ir_rule.xml',
        'wizard/sms_template_preview_view.xml',
        'views/configure_gateway_view.xml',
        'views/sms_sms_view.xml',
        'views/sms_group_view.xml',
        'views/res_config_view.xml',
        'views/sms_report_view.xml',
        'views/sms_cron_view.xml',
        'views/sms_template_view.xml',
        'edi/general_messages.xml',
        'edi/sms_template_for_order_creation.xml',
        'edi/sms_template_for_order_confirm.xml',
        'edi/sms_template_for_invoice_validate.xml',
        'edi/sms_template_for_delivery_done.xml',
        'edi/sms_template_for_invoice_payment_register.xml',
        'security/ir.model.access.csv',
    ],
    "images":  ['static/description/Banner.png'],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
    "price":  49,
    "currency":  "EUR",
}