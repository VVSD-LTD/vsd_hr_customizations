"""Static fixtures used by Company → Action → HRMS Settings."""

from __future__ import annotations

HRMS_DEFAULT_EMPLOYMENT_TYPES = [
	"Full-time",
	"Part-time",
	"Probation",
	"Contract",
	"Commission",
	"Piecework",
	"Intern",
	"Apprentice",
]

TARGET_EMPLOYMENT_TYPES = ["Primary", "Secondary"]

# HRMS ships a default "Sick Leave"; Emirates uses Sick Leave Full / Half instead.
HRMS_DEFAULT_LEAVE_TYPES = ["Sick Leave"]

SSA_CUSTOM_FIELDS = {
	"Salary Structure Assignment": [
		{
			"fieldname": "custom_position_pay",
			"label": "Position Pay",
			"fieldtype": "Currency",
			"insert_after": "base",
		},
		{
			"fieldname": "custom_deduct_nhif",
			"label": "Deduct NHIF",
			"fieldtype": "Check",
			"insert_after": "custom_position_pay",
		},
		{
			"fieldname": "custom_deduct_heslb",
			"label": "Deduct HESLB",
			"fieldtype": "Check",
			"insert_after": "leave_encashment_amount_per_day",
		},
	]
}

LEAVE_TYPES = [
	{
		"leave_type_name": "Annual Leave",
		"applicable_after": 30,
		"max_continuous_days_allowed": 28,
		"is_carry_forward": 1,
		"include_holiday": 1,
		"maximum_carry_forwarded_leaves": 28,
		"expire_carry_forwarded_leaves_after_days": 180,
		"rounding": "0.5",
	},
	{
		"leave_type_name": "Casual Leave",
		"max_continuous_days_allowed": 3,
		"is_carry_forward": 1,
		"include_holiday": 1,
		"allow_encashment": 1,
	},
	{
		"leave_type_name": "Sick Leave Full",
		"max_continuous_days_allowed": 63,
		"rounding": "0.5",
	},
	{
		"leave_type_name": "Sick Leave Half",
		"max_continuous_days_allowed": 63,
		"is_ppl": 1,
		"fraction_of_daily_salary_per_leave": 0.5,
		"allow_negative": 1,
		"allow_over_allocation": 1,
		"include_holiday": 1,
		"rounding": "0.5",
	},
	{
		"leave_type_name": "Maternity Leave",
		"max_continuous_days_allowed": 84,
		"rounding": "0.5",
	},
	{
		"leave_type_name": "Maternity Leave Twins",
		"max_continuous_days_allowed": 100,
		"rounding": "0.5",
	},
	{
		"leave_type_name": "Post Maternity Leave",
		"max_continuous_days_allowed": 84,
		"is_optional_leave": 1,
		"rounding": "0.5",
	},
	{
		"leave_type_name": "Paternity Leave",
		"max_continuous_days_allowed": 3,
		"is_optional_leave": 1,
		"rounding": "0.5",
	},
	{
		"leave_type_name": "Compassionate Leave",
		"max_continuous_days_allowed": 4,
		"rounding": "0.5",
	},
	{
		"leave_type_name": "Leave Without Pay",
		"is_lwp": 1,
		"include_holiday": 1,
	},
	{
		"leave_type_name": "Compensatory Off",
		"include_holiday": 1,
		"is_compensatory": 1,
	},
	{
		"leave_type_name": "Privilege Leave",
		"include_holiday": 1,
	},
]


