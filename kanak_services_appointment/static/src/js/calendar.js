odoo.define('kanak_services_appointment.kanak_services_appointment', function(require) {
    "use strict";
    var core = require('web.core');
    var CalendarView = require('web_calendar.CalendarView');
    CalendarView.include({
        get_color: function(key) {
            if (this.name = 'Exception Calendar')
                if (this.color_map[key]) {
                    return this.color_map[key];
                }
            var index = (((_.keys(this.color_map).length +
                    1) *
                5) % 24) + 1;
            if (key == 'appointment') {
                index = 'green';
            } else if (key == 'exception') {
                index = 'red';
            }
            this.color_map[key] = index
            return index;
        },

    })
});
