"""School-logo image helpers for print formats -- both registered as
Jinja methods (hooks.py), same pattern as qr.py's verification QR code.

Both variants embed the logo as a base64 data URI rather than pointing
<img src> at the raw file URL. wkhtmltopdf fetches src URLs over real
HTTP, and on this LAN setup that means looping back through the
machine's own external IP (hairpin NAT via host_name) -- unreliable
from inside the Docker container, and it intermittently fails PDF
generation outright ("broken image links"). Embedding the bytes
directly sidesteps any network fetch, for the plain logo just as much
as the faded watermark.
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


def _get_logo_image():
	logo_url = frappe.db.get_single_value("School Settings", "logo")
	if not logo_url:
		return None

	file_name = frappe.db.get_value("File", {"file_url": logo_url}, "name")
	if not file_name:
		return None

	file_path = frappe.get_doc("File", file_name).get_full_path()

	try:
		return Image.open(file_path).convert("RGBA")
	except Exception:
		frappe.log_error(title="School logo load failed")
		return None


def _to_data_uri(img) -> str:
	buf = BytesIO()
	img.save(buf, format="PNG")
	encoded = base64.b64encode(buf.getvalue()).decode()
	return f"data:image/png;base64,{encoded}"


def school_logo_data_uri() -> str | None:
	"""Full-opacity school logo, for the header of any print format --
	use this instead of School Settings.logo's raw file URL directly."""
	img = _get_logo_image()
	if img is None:
		return None
	img.thumbnail((400, 400))
	return _to_data_uri(img)


def report_card_watermark_data_uri() -> str | None:
	img = _get_logo_image()
	if img is None:
		return None
	img.thumbnail((500, 500))
	luminance = img.convert("L")
	alpha = luminance.point(lambda p: min(255 - p, WATERMARK_MAX_ALPHA))
	img.putalpha(alpha)
	return _to_data_uri(img)
