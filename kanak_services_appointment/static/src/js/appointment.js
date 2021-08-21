odoo.define('kanak_services_appointment.appointment', function(require) {
"use strict";

var ajax = require('web.ajax');
var base = require('web_editor.base');
var core = require('web.core');
var qweb = core.qweb;
var website = require('website.website');


    $('.appointment_timezone').on('change', function() {
        $('.appointment_form').submit();
    });
    $('.carousel').carousel('pause');
    var offset = -(new Date().getTimezoneOffset());
    var browser_offset = (offset < 0) ? "-" : "+";
    browser_offset += _.str.sprintf("%02d", Math.abs(offset / 60));
    browser_offset += _.str.sprintf("%02d", Math.abs(offset % 60));
    if (!$('.default_timezone').length) {
        $('.appointment_timezone option[data="' + browser_offset + '"]')
            .prop('selected', true);
        $('.appointment_form').submit();
    }
    var datepickers_options = {
        calendarWeeks: true,
        icons: {
            time: 'fa fa-clock-o',
            date: 'fa fa-calendar',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down'
        },
        pickTime: false,
        defaultDate: new Date(),
    }
    var min_date = $('#jump_min_date').val();
    var max_date = $('#jump_max_date').val();
    if (min_date && max_date) {
        datepickers_options['minDate'] = new Date(min_date)
        datepickers_options['maxDate'] = new Date(max_date)
        datepickers_options['defaultDate'] = new Date(min_date)
    }
    $('.jump_to_date').datetimepicker(datepickers_options).on(
        'dp.change',
        function(e) {
            $('.appointment_form').submit();
        });

    $('#appointment').find('button.kanak-available').on('click', function() {
        var $timezone = $('form select[name=timezone]').val();
        var $date = $(this).data('date');
        var $time = $(this).data('time');
        $('form input[name=date]').val($date);
        $('form input[name=time]').val($time);
        $('form input[name=timezone]').val($timezone);

        $('form.services_form_cart').submit();
    });

    $('a[href="/shop/checkout"]').on('click', function(event) {
        event.preventDefault();
        var notes = $('textarea#order_note').val();
        console.log("note..", notes);
        var redirect = $(this).attr('href');
        if(notes) {
            ajax.jsonRpc("/shop/order_note", 'call', {
                'order': $('textarea#order_note').data('so'),
                'note': notes,
            }).then(function (result) {
                console.log($(result));
                window.location = redirect;
            });
        } else {
            window.location = redirect;
        }
    });
});