def get_payroll_accounts(abbr: str) -> list[dict]:
	"""Accounts required before salary components (plus Salary expense).

	parent_account_name is matched by Account.account_name so numbered COA
	templates (e.g. '2100 - Accounts Payable - ABBR') work.
	"""
	_ = abbr  # kept for call-site compatibility
	return [
		# Liabilities
		{"account_name": "ZSSF Payable", "parent_account_name": "Accounts Payable"},
		{"account_name": "ZHSF - Payable", "parent_account_name": "Accounts Payable"},
		{"account_name": "SACCOS Payable", "parent_account_name": "Accounts Payable"},
		{"account_name": "HESLB Payable", "parent_account_name": "Accounts Payable"},
		{"account_name": "NHIF - Payable", "parent_account_name": "Accounts Payable"},
		{"account_name": "NSSF Payable", "parent_account_name": "Accounts Payable"},
		{"account_name": "PAYE - Payable", "parent_account_name": "Accounts Payable"},
		{
			"account_name": "Skills and Development Levy (SDL) - Payable",
			"parent_account_name": "Accounts Payable",
		},
		{
			"account_name": "Workers Compensation Fund (WCF) - Payable",
			"parent_account_name": "Accounts Payable",
		},
		# Expenses
		{
			"account_name": "ZSSF Expenses",
			"account_type": "Indirect Expense",
			"parent_account_name": "Indirect Expenses",
		},
		{
			"account_name": "ZHSF Contribution Expense",
			"account_type": "Indirect Expense",
			"parent_account_name": "Indirect Expenses",
		},
		{
			"account_name": "NHIF Contribution Expense",
			"account_type": "Expense Account",
			"parent_account_name": "Indirect Expenses",
		},
		{
			"account_name": "NSSF Expenses",
			"account_type": "Expense Account",
			"parent_account_name": "Indirect Expenses",
		},
		{
			"account_name": "Skills and Development Levy (SDL) Expenses",
			"account_type": "Expense Account",
			"parent_account_name": "Indirect Expenses",
		},
		{
			"account_name": "Worker Compensation Fund (WCF) Expenses",
			"parent_account_name": "Indirect Expenses",
		},
		{
			"account_name": "Salary",
			"parent_account_name": "Indirect Expenses",
		},
		# Assets
		{"account_name": "Staff Loan", "parent_account_name": "Loans and Advances (Assets)"},
		{
			"account_name": "Staff Loan - Receivable",
			"parent_account_name": "Loans and Advances (Assets)",
		},
		{
			"account_name": "Employee Advances",
			"account_type": "Payable",
			"parent_account_name": "Loans and Advances (Assets)",
		},
	]


