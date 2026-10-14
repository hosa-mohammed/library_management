# Copyright (c) 2026, TEST and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, add_days


class BookIssue(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from learning_app.to_learning.doctype.book_issue_item.book_issue_item import BookIssueItem

		amended_from: DF.Link | None
		books: DF.Table[BookIssueItem]
		expected_return_date: DF.Date | None
		issue_date: DF.Date
		member: DF.Link
		status: DF.Literal["Draft", "Active", "Completed", "Overdue"]
		total_books: DF.Int
		total_fine: DF.Currency
	# end: auto-generated types

	_DOCTYPE_NAME = "Book Issue"

	# ==================== Controller Methods ====================

	def validate(self):
		"""يُنفّذ قبل الحفظ — للتحقق من البيانات وحساب الإجماليات"""
		self.validate_member()
		self.validate_books()
		self.calculate_totals()

	def before_submit(self):
		"""يُنفّذ قبل Submit — التحقق الصارم من توفر الكتب"""
		for row in self.books:
			article_status = frappe.db.get_value(
				"Article", row.article, "status"
			)
			if article_status != "Available":
				article_name = frappe.db.get_value(
					"Article", row.article, "article_name"
				)
				frappe.throw(
					f"لا يمكن إصدار الاستعارة: الكتاب "
					f"{article_name} غير متاح "
					f"(الحالة الحالية: {article_status})."
				)
	def on_submit(self):
		"""يُنفّذ عند Submit — لتطبيق منطق العمل"""
		self.update_articles_status("Issued")
		self.db_set("status", "Active")

	def on_cancel(self):
		"""يُنفّذ عند Cancel — لإلغاء التأثيرات"""
		self.update_articles_status("Available")
		self.db_set("status", "Draft")

	# ==================== Helper Methods ====================

	def validate_member(self):
		"""التحقق من أن العضو نشط ولم يتجاوز الحد"""
		member = frappe.get_doc("Library Member", self.member)

		if not member.is_active:
			frappe.throw(
				f"العضو {member.member_name} غير نشط. لا يمكن استعارة الكتب."
			)

		# حساب عدد الاستعارات النشطة لهذا العضو
		active_count = frappe.db.count(
			"Book Issue",
			filters={
				"member": self.member,
				"docstatus": 1,
				"status": "Active",
				"name": ["!=", self.name or ""],
			},
		)

		if active_count >= 3:
			frappe.throw(
				f"العضو {member.member_name} وصل للحد الأقصى "
				f"({active_count} استعارات نشطة)."
			)

	def validate_books(self):
		"""التحقق من كل كتاب في الجدول (فحص أساسي فقط)"""
		if not self.books:
			frappe.throw("يجب إضافة كتاب واحد على الأقل.")

		seen_articles = set()

		for row in self.books:
			# التحقق من عدم التكرار
			if row.article in seen_articles:
				frappe.throw(f"الكتاب {row.article} مكرر في القائمة.")
			seen_articles.add(row.article)

			# ضبط Issue Date تلقائياً إذا كان فارغاً
			if not row.issue_date:
				row.issue_date = self.issue_date

			# ضبط Due Date تلقائياً (+14 يوم)
			if not row.due_date and row.issue_date:
				row.due_date = add_days(row.issue_date, 14)

			# ضبط Status تلقائياً
			if not row.status:
				row.status = "Issued"
				
	def calculate_totals(self):
		"""حساب الإجماليات"""
		self.total_books = len(self.books)
		self.total_fine = sum(
			flt(row.fine_amount) for row in self.books
		)

	def update_articles_status(self, status):
		"""تحديث حالة كل كتاب في Article"""
		for row in self.books:
			frappe.db.set_value(
				"Article", row.article, "status", status
			)
		frappe.db.commit()