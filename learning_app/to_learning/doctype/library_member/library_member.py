# Copyright (c) 2026, TEST and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LibraryMember(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		email: DF.Data | None
		is_active: DF.Check
		member_name: DF.Data
		membership_date: DF.Data | None
		phone: DF.Data | None
	# end: auto-generated types

	_DOCTYPE_NAME = "Library Member"