def get_salary_components(company: str, abbr: str) -> list[dict]:
	_ = abbr
	salary = "Salary"
	return [
		# Earnings
		_comp("Basic", "B", "Earning", salary, company, depends_on_payment_days=1, is_tax_applicable=1),
		_comp(
			"POSITION PAY",
			"PPAY",
			"Earning",
			salary,
			company,
			depends_on_payment_days=1,
			is_tax_applicable=1,
		),
		_comp(
			"Housing Allowance",
			"HOUSING",
			"Earning",
			salary,
			company,
			depends_on_payment_days=1,
			is_tax_applicable=1,
		),
		_comp("Arrear", "A", "Earning", salary, company, depends_on_payment_days=1, is_tax_applicable=1),
		_comp("Bonus", "BONUS", "Earning", salary, company, is_tax_applicable=1),
		_comp("Fuel Allowance", "FUEL", "Earning", salary, company, is_tax_applicable=1),
		_comp(
			"Leave Encashment",
			"LE",
			"Earning",
			salary,
			company,
			depends_on_payment_days=1,
			is_tax_applicable=1,
		),
		_comp("Meal Allowance", "MEAL", "Earning", salary, company, is_tax_applicable=1),
		_comp("Medical Allowance", "MED", "Earning", salary, company, is_tax_applicable=1),
		_comp("Notice Pay in Liue", "NOTICE", "Earning", salary, company, is_tax_applicable=1),
		_comp(
			"Severance Allowance",
			"SEVERANCE",
			"Earning",
			salary,
			company,
			depends_on_payment_days=1,
			is_tax_applicable=1,
		),
		_comp(
			"Transport Allowance",
			"TRANSPORT",
			"Earning",
			salary,
			company,
			depends_on_payment_days=1,
			is_tax_applicable=1,
		),
		_comp(
			"Travelling Allowance",
			"TRAVEL",
			"Earning",
			salary,
			company,
			depends_on_payment_days=1,
			is_tax_applicable=1,
		),
		_comp("Night Allowance", "NGTALLOWA", "Earning", salary, company, is_tax_applicable=1),
		_comp("Overtime Holiday", "OVH", "Earning", salary, company, is_tax_applicable=1),
		_comp("Overtime Normal", "OVN", "Earning", salary, company, is_tax_applicable=1),
		_comp(
			"NHIF Expense",
			"NHIFExp",
			"Earning",
			"NHIF Contribution Expense",
			company,
			depends_on_payment_days=0,
			is_tax_applicable=1,
			do_not_include_in_total=1,
		),
		_comp(
			"NSSF Expense",
			"NSSFExp",
			"Earning",
			"NSSF Expenses",
			company,
			do_not_include_in_total=1,
		),
		_comp(
			"SDL Expense",
			"SDLExp",
			"Earning",
			"Skills and Development Levy (SDL) Expenses",
			company,
			do_not_include_in_total=1,
		),
		_comp(
			"WCF Expense",
			"WCFExp",
			"Earning",
			"Worker Compensation Fund (WCF) Expenses",
			company,
			do_not_include_in_total=1,
		),
		_comp(
			"ZSSF Expense",
			"ZSSFExp",
			"Earning",
			"ZSSF Expenses",
			company,
			do_not_include_in_total=1,
		),
		_comp(
			"ZHSF Expense",
			"ZHSFExp",
			"Earning",
			"ZHSF Contribution Expense",
			company,
			depends_on_payment_days=0,
			is_tax_applicable=1,
			do_not_include_in_total=1,
		),
		# Deductions
		_comp("Advance", "ADV", "Deduction", "Staff Loan - Receivable", company),
		_comp("NSSF", "NSSF", "Deduction", "NSSF Payable", company),
		_comp(
			"NSSF Employer",
			"NSSFEmp",
			"Deduction",
			"NSSF Payable",
			company,
			do_not_include_in_total=1,
		),
		_comp("NHIF", "NHIF", "Deduction", "NHIF - Payable", company, is_tax_applicable=1),
		_comp(
			"NHIF Employer",
			"NHIFEmp",
			"Deduction",
			"NHIF - Payable",
			company,
			depends_on_payment_days=0,
			do_not_include_in_total=1,
		),
		_comp("PAYE", "PAYE", "Deduction", "PAYE - Payable", company, is_tax_applicable=1),
		_comp(
			"HESLB Deducation",
			"HESLB",
			"Deduction",
			"HESLB Payable",
			company,
			is_tax_applicable=1,
		),
		_comp(
			"SDL",
			"SDL",
			"Deduction",
			"Skills and Development Levy (SDL) - Payable",
			company,
			do_not_include_in_total=1,
		),
		_comp(
			"WCF",
			"WCF",
			"Deduction",
			"Workers Compensation Fund (WCF) - Payable",
			company,
			do_not_include_in_total=1,
		),
		_comp("ZSSF", "ZSSF", "Deduction", "ZSSF Payable", company),
		_comp(
			"ZSSF Employer",
			"ZSSFEmp",
			"Deduction",
			"ZSSF Payable",
			company,
			do_not_include_in_total=1,
		),
		_comp("ZHSF", "ZHSF", "Deduction", "ZHSF - Payable", company, is_tax_applicable=1),
		_comp(
			"ZHSF Employer",
			"ZHSFEmp",
			"Deduction",
			"ZHSF - Payable",
			company,
			depends_on_payment_days=0,
			do_not_include_in_total=1,
		),
		_comp(
			"SACCOS",
			"SACCOS",
			"Deduction",
			"SACCOS Payable",
			company,
			depends_on_payment_days=1,
		),
		_comp("Other Deduction", "ODed", "Deduction", salary, company),
		_comp("Staff Loan", "Staff Loan", "Deduction", "Staff Loan", company),
		_comp(
			"Salary Advance",
			"ADVANCE",
			"Deduction",
			"Employee Advances",
			company,
		),
		{
			"salary_component": "Income Tax",
			"salary_component_abbr": "IT",
			"type": "Deduction",
			"depends_on_payment_days": 1,
			"is_tax_applicable": 1,
			"is_income_tax_component": 1,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 1,
			"account": None,
			"company": company,
		},
	]


def _comp(
	name: str,
	abbr: str,
	comp_type: str,
	account: str,
	company: str,
	*,
	depends_on_payment_days: int = 0,
	is_tax_applicable: int = 0,
	do_not_include_in_total: int = 0,
) -> dict:
	return {
		"salary_component": name,
		"salary_component_abbr": abbr,
		"type": comp_type,
		"depends_on_payment_days": depends_on_payment_days,
		"is_tax_applicable": is_tax_applicable,
		"do_not_include_in_total": do_not_include_in_total,
		"remove_if_zero_valued": 1,
		"account": account,
		"company": company,
	}


