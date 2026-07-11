"""Faded school-logo watermark for the Report Card print format --
registered as a Jinja method (hooks.py), same pattern as qr.py's
verification QR code.

The low opacity is baked into the PNG's own alpha channel rather than
left to CSS `opacity` on the <img> tag: wkhtmltopdf's older WebKit
engine renders CSS opacity on position:absolute images unreliably (it
showed up full-strength in testing), so this bypasses that entirely.
"""

import base64
from io import BytesIO

import frappe
from PIL import Image

# Cap on the darkest/most saturated logo pixels' final alpha (0-255) --
# not a flat multiplier. Most school logo files are flattened PNGs/JPEGs
# with an opaque white background rather than real transparency, so
# scaling the existing alpha channel uniformly just fades the whole
# rectangle to a grey blob instead of leaving a recognisable logo
# silhouette. Deriving alpha from luminance instead means white/near-
# white background pixels become fully transparent (0) while only the
# actual ink/colour of the emblem fades in, capped well short of solid.
WATERMARK_MAX_ALPHA = 70


def report_card_watermark_data_uri() -> str | None:
	logo_url = frappe.db.get_single_value("School Settings", "logo")
	if not logo_url:
		return None

	file_name = frappe.db.get_value("File", {"file_url": logo_url}, "name")
	if not file_name:
		return None

	file_path = frappe.get_doc("File", file_name).get_full_path()

	try:
		img = Image.open(file_path).convert("RGBA")
	except Exception:
		frappe.log_error(title="Report card watermark generation failed")
		return None

	img.thumbnail((500, 500))
	luminance = img.convert("L")
	alpha = luminance.point(lambda p: min(255 - p, WATERMARK_MAX_ALPHA))
	img.putalpha(alpha)

	buf = BytesIO()
	img.save(buf, format="PNG")
	encoded = base64.b64encode(buf.getvalue()).decode()
	return f"data:image/png;base64,{encoded}"
