# Copyright (c) 2022, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

month_name = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

def execute(filters=None):
    date_parts = filters.date.split("-")
    year = date_parts[0]
    month = date_parts[1]
    
    columns = get_columns(year, month)
    data = get_data(filters)
    
    return columns, data

def get_columns(year, month):
    return [
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Data", "width": 300},
        {"label": "per {0} {1}".format(month_name[int(month)], year), "fieldname": "ytd", "fieldtype": "Currency", "width": 150},
        {"label": "per {0} {1}".format(month_name[int(month)], int(year) - 1), "fieldname": "py", "fieldtype": "Currency", "width": 150},
        {"label": _("Abweichung Lfd - VJ"), "fieldname": "diff", "fieldtype": "Currency", "width": 150},
        {"label": "", "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]
    
    
def get_data(filters):
    data = []
    data.append({
        'account': "<b>Umsatzerlöse</b>"
    })
    
    revenue_py = 0
    revenue_ytd = 0
    revenue_accounts = ["4000", "4010", "4020", "4022", "4120", "4200", "4210", "4220", "4400", "4405", "4410"]
    for a in revenue_accounts:
        _data = get_row(a, filters.date, filters.company)
        data.append(_data)
        revenue_py += _data['py']
        revenue_ytd += _data['ytd']
    data.append({
        'account': "<b>Betriebsleistung</b>",
        'py': revenue_py,
        'ytd': revenue_ytd,
        'diff': revenue_ytd - revenue_py
    })
    data.append({
        'account': ""
    })
    
    data.append({
        'account': "<b>Wareneinsatz</b>"
    })
    expense_1_py = 0
    expense_1_ytd = 0
    revenue_accounts = ["5050", "5099", "5100", "5110", "5130", "5140", "5199", "5200"]
    for a in revenue_accounts:
        _data = get_row(a, filters.date, filters.company)
        data.append(_data)
        expense_1_py += _data['py']
        expense_1_ytd += _data['ytd']
    data.append({
        'account': "",
        'py': expense_1_py,
        'ytd': expense_1_ytd,
        'diff': expense_1_ytd - expense_1_py
    })
    
    data.append({
        'account': "<b>Materialverbrauch</b>"
    })
    expense_2_py = 0
    expense_2_ytd = 0
    revenue_accounts = ["5800", "5805", "5812", "5300", "5310", "5320", "5340", "5360", "5380", "5390", "5399", "5400", "5440", "5450", "5470", "5621"]
    for a in revenue_accounts:
        _data = get_row(a, filters.date, filters.company)
        data.append(_data)
        expense_2_py += _data['py']
        expense_2_ytd += _data['ytd']
    data.append({
        'account': "",
        'py': expense_2_py,
        'ytd': expense_2_ytd,
        'diff': expense_2_ytd - expense_2_py
    })
    revenue_1_py = revenue_py + expense_1_py + expense_2_py
    revenue_1_ytd = revenue_ytd + expense_1_ytd + expense_2_ytd
    data.append({
        'account': "<b>Rohertrag I</b>",
        'py': revenue_1_py,
        'ytd': revenue_1_ytd,
        'diff': (revenue_1_ytd) - (revenue_1_py)
    })
    
    
    data.append({
        'account': ""
    })
    
    data.append({
        'account': "<b>Personalaufwand</b>"
    })
    salary_py = 0
    salary_ytd = 0
    revenue_accounts = ["6000", "6008", "6010", "6020", "6040", "6200", "6210", "6220", "6230", "6240", "6400", "6402", "6600", "6607", "6620", "6630", "6640", "6790"]
    for a in revenue_accounts:
        _data = get_row(a, filters.date, filters.company)
        data.append(_data)
        salary_py += _data['py']
        salary_ytd += _data['ytd']
    data.append({
        'account': "",
        'py': salary_py,
        'ytd': salary_ytd,
        'diff': salary_ytd - salary_py
    })
    
    revenue_2_py = revenue_1_py + salary_py
    revenue_2_ytd = revenue_1_ytd + salary_ytd
    data.append({
        'account': "<b>Rohertrag II</b>",
        'py': revenue_2_py,
        'ytd': revenue_2_ytd,
        'diff': (revenue_2_ytd) - (revenue_2_py)
    })
    
    data.append({
        'account': ""
    })
    
    data.append({
        'account': "<b>sonstige betriebliche Erträge</b>"
    })
    other_revenue_py = 0
    other_revenue_ytd = 0
    revenue_accounts = ["4809", "4831"]
    for a in revenue_accounts:
        _data = get_row(a, filters.date, filters.company)
        data.append(_data)
        other_revenue_py += _data['py']
        other_revenue_ytd += _data['ytd']
    data.append({
        'account': "",
        'py': other_revenue_py,
        'ytd': other_revenue_ytd,
        'diff': other_revenue_ytd - other_revenue_py
    })
    
    data.append({
        'account': "<b>sonstige betriebliche Aufwendungen</b>"
    })
    other_expense_py = 0
    other_expense_ytd = 0
    revenue_accounts = ["7180", "7201", "7203", "7206", "7210", "7240", "7300", "7321", "7323", "7340", "7360", "7370", "7380", "7381", "7382", "7390", "7400", "7402", "7540", "7600", "7605", "7630", "7650", "7652", "7660", "7662", "7690", "7696", "7700", "7750", "7770", "7782", "7785", "7790", "7800", "4860", "5860"]
    for a in revenue_accounts:
        _data = get_row(a, filters.date, filters.company)
        data.append(_data)
        other_expense_py += _data['py']
        other_expense_ytd += _data['ytd']
    data.append({
        'account': "",
        'py': other_expense_py,
        'ytd': other_expense_ytd,
        'diff': other_expense_ytd - other_expense_py
    })
    
    profit_py = revenue_2_py + other_expense_py
    profit_ytd = revenue_2_ytd + other_expense_ytd
    data.append({
        'account': "<b>Betriebserfolg</b>",
        'py': profit_py,
        'ytd': profit_ytd,
        'diff': (profit_ytd) - (profit_py)
    })
    
    interest_py = 0
    interest_ytd = 0
    revenue_accounts = ["8100", "8280"]
    for a in revenue_accounts:
        _data = get_row(a, filters.date, filters.company)
        data.append(_data)
        interest_py += _data['py']
        interest_ytd += _data['ytd']
    data.append({
        'account': "",
        'py': interest_py,
        'ytd': interest_ytd,
        'diff': interest_ytd - interest_py
    })
    
    data.append({
        'account': ""
    })
    
    data.append({
        'account': "<b>Finanzerfolg</b>"
    })
    
    cashflow_py = profit_py + interest_py
    cashflow_ytd = profit_ytd + interest_ytd
    data.append({
        'account': "<b>Cashflow (vor Steuern)</b>",
        'py': cashflow_py,
        'ytd': cashflow_ytd,
        'diff': (cashflow_ytd) - (cashflow_py)
    })
    
    data.append({
        'account': "<b>Abschreibungen</b>"
    })
    
    depreciation_py = 0
    depreciation_ytd = 0
    revenue_accounts = ["7020", "7050"]
    for a in revenue_accounts:
        _data = get_row(a, filters.date, filters.company)
        data.append(_data)
        depreciation_py += _data['py']
        depreciation_ytd += _data['ytd']
    data.append({
        'account': "",
        'py': depreciation_py,
        'ytd': depreciation_ytd,
        'diff': depreciation_ytd - depreciation_py
    })
    
    financial_result_py = cashflow_py + depreciation_py
    financial_result_ytd = cashflow_ytd + depreciation_ytd
    data.append({
        'account': "<b>Wirtschaftlicher Erfolg</b>",
        'py': financial_result_py,
        'ytd': financial_result_ytd,
        'diff': (financial_result_ytd) - (financial_result_py)
    })
    
    data.append({
        'account': ""
    })
    
    tax_py = 0
    tax_ytd = 0
    revenue_accounts = ["8500"]
    for a in revenue_accounts:
        _data = get_row(a, filters.date, filters.company)
        data.append(_data)
        tax_py += _data['py']
        tax_ytd += _data['ytd']
    data.append({
        'account': "<b>Verlust/Gewinn</b>",
        'py': financial_result_py + tax_py,
        'ytd': financial_result_ytd + tax_ytd,
        'diff': (financial_result_ytd + tax_ytd) - (financial_result_py + tax_py)
    })
    
    return data
    
def get_row(account_code, date, company):
    date_parts = str(date).split("-")
    year = date_parts[0]
    py = int(year) - 1
    month_day = "-{0}-{1}".format(date_parts[1], date_parts[2])
    py_start = "{0}-01-01".format(py)
    py_end = "{0}{1}".format(py, month_day)
    ytd_start = "{0}-01-01".format(year)
    ytd_end = "{0}{1}".format(year, month_day)
    
    py = get_turnover(py_start, py_end, company, account_code)
    ytd = get_turnover(ytd_start, ytd_end, company, account_code)
    try:
        account_name = frappe.get_all("Account", filters={'account_number': account_code}, fields=['name'])[0]['name']
    except:
        return {
            'account': "Account {0} not found".format(account_code),
            'py': 0,
            'ytd': 0,
            'diff': 0
        }
    return {
        'account': account_name,
        'py': py[0]['balance'] if len(py) > 0 else 0,
        'ytd': ytd[0]['balance'] if len(ytd) > 0 else 0,
        'diff': ytd[0]['balance'] - py[0]['balance'] if len(py) > 0 and len(ytd) > 0 else 0
    }
    
def get_turnover_budget_ytd(year, month, accounts, company):
    try:
        amount = frappe.db.sql("""SELECT 
                IFNULL(SUM(`tabMonthly Distribution Percentage`.`percentage_allocation` * `tabBudget Account`.`budget_amount` / 100), 0)
            FROM `tabBudget` 
            LEFT JOIN `tabMonthly Distribution Percentage` ON `tabMonthly Distribution Percentage`.`parent` = `tabBudget`.`monthly_distribution`
            LEFT JOIN `tabBudget Account` ON `tabBudget Account`.`parent` = `tabBudget`.`name`
            LEFT JOIN `tabAccount` ON `tabAccount`.`name` = `tabBudget Account`.`account`
            WHERE 
              `tabBudget`.`fiscal_year` = "{year}"
              AND `tabBudget`.`docstatus` < 2
              AND `tabBudget`.`company` = "{company}"
              AND `tabMonthly Distribution Percentage`.`idx` <= {month}
              AND `tabAccount`.`account_number` IN ({accounts});
                """.format(month=month, year=year, accounts=", ".join(accounts), 
                    last_day=last_day_of_month(year, month), company=company))[0][0]
    except:
        return 0
    return amount

def get_turnover(from_date, to_date, company, account_code):
    sql_query = """
       SELECT *, (`raw`.`credit` - `raw`.`debit`) AS `balance` 
       FROM
       (SELECT 
          `tabAccount`.`name` AS `account`, 
          IFNULL((SELECT 
             ROUND((SUM(`t3`.`debit`)), 2)
           FROM `tabGL Entry` AS `t3`
           WHERE 
             `t3`.`posting_date` <= '{to_date}'
             AND `t3`.`posting_date` >= '{from_date}'
            AND `t3`.`account` = `tabAccount`.`name`
          ), 0) AS `debit`,
          IFNULL((SELECT 
             ROUND((SUM(`t4`.`credit`)), 2)
           FROM `tabGL Entry` AS `t4`
           WHERE 
             `t4`.`posting_date` <= '{to_date}'
             AND `t4`.`posting_date` >= '{from_date}'
            AND `t4`.`account` = `tabAccount`.`name`
          ), 0) AS `credit`
       FROM `tabAccount`
       WHERE 
         `tabAccount`.`is_group` = 0
         AND `tabAccount`.`account_number` = "{account_code}"
         AND `tabAccount`.`company` = "{company}"
       ) AS `raw`
       WHERE (`raw`.`debit` - `raw`.`credit`) != 0;""".format(from_date=from_date, to_date=to_date, company=company, account_code=account_code)
 
    # run query
    data = frappe.db.sql(sql_query, as_dict = True)
    return data

def get_budget_fy(year, company):
    data = frappe.db.sql("""SELECT 
            `tabBudget Account`.`account` AS  `account`,
            IFNULL(`tabBudget Account`.`budget_amount`, 0) AS `amount`
        FROM `tabBudget Account` 
        LEFT JOIN `tabBudget` ON `tabBudget Account`.`parent` = `tabBudget`.`name`
        WHERE 
          `tabBudget`.`fiscal_year` = "{year}"
          AND `tabBudget`.`docstatus` < 2
          AND `tabBudget`.`company` = "{company}";
            """.format(year=year, company=company), as_dict=True)
    return data
