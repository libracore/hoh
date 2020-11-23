// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stickplan"] = {
    "filters": [
        {
            "fieldname":"stickmaschine",
            "label": __("Stickmaschine"),
            "fieldtype": "Link",
            "options": "Stickmaschine"
        },
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "width": "60px"
        },
                {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), +12),
            "width": "60px"
        },
                {
            "fieldname":"sales_order",
            "label": __("Sales Order"),
            "fieldtype": "Link",
            "options": "Sales Order"
        },
        {
            "fieldname":"item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item"
        }
    ],
    "onload": (report) => {
        report.page.add_inner_button(__('Work Order List'), function () {
           window.location.href="/desk#List/Work Order/List";
        });
        report.page.add_inner_button(__('Automatically plan'), function () {
           auto_plan();
        });
        report.page.add_inner_button(__('Update Material'), function () {
            frappe.call({
                "method": "hoh.hoh.report.stickplan.stickplan.update_material_status",
                "callback": function(response) {
                    frappe.show_alert( __("Updated") );
                }
            });
        });
    }
};

/* add event listener for double clicks to move up */
cur_page.container.addEventListener("dblclick", function(event) {
    var content = strip_html_tags(event.target.innerHTML).trim();
    if (content.startsWith("WO-")) {
        get_wo_details(content);
    }
});

function strip_html_tags(str)
{
   if ((str===null) || (str===''))
       return false;
   else
   str = str.toString();
  return str.replace(/<[^>]*>/g, '');
}

function get_wo_details(work_order) {
    frappe.call({
        "method": "hoh.hoh.report.stickplan.stickplan.get_planning_wo",
        "args": {
            "wo": work_order
        },
        "callback": function(response) {
            var wo = response.message;
            show_planning_dialog(wo);
        }
    });
}

function show_planning_dialog(wo) {
    console.log(wo);
    var d = new frappe.ui.Dialog({
        'title': __('Planning'),
        'fields': [
            {'fieldname': 'work_order', 'fieldtype': 'Link', 'options': 'Work Order', 
             'label': __('Work Order'), 'read_only': 1, 'default': wo.work_order},
            {'fieldname': 'sales_order', 'fieldtype': 'Link', 'options': 'Sales Order', 
             'label': __('Sales Order'), 'read_only': 1, 'default': wo.sales_order},
            {'fieldname': 'start_date', 'fieldtype': 'Datetime', 'default': wo.planned_start_date,
             'label': __('Start Date')  },
            {'fieldname': 'earlier_date', 'fieldtype': 'Datetime', 'default': wo.previous_date,
             'label': __('Earlier Date') , 'read_only': 1 },
            {'fieldname': 'later_date', 'fieldtype': 'Datetime', 'default': wo.next_date,
             'label': __('Later Date') , 'read_only': 1 }
        ],
        primary_action: function(){
            d.hide();
            show_alert(d.get_values());
        },
        primary_action_label: __('Plan')
    });
    d.show();
}

function auto_plan() {
    frappe.prompt([
        {'fieldname': 'machine', 'fieldtype': 'Link', 'label': __('Machine'), 'reqd': 1, 'options': 'Stickmaschine'}  
    ],
    function(values){
        plan_machine(values.machine);
    },
    __('Select machine'),
    __('Plan')
    );
}

function plan_machine(machine) {
    frappe.call({
        "method": "hoh.hoh.report.stickplan.stickplan.plan_machine",
        "args": {
            "machine": machine
        },
        "callback": function(response) {
            frappe.show_alert( __("Updated") );
        }
    });
}
