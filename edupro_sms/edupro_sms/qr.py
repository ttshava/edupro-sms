"""QR code generation for the Report Card print format's authenticity
check -- registered as a Jinja method (hooks.py) so the print format can
call it directly without any server-side view."""

import base64
from io import BytesIO

import frappe
import qrcode


def report_card_verification_qr_data_uri(verification_code: str | None) -> str | None:
	if not verification_code:
		return None

	url = frappe.utils.get_url(f"/verify-report-card?code={verification_code}")
	img = qrcode.make(url, box_size=6, border=2)
	buf = BytesIO()
	img.save(buf, format="PNG")
	encoded = base64.b64encode(buf.getvalue()).decode()
	return f"data:image/png;base64,{encoded}"
