from ..shared import write_pdf_report


def export_pdf(path, summary_lines, title='Database Accelerator - Quality Report'):
    write_pdf_report(path, summary_lines, title=title)
    return path
