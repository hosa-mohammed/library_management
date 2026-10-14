# Copyright (c) 2026, TEST and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BookIssueItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		article: DF.Link
		days_late: DF.Int
		due_date: DF.Data
		fine_amount: DF.Currency
		issue_date: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		return_date: DF.Data | None
		status: DF.Literal["Issued", "Returned", "Overdue"]
	# end: auto-generated types

	_DOCTYPE_NAME = "Book Issue Item"
