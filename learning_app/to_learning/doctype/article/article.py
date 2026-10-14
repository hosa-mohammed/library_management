# Copyright (c) 2026, TEST and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Article(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		article_name: DF.Data
		author: DF.Data | None
		description: DF.TextEditor | None
		image: DF.AttachImage | None
		isbn: DF.Data | None
		issued_date: DF.Data | None
		issued_to: DF.Link | None
		status: DF.Literal["Available", "Issued"]
	# end: auto-generated types

	_DOCTYPE_NAME = "Article"
