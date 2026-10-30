"""Company → Action → HRMS Settings setup (idempotent)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from vsd_hr_customizations.hrms_setup.fixtures import (
	HRMS_DEFAULT_EMPLOYMENT_TYPES,
	HRMS_DEFAULT_LEAVE_TYPES,
	LEAVE_TYPES,
	SSA_CUSTOM_FIELDS,
	TARGET_EMPLOYMENT_TYPES,
	get_payroll_accounts,
	get_salary_components,
	get_salary_structures,
)


@frappe.whitelist()
def apply_hrms_settings(company: str) -> str:
	"""Create HRMS bootstrap masters for a company if they do not already exist."""
	if not company:
		frappe.throw(_("Company is required"))

	if not frappe.db.exists("Company", company):
		frappe.throw(_("Company {0} does not exist").format(company))

	frappe.only_for("System Manager")

	abbr = frappe.db.get_value("Company", company, "abbr")
	if not abbr:
		frappe.throw(_("Company abbreviation is missing for {0}").format(company))

	summary = {
		"custom_fields": 0,
		"employment_types_created": 0,
		"employment_types_removed": 0,
		"leave_types_created": 0,
		"leave_types_removed": 0,
		"accounts": 0,
		"salary_components": 0,
		"salary_structures": 0,
		"skipped": [],
	}

	summary["custom_fields"] = _ensure_custom_fields()
	created, removed = _ensure_employment_types()
	summary["employment_types_created"] = created
	summary["employment_types_removed"] = removed
	lt_created, lt_removed = _ensure_leave_types(summary["skipped"])
	summary["leave_types_created"] = lt_created
	summary["leave_types_removed"] = lt_removed
	summary["accounts"] = _ensure_accounts(company, abbr, summary["skipped"])
	summary["salary_components"] = _ensure_salary_components(company, abbr, summary["skipped"])
	currency = frappe.db.get_value("Company", company, "default_currency") or "TZS"
	summary["salary_structures"] = _ensure_salary_structures(company, currency, summary["skipped"])

	frappe.db.commit()
	return _format_summary(summary)


def _ensure_custom_fields() -> int:
	before = frappe.db.count(
		"Custom Field",
		{
			"dt": "Salary Structure Assignment",
			"fieldname": (
				"in",
				["custom_position_pay", "custom_deduct_nhif", "custom_deduct_heslb"],
			),
		},
	)
	create_custom_fields(SSA_CUSTOM_FIELDS, update=False)
	after = frappe.db.count(
		"Custom Field",
		{
			"dt": "Salary Structure Assignment",
			"fieldname": (
				"in",
				["custom_position_pay", "custom_deduct_nhif", "custom_deduct_heslb"],
			),
		},
	)
	return max(after - before, 0)


def _ensure_employment_types() -> tuple[int, int]:
	created = 0
	removed = 0

	for name in TARGET_EMPLOYMENT_TYPES:
		if frappe.db.exists("Employment Type", name):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Employment Type",
				"employee_type_name": name,
			}
		)
		doc.insert(ignore_permissions=True)
		created += 1

	for name in HRMS_DEFAULT_EMPLOYMENT_TYPES:
		if not frappe.db.exists("Employment Type", name):
			continue
		if frappe.db.exists("Employee", {"employment_type": name}):
			continue
		try:
			frappe.delete_doc("Employment Type", name, ignore_permissions=True, force=True)
			removed += 1
		except Exception:
			frappe.log_error(
				title=f"Could not delete Employment Type {name}",
				message=frappe.get_traceback(),
			)

	return created, removed


def _ensure_leave_types(skipped: list[str]) -> tuple[int, int]:
	created = 0
	removed = 0
	for row in LEAVE_TYPES:
		name = row["leave_type_name"]
		if frappe.db.exists("Leave Type", name):
			skipped.append(f"Leave Type: {name}")
			continue
		doc = frappe.get_doc({"doctype": "Leave Type", **row})
		doc.insert(ignore_permissions=True)
		created += 1

	for name in HRMS_DEFAULT_LEAVE_TYPES:
		if not frappe.db.exists("Leave Type", name):
			continue
		# Keep if already used on leave allocations / applications / policies
		in_use = (
			frappe.db.exists("Leave Allocation", {"leave_type": name})
			or frappe.db.exists("Leave Application", {"leave_type": name})
			or frappe.db.exists("Leave Policy Detail", {"leave_type": name})
		)
		if in_use:
			skipped.append(f"Leave Type (in use, not removed): {name}")
			continue
		try:
			frappe.delete_doc("Leave Type", name, ignore_permissions=True, force=True)
			removed += 1
		except Exception:
			frappe.log_error(
				title=f"Could not delete Leave Type {name}",
				message=frappe.get_traceback(),
			)

	return created, removed


def _find_account(company: str, account_name: str, *, is_group: int | None = None) -> str | None:
	"""Resolve Account.name by account_name + company (supports numbered COA names)."""
	filters = {"account_name": account_name, "company": company}
	if is_group is not None:
		filters["is_group"] = is_group
	return frappe.db.get_value("Account", filters, "name")


def _ensure_accounts(company: str, abbr: str, skipped: list[str]) -> int:
	created = 0
	for row in get_payroll_accounts(abbr):
		account_name = row["account_name"]
		if _find_account(company, account_name):
			skipped.append(f"Account: {account_name}")
			continue

		parent_name = row["parent_account_name"]
		parent = _find_account(company, parent_name, is_group=1)
		if not parent:
			# fallback: some templates use non-group naming quirks
			parent = _find_account(company, parent_name)
		if not parent:
			frappe.throw(
				_(
					"Parent account '{0}' not found for company {1}. Please create Chart of Accounts first."
				).format(parent_name, company)
			)

		doc = frappe.get_doc(
			{
				"doctype": "Account",
				"account_name": account_name,
				"parent_account": parent,
				"company": company,
				"is_group": 0,
				"account_type": row.get("account_type") or "",
			}
		)
		doc.insert(ignore_permissions=True)
		created += 1
	return created


def _ensure_salary_components(company: str, abbr: str, skipped: list[str]) -> int:
	created = 0
	# Keep formula-driven statutory components free of payment-days doubling.
	force_no_payment_days = {
		"NHIF Expense",
		"NHIF Employer",
		"ZHSF Expense",
		"ZHSF Employer",
	}

	for row in get_salary_components(company, abbr):
		name = row["salary_component"]
		if frappe.db.exists("Salary Component", name):
			if name in force_no_payment_days:
				frappe.db.set_value(
					"Salary Component",
					name,
					"depends_on_payment_days",
					0,
					update_modified=False,
				)
			# Correct known wrong default: Staff Loan must use Staff Loan asset account
			if name == "Staff Loan":
				_sync_component_account(company, name, row.get("account"))
			skipped.append(f"Salary Component: {name}")
			continue

		account_name = row.get("account")
		accounts = []
		if account_name:
			account = _find_account(company, account_name)
			if not account:
				frappe.throw(
					_("Account '{0}' is required for Salary Component {1}").format(account_name, name)
				)
			accounts = [{"company": company, "account": account}]

		doc = frappe.get_doc(
			{
				"doctype": "Salary Component",
				"salary_component": name,
				"salary_component_abbr": row["salary_component_abbr"],
				"type": row["type"],
				"depends_on_payment_days": row.get("depends_on_payment_days", 0),
				"is_tax_applicable": row.get("is_tax_applicable", 0),
				"is_income_tax_component": row.get("is_income_tax_component", 0),
				"do_not_include_in_total": row.get("do_not_include_in_total", 0),
				"remove_if_zero_valued": row.get("remove_if_zero_valued", 1),
				"accounts": accounts,
			}
		)
		doc.insert(ignore_permissions=True)
		created += 1
	return created


def _sync_component_account(company: str, component: str, account_name: str | None) -> None:
	"""Keep company account mapping aligned (e.g. Staff Loan → Staff Loan account)."""
	if not account_name:
		return
	account = _find_account(company, account_name)
	if not account:
		return

	existing = frappe.db.get_value(
		"Salary Component Account",
		{"parent": component, "company": company},
		["name", "account"],
		as_dict=True,
	)
	if existing:
		if existing.account != account:
			frappe.db.set_value(
				"Salary Component Account",
				existing.name,
				"account",
				account,
				update_modified=False,
			)
		return

	doc = frappe.get_doc("Salary Component", component)
	doc.append("accounts", {"company": company, "account": account})
	doc.save(ignore_permissions=True)


def _ensure_salary_structures(company: str, currency: str, skipped: list[str]) -> int:
	created = 0
	for structure in get_salary_structures():
		name = structure["name"]
		if frappe.db.exists("Salary Structure", name):
			skipped.append(f"Salary Structure: {name}")
			continue

		doc = frappe.new_doc("Salary Structure")
		doc.name = name
		doc.company = company
		doc.is_active = structure["is_active"]
		doc.payroll_frequency = structure["payroll_frequency"]
		doc.currency = currency

		for earning in structure["earnings"]:
			doc.append("earnings", earning)
		for deduction in structure["deductions"]:
			doc.append("deductions", deduction)

		doc.insert(ignore_permissions=True)
		doc.submit()
		created += 1
	return created


def _format_summary(summary: dict) -> str:
	lines = [
		_("HRMS Settings completed (idempotent)."),
		_("Custom fields created: {0}").format(summary["custom_fields"]),
		_("Employment types created: {0}, removed defaults: {1}").format(
			summary["employment_types_created"], summary["employment_types_removed"]
		),
		_("Leave types created: {0}, removed defaults: {1}").format(
			summary["leave_types_created"], summary["leave_types_removed"]
		),
		_("Accounts created: {0}").format(summary["accounts"]),
		_("Salary components created: {0}").format(summary["salary_components"]),
		_("Salary structures created: {0}").format(summary["salary_structures"]),
	]
	skipped_count = len(summary["skipped"])
	if skipped_count:
		lines.append(_("Already existed / skipped: {0}").format(skipped_count))
	return "<br>".join(lines)
