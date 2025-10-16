import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
from apps.contracts.services.upload_service import UploadService


class ExportService:
    """
    Service for exporting contract analysis reports
    """

    def __init__(self):
        self.upload_service = UploadService()

    def generate_docx_report(self, contract):
        """
        Generate DOCX report (placeholder - would use python-docx)
        """
        # Placeholder implementation
        # In production, this would generate a proper DOCX report
        report_filename = f"contract_report_{contract.id}.docx"
        s3_key = f"reports/{contract.tenant.id}/{report_filename}"

        # Generate presigned URL
        return self.upload_service.get_presigned_url(s3_key)

    def generate_pdf_report(self, contract):
        """
        Generate PDF report using ReportLab
        """
        try:
            # Create PDF filename
            pdf_filename = f"contract_report_{contract.id}.pdf"
            local_path = os.path.join(settings.MEDIA_ROOT, 'reports', pdf_filename)

            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Create PDF document
            doc = SimpleDocTemplate(local_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
            )
            story.append(Paragraph(f"Contract Analysis Report: {contract.original_filename}", title_style))
            story.append(Spacer(1, 12))

            # Contract Information
            story.append(Paragraph("Contract Information", styles['Heading2']))
            contract_info = [
                ["Contract Type:", contract.contract_type or "N/A"],
                ["Industry:", contract.industry],
                ["Language:", contract.language],
                ["Contract Date:", str(contract.contract_date) if contract.contract_date else "N/A"],
                ["Expiry Date:", str(contract.expiry_date) if contract.expiry_date else "N/A"],
                ["Value:", f"{contract.contract_value or 0} {contract.currency or 'USD'}"],
            ]

            table = Table(contract_info, colWidths=[100, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))

            # Risk Assessment
            if hasattr(contract, 'analysis'):
                story.append(Paragraph("Risk Assessment", styles['Heading2']))

                risk_info = [
                    ["Overall Risk Score:", f"{contract.analysis.overall_risk_score}/100"],
                    ["Priority Level:", contract.analysis.priority_level.title()],
                    ["Critical Issues:", str(contract.analysis.critical_issues_count)],
                    ["Missing Clauses:", str(contract.analysis.missing_clauses_count)],
                ]

                risk_table = Table(risk_info, colWidths=[120, 200])
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(risk_table)
                story.append(Spacer(1, 20))

            # Build PDF
            doc.build(story)

            # Upload to S3
            s3_key = f"reports/{contract.tenant.id}/{pdf_filename}"
            with open(local_path, 'rb') as f:
                self.upload_service.s3_client.upload_fileobj(
                    f,
                    self.upload_service.bucket_name,
                    s3_key,
                    ExtraArgs={'ContentType': 'application/pdf'}
                )

            # Generate presigned URL
            return self.upload_service.get_presigned_url(s3_key)

        except Exception as e:
            raise Exception(f"Failed to generate PDF report: {str(e)}")