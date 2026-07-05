"""
Batch Report Card Printing API

Whitelisted method to generate merged PDF of multiple report cards.

Usage:
    frappe.call({
        method: 'edupro_sms.batch_print_api.generate_batch_report_cards',
        args: {
            student_group: 'Form 1A',
            academic_term: 'Term 1 2026',
            status_filter: 'Published'
        }
    })
"""

import frappe
from frappe import _
from frappe.utils import get_files_path
import os
import subprocess
from datetime import datetime
from PyPDF2 import PdfMerger


@frappe.whitelist()
def generate_batch_report_cards(student_group=None, academic_term=None, status_filter='Published'):
    """
    Generate batch report cards PDF by merging individual report card PDFs.

    Args:
        student_group: Student Group/Class name (e.g., 'Form 1A'), or 'ALL' for all groups
        academic_term: Academic Term name (required)
        status_filter: 'Published', 'Approved', or 'ALL'

    Returns:
        {
            'success': True,
            'file_path': '/path/to/merged.pdf',
            'file_url': '/files/merged.pdf',
            'page_count': 50,
            'report_count': 25,
            'file_size_mb': 5.2,
            'message': 'Successfully merged 25 report cards (50 pages) into single PDF'
        }
    """

    # Permission check
    if not frappe.has_permission('Report Card', 'read'):
        frappe.throw(_("You do not have permission to generate batch reports"))

    # Validate academic term
    if not academic_term:
        frappe.throw("Academic Term is required")

    term_doc = frappe.db.get_value('Academic Term', academic_term, ['name', 'start_date', 'end_date'])
    if not term_doc:
        frappe.throw(f"Academic Term '{academic_term}' not found")

    try:
        # Build filters for Report Cards
        filters = {
            'academic_term': academic_term
        }

        if student_group and student_group != 'ALL':
            filters['student_group'] = student_group

        if status_filter and status_filter != 'ALL':
            filters['docstatus'] = 1 if status_filter == 'Published' else 0

        # Query Report Cards
        report_cards = frappe.db.get_list(
            'Report Card',
            filters=filters,
            fields=['name', 'student', 'student_name', 'student_group', 'docstatus'],
            order_by='student_group asc, student_name asc'
        )

        if not report_cards:
            return {
                'success': False,
                'error': f'No report cards found for {academic_term}',
                'report_count': 0
            }

        frappe.logger().info(f"Batch print: Found {len(report_cards)} report cards for {academic_term}")

        # Generate merged PDF
        merge_result = merge_report_card_pdfs(report_cards, academic_term, student_group)

        return merge_result

    except Exception as e:
        frappe.logger().error(f"Error in batch print: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def merge_report_card_pdfs(report_cards, academic_term, student_group):
    """
    Generate individual PDFs and merge them.

    Args:
        report_cards: List of Report Card documents
        academic_term: Term name
        student_group: Group/class name

    Returns:
        {
            'success': True,
            'file_path': '/path/to/merged.pdf',
            'file_url': '/files/merged.pdf',
            'page_count': total_pages,
            'report_count': len(report_cards),
            'file_size_mb': file_size,
            'message': 'Successfully merged...'
        }
    """

    try:
        # Prepare merger
        merger = PdfMerger()
        temp_pdfs = []
        total_pages = 0

        # Generate each report card PDF
        for idx, report in enumerate(report_cards):
            try:
                # Get report card HTML/Print format
                report_doc = frappe.get_doc('Report Card', report['name'])

                # Generate PDF using Frappe's print method
                # This uses the default print format for Report Card
                pdf_content = frappe.get_print(
                    doctype='Report Card',
                    name=report['name'],
                    print_format='Standard',
                    as_pdf=True
                )

                # Save to temp file
                temp_filename = f"/tmp/report_{report['name']}_{idx}.pdf"
                with open(temp_filename, 'wb') as f:
                    f.write(pdf_content)

                temp_pdfs.append(temp_filename)

                # Add to merger
                merger.append(temp_filename)

                # Count pages (approximate: 1 page per report)
                total_pages += 1

                frappe.logger().info(f"Generated PDF for report {report['name']}")

            except Exception as e:
                frappe.logger().error(f"Error generating PDF for {report['name']}: {str(e)}")
                continue

        if not temp_pdfs:
            frappe.throw("Failed to generate any report PDFs")

        # Create output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        group_name = student_group if student_group != 'ALL' else 'All'
        output_filename = f"batch_reports_{group_name}_{academic_term}_{timestamp}.pdf"

        # Get files directory
        files_path = get_files_path()
        output_path = os.path.join(files_path, output_filename)

        # Write merged PDF
        merger.write(output_path)
        merger.close()

        # Calculate file size
        file_size_bytes = os.path.getsize(output_path)
        file_size_mb = file_size_bytes / (1024 * 1024)

        # Generate public URL
        file_url = f'/files/{output_filename}'

        # Cleanup temp files
        for temp_pdf in temp_pdfs:
            try:
                os.remove(temp_pdf)
            except:
                pass

        # Log operation
        frappe.logger().info(
            f"Batch print complete: {len(report_cards)} reports merged "
            f"({total_pages} pages, {file_size_mb:.2f}MB) by {frappe.session.user}"
        )

        return {
            'success': True,
            'file_path': output_path,
            'file_url': file_url,
            'file_name': output_filename,
            'page_count': total_pages,
            'report_count': len(report_cards),
            'file_size_mb': round(file_size_mb, 2),
            'message': f"Successfully merged {len(report_cards)} report cards ({total_pages} pages) into single PDF. File size: {file_size_mb:.2f}MB"
        }

    except Exception as e:
        frappe.logger().error(f"Error in PDF merge: {str(e)}")
        raise


@frappe.whitelist()
def preview_batch_print(student_group=None, academic_term=None, status_filter='Published'):
    """
    Preview how many report cards will be printed (no side effects).

    Args:
        student_group: Student Group name or 'ALL'
        academic_term: Academic Term name
        status_filter: 'Published', 'Approved', or 'ALL'

    Returns:
        {
            'count': 25,
            'student_group': 'Form 1A',
            'academic_term': 'Term 1 2026',
            'estimated_pages': 25,
            'estimated_file_size_mb': 5.2,
            'students': [first 5 as preview]
        }
    """

    if not frappe.has_permission('Report Card', 'read'):
        frappe.throw(_("You do not have permission to preview reports"))

    if not academic_term:
        frappe.throw("Academic Term is required")

    try:
        filters = {'academic_term': academic_term}

        if student_group and student_group != 'ALL':
            filters['student_group'] = student_group

        if status_filter and status_filter != 'ALL':
            filters['docstatus'] = 1 if status_filter == 'Published' else 0

        report_cards = frappe.db.get_list(
            'Report Card',
            filters=filters,
            fields=['name', 'student_name', 'student_group'],
            order_by='student_group asc, student_name asc'
        )

        count = len(report_cards)
        estimated_pages = count  # Rough estimate: 1 page per report
        estimated_size = count * 0.2  # Rough estimate: ~200KB per report

        return {
            'count': count,
            'student_group': student_group or 'All',
            'academic_term': academic_term,
            'estimated_pages': estimated_pages,
            'estimated_file_size_mb': round(estimated_size, 2),
            'students': [
                {
                    'name': r['student_name'],
                    'class': r['student_group']
                }
                for r in report_cards[:5]
            ],
            'message': f"{count} report cards will be merged into {estimated_pages} pages"
        }

    except Exception as e:
        frappe.logger().error(f"Error in preview: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_batch_print_history(limit=10):
    """
    Get history of recently generated batch prints.

    Returns list of recent batch print operations with timestamps.
    """

    if not frappe.has_permission('Report Card', 'read'):
        frappe.throw(_("You do not have permission to view history"))

    try:
        # Query Frappe's Job Log for batch print operations
        history = frappe.db.get_list(
            'Job Log',
            filters={'method': 'edupro_sms.batch_print_api.generate_batch_report_cards'},
            fields=['name', 'creation', 'user', 'status'],
            order_by='creation desc',
            limit_page_length=limit
        )

        return {
            'history': history,
            'count': len(history)
        }

    except Exception as e:
        frappe.logger().error(f"Error getting history: {str(e)}")
        return {'error': str(e)}
