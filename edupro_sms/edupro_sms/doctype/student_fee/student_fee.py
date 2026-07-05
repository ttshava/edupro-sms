# Copyright (c) 2026, Edupro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class StudentFee(Document):
	def validate(self):
		self.balance = flt(self.amount) - flt(self.amount_paid)
		if self.balance <= 0:
			self.status = "Paid"
		elif flt(self.amount_paid) > 0:
			self.status = "Partially Paid"
		else:
			self.status = "Billed"