def _row(
	component: str,
	*,
	formula: str | None = None,
	condition: str = "",
	amount_based_on_formula: int | None = None,
	depends_on_payment_days: int | None = None,
	is_tax_applicable: int | None = None,
	do_not_include_in_total: int | None = None,
) -> dict:
	row = {"salary_component": component, "condition": condition or ""}
	if formula is not None:
		row["formula"] = formula
		row["amount_based_on_formula"] = 1 if amount_based_on_formula is None else amount_based_on_formula
	elif amount_based_on_formula is not None:
		row["amount_based_on_formula"] = amount_based_on_formula
	if depends_on_payment_days is not None:
		row["depends_on_payment_days"] = depends_on_payment_days
	if is_tax_applicable is not None:
		row["is_tax_applicable"] = is_tax_applicable
	if do_not_include_in_total is not None:
		row["do_not_include_in_total"] = do_not_include_in_total
	return row


def get_salary_structures() -> list[dict]:
	mainland_earnings = [
		_row("Basic", formula="base", depends_on_payment_days=1, is_tax_applicable=1),
		_row("POSITION PAY", formula="custom_position_pay", depends_on_payment_days=1, is_tax_applicable=1),
		_row("Housing Allowance", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Arrear", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Bonus", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Fuel Allowance", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Leave Encashment", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Meal Allowance", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Medical Allowance", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Notice Pay in Liue", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Severance Allowance", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Transport Allowance", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Travelling Allowance", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Night Allowance", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row(
			"NHIF Expense",
			formula="B * (3 / 100)",
			condition="custom_deduct_nhif == 1",
			depends_on_payment_days=0,
			is_tax_applicable=1,
			do_not_include_in_total=1,
		),
		_row("SDL Expense", formula="gross_pay * (3.5 / 100)", do_not_include_in_total=1),
		_row("WCF Expense", formula="gross_pay * (0.5 / 100)", do_not_include_in_total=1),
		_row("NSSF Expense", formula="gross_pay * (10 / 100)", do_not_include_in_total=1),
	]

	mainland_deductions = [
		_row("Advance", amount_based_on_formula=0),
		_row("NSSF", formula="gross_pay * (10 / 100)"),
		_row(
			"NHIF Employer",
			formula="B * (3/100)",
			condition="custom_deduct_nhif == 1",
			depends_on_payment_days=0,
			do_not_include_in_total=1,
		),
		_row(
			"PAYE",
			formula="((gross_pay - NSSF) - 270000) * 0.08",
			condition="((gross_pay - NSSF) > 270000) and ((gross_pay - NSSF) <= 520000) and (employment_type != 'Secondary')",
			is_tax_applicable=1,
		),
		_row(
			"PAYE",
			formula="(((gross_pay - NSSF) - 520000) * 0.2) + 20000",
			condition="((gross_pay - NSSF) > 520000) and ((gross_pay - NSSF) <= 760000) and (employment_type != 'Secondary')",
			is_tax_applicable=1,
		),
		_row(
			"PAYE",
			formula="(((gross_pay - NSSF) - 760000) * 0.25) + 68000",
			condition="((gross_pay - NSSF) > 760000) and ((gross_pay - NSSF) <= 1000000) and (employment_type != 'Secondary')",
			is_tax_applicable=1,
		),
		_row(
			"PAYE",
			formula="(((gross_pay - NSSF) - 1000000) * 0.3) + 128000",
			condition="((gross_pay - NSSF) > 1000000) and (employment_type != 'Secondary')",
			is_tax_applicable=1,
		),
		_row(
			"PAYE",
			formula="(gross_pay - NSSF) * 0.3",
			condition="employment_type == 'Secondary'",
			is_tax_applicable=1,
		),
		_row("NSSF Employer", formula="gross_pay * (10 / 100)", do_not_include_in_total=1),
		_row(
			"NHIF",
			formula="B * (3 / 100)",
			condition="custom_deduct_nhif == 1",
			is_tax_applicable=1,
		),
		_row("SDL", formula="gross_pay * (3.5 / 100)", do_not_include_in_total=1),
		_row("WCF", formula="gross_pay * (0.5 / 100)", do_not_include_in_total=1),
		_row(
			"HESLB Deducation",
			formula="B * (15 / 100)",
			condition="custom_deduct_heslb == 1",
			is_tax_applicable=1,
		),
	]

	zanzibar_earnings = [
		_row("Basic", formula="base", depends_on_payment_days=1, is_tax_applicable=1),
		_row("POSITION PAY", formula="custom_position_pay", depends_on_payment_days=1, is_tax_applicable=1),
		_row("Housing Allowance", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Arrear", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Bonus", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Fuel Allowance", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Leave Encashment", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Meal Allowance", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Medical Allowance", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Notice Pay in Liue", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("Severance Allowance", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Transport Allowance", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Travelling Allowance", amount_based_on_formula=0, depends_on_payment_days=1, is_tax_applicable=1),
		_row("Night Allowance", amount_based_on_formula=0, depends_on_payment_days=0, is_tax_applicable=1),
		_row("SDL Expense", formula="gross_pay * (4 / 100)", do_not_include_in_total=1),
		_row("ZSSF Expense", formula="gross_pay * (14 / 100)", do_not_include_in_total=1),
		_row(
			"ZHSF Expense",
			formula="base * (3.5 / 100)",
			condition="custom_deduct_nhif == 1",
			depends_on_payment_days=0,
			is_tax_applicable=1,
			do_not_include_in_total=1,
		),
	]

	zanzibar_deductions = [
		_row("Advance", amount_based_on_formula=0),
		_row("ZSSF", formula="gross_pay * (7 / 100)"),
		_row(
			"PAYE",
			formula="((gross_pay - ZSSF) - 270000) * 0.08",
			condition="((gross_pay - ZSSF) > 270000) and ((gross_pay - ZSSF) <= 520000) and (employment_type != 'Secondary')",
			is_tax_applicable=1,
		),
		_row(
			"PAYE",
			formula="(((gross_pay - ZSSF) - 520000) * 0.2) + 20000",
			condition="((gross_pay - ZSSF) > 520000) and ((gross_pay - ZSSF) <= 760000) and (employment_type != 'Secondary')",
			is_tax_applicable=1,
		),
		_row(
			"PAYE",
			formula="(((gross_pay - ZSSF) - 760000) * 0.25) + 68000",
			condition="((gross_pay - ZSSF) > 760000) and ((gross_pay - ZSSF) <= 1000000) and (employment_type != 'Secondary')",
			is_tax_applicable=1,
		),
		_row(
			"PAYE",
			formula="(((gross_pay - ZSSF) - 1000000) * 0.3) + 128000",
			condition="((gross_pay - ZSSF) > 1000000) and (employment_type != 'Secondary')",
			is_tax_applicable=1,
		),
		_row(
			"PAYE",
			formula="(gross_pay - ZSSF) * 0.3",
			condition="employment_type == 'Secondary'",
			is_tax_applicable=1,
		),
		_row("ZSSF Employer", formula="gross_pay * (14 / 100)", do_not_include_in_total=1),
		_row("SDL", formula="gross_pay * (4 / 100)", do_not_include_in_total=1),
		_row(
			"ZHSF",
			formula="base * (3.5/100)",
			condition="custom_deduct_nhif == 1",
			is_tax_applicable=1,
		),
		_row(
			"ZHSF Employer",
			formula="base * (3.5/100)",
			condition="custom_deduct_nhif == 1",
			depends_on_payment_days=0,
			do_not_include_in_total=1,
		),
	]

	return [
		{
			"name": "Tanzania Mainland Salary Structure",
			"is_active": "Yes",
			"payroll_frequency": "Monthly",
			"currency": "TZS",
			"earnings": mainland_earnings,
			"deductions": mainland_deductions,
		},
		{
			"name": "Zanzibar Salary Structure",
			"is_active": "No",
			"payroll_frequency": "Monthly",
			"currency": "TZS",
			"earnings": zanzibar_earnings,
			"deductions": zanzibar_deductions,
		},
	]
