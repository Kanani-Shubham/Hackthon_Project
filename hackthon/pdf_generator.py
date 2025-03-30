from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class TenderPDFGenerator:
    def __init__(self, output_path):
        # Use standard Windows fonts
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        # Use standard Windows fonts for styles
        self.styles.add(ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName='Times-Roman',
            fontSize=24,
            spaceAfter=30,
            alignment=1
        ))
        
        self.styles.add(ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontName='Times-Bold',
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#333333')
        ))
        
        self.styles.add(ParagraphStyle(
            'CustomBodyText',
            parent=self.styles['Normal'],
            fontName='Times-Roman',
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            leading=16
        ))

    def _format_currency(self, amount):
        """Format amount with Rs. instead of Rupee symbol"""
        return 'Rs. {:,.2f}'.format(float(amount))

    def generate_pdf(self, tender_data, generated_content):
        story = []
        
        # Title Page
        story.append(Paragraph(f"TENDER DOCUMENT", self.styles['CustomTitle']))
        story.append(Paragraph(f"{tender_data['tender_title']}", self.styles['CustomTitle']))
        story.append(Spacer(1, 30))
        
        # Format tender information with Rs.
        tender_info = [
            ['Tender ID:', tender_data['tender_id']],
            ['Issuing Authority:', tender_data['issuing_authority']],
            ['Tender Amount:', self._format_currency(tender_data['tender_amount'])],
            ['Bid Start Date:', tender_data['bid_start_date'].strftime('%d-%m-%Y')],
            ['Bid End Date:', tender_data['bid_end_date'].strftime('%d-%m-%Y')]
        ]
        
        table = Table(tender_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(table)
        story.append(PageBreak())

        # Generated Content Sections
        for section in generated_content['generated_content']['sections']:
            story.append(Paragraph(section['title'], self.styles['SectionHeader']))
            story.append(Spacer(1, 12))
            
            content_lines = section['content'].split('\n')
            for line in content_lines:
                line = line.strip()
                if line:
                    story.append(Paragraph(line, self.styles['CustomBodyText']))
                    
            story.append(Spacer(1, 12))

        try:
            self.doc.build(story)
        except Exception as e:
            print(f"Error building PDF: {str(e)}")
            raise