# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta

import logging
from openerp import fields, SUPERUSER_ID
from openerp.http import request
from openerp.osv import orm
from openerp.tools import float_compare

_logger = logging.getLogger(__name__)


class PaymentTransaction(orm.Model):
    _inherit = 'payment.transaction'

    def get_booking_date(self, times="0:0", date=None):
        booking_times = times.split(":")
        booking_time = int(booking_times[0]) * 60 + int(booking_times[1])
        return datetime.strptime(str(date), '%d/%m/%Y') + timedelta(minutes=booking_time)

    def get_utc_date(self, date=None, timezone=None):
        to_zone = pytz.timezone('UTC')
        from_zone = pytz.timezone(timezone)
        return from_zone.localize(date).astimezone(to_zone)

    def form_feedback(self, cr, uid, data, acquirer_name, context=None):
        """ Override to confirm the sale order, if defined, and if the transaction
        is done. """
        tx = None
        res = super(PaymentTransaction, self).form_feedback(cr, uid, data, acquirer_name, context=context)

        # fetch the tx, check its state, confirm the potential SO
        try:
            tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
            if hasattr(self, tx_find_method_name):
                tx = getattr(self, tx_find_method_name)(cr, uid, data, context=context)
            _logger.info('<%s> transaction processed: tx ref:%s, tx amount: %s', acquirer_name, tx.reference if tx else 'n/a', tx.amount if tx else 'n/a')

            tx.write({'state': 'done'})
            if tx and tx.sale_order_id:
                # verify SO/TX match, excluding tx.fees which are currently not included in SO
                amount_matches = (tx.sale_order_id.state in ['draft', 'sent'] and float_compare(tx.amount, tx.sale_order_id.amount_total, 2) == 0)
                if amount_matches:
                    if tx.state == 'done' and tx.acquirer_id.auto_confirm == 'at_pay_confirm':
                        _logger.info('<%s> transaction completed, auto-confirming order %s (ID %s)', acquirer_name, tx.sale_order_id.name, tx.sale_order_id.id)
                        print "before"
                        for line in tx.sale_order_id.order_line:
                            if line.appointment_id:
                                for app in line.appointment_id:
                                    print "hello", app
                                    name = '%s-%s' % (tx.sale_order_id.partner_id.name, app.click_time_dt)
                                    app.write({
                                        'name': name,
                                        'status': 'booked',
                                        'app_state': 'done',
                                        #'partner_ids': [(4, tx.sale_order_id.partner_id.id)]
                                        'partner_ids': [(4, [tx.sale_order_id.partner_id.id, app.app_partner_id.id])]
                                    })
                        self.pool['sale.order'].action_confirm(cr, SUPERUSER_ID, [tx.sale_order_id.id], context=dict(context, send_email=True))
                    elif tx.state not in ['cancel', 'error'] and tx.sale_order_id.state == 'draft':
                        _logger.info('<%s> transaction pending/to confirm manually, sending quote email for order %s (ID %s)', acquirer_name, tx.sale_order_id.name, tx.sale_order_id.id)
                        self.pool['sale.order'].force_quotation_send(cr, SUPERUSER_ID, [tx.sale_order_id.id], context=context)
                else:
                    _logger.warning('<%s> transaction MISMATCH for order %s (ID %s)', acquirer_name, tx.sale_order_id.name, tx.sale_order_id.id)
        except Exception:
            _logger.exception('Fail to confirm the order or send the confirmation email%s', tx and ' for the transaction %s' % tx.reference or '')

        return res
