// Copyright (c) 2020-2022, libracore and contributors
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
            "fieldname":"item",
            "label": __("Item"),
            "fieldtype": "Data",
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
        report.page.add_inner_button(__('Automatically plan all'), function () {
           auto_plan_all();
        });
        report.page.add_inner_button(__('Update Material'), function () {
            frappe.call({
                "method": "hoh.hoh.report.stickplan.stickplan.update_material_status",
                "callback": function(response) {
                    frappe.show_alert( __("Updated") );
                    frappe.query_report.refresh();
                }
            });
        });
    },
    "initial_depth": 0
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
            {'fieldname': 'maschine', 'fieldtype': 'Link', 'options': 'Stickmaschine', 
             'label': __('Stickmaschine'), 'read_only': 0, 'default': wo.stickmaschine},
            {'fieldname': 'start_date', 'fieldtype': 'Datetime', 'default': wo.planned_start_date,
             'label': __('Start Date')  },
            {'fieldname': 'earlier_date', 'fieldtype': 'Datetime', 'default': wo.previous_date,
             'label': __('Earlier Date') , 'read_only': 1 },
            {'fieldname': 'later_date', 'fieldtype': 'Datetime', 'default': wo.next_date,
             'label': __('Later Date') , 'read_only': 1 },
            {'fieldname': 'btn_earlier', 'fieldtype': 'Button', 'label': __('Earlier'),
             'click': function() {
                 var earlier = new Date(d.get_value('earlier_date'));
                 var before_earlier = new Date(earlier - 60000);
                 d.set_value('start_date',  before_earlier)  ;
              }  },
            {'fieldname': 'all_sales_order', 'fieldtype': 'Check', 'label': __('Apply to complete sales order'), 'default': 1 },
        ],
        primary_action: function(){
            d.hide();
            replan_work_order(d.get_values());
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

function auto_plan_all() {
    frappe.call({
        'method': 'frappe.client.get_list',
        'args': {
            'doctype': 'Stickmaschine',
            'fields': ['name'],
        },
        'callback': function(response) {
            var machines = response.message;
            for (var i = 0; i < machines.length; i++) {
                plan_machine(machines[i]['name']);
            }
        }
    });
}

function plan_machine(machine) {
    frappe.call({
        "method": "hoh.hoh.report.stickplan.stickplan.plan_machine",
        "args": {
            "machine": machine
        },
        "callback": function(response) {
            frappe.show_alert( __("Updated") + " " + machine);
            frappe.query_report.refresh();
        }
    });
}

function replan_work_order(values) {
    frappe.call({
        "method": "hoh.hoh.report.stickplan.stickplan.replan_work_order",
        "args": {
            'work_order': values.work_order,
            'sales_order': values.sales_order,
            'maschine': values.maschine,
            'target_date': values.start_date,
            'all_sales_order': values.all_sales_order
        },
        "callback": function(response) {
            frappe.show_alert( __("Replanned") );
            frappe.query_report.refresh()
        }
    });
}
