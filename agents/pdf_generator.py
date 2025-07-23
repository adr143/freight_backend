from fpdf import FPDF
import uuid
import os
from datetime import datetime

class StyledPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "AMZ PREP PHILIPPINES", ln=True, align="L")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, "Freight Quote & Logistics Services", ln=True, align="L")
        self.ln(5)

    def add_quote_metadata(self, quote_id):
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, f"Quote ID: {quote_id}", ln=False, align="L")
        self.cell(0, 8, f"Date: {datetime.now().strftime('%m/%d/%Y')}", ln=True, align="R")
        self.ln(4)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 30, 30)
        self.cell(0, 8, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def shipment_details(self, data):
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, f"Origin: {data['origin']}", ln=True)
        self.cell(0, 6, f"Destination: {data['destination']}", ln=True)
        self.cell(0, 6, f"Weight: {data['weight']} kg", ln=True)
        self.cell(0, 6, f"Freight Class: {data.get('freight_class', 'N/A')}", ln=True)
        self.cell(0, 6, f"Mode: {data.get('mode', 'N/A')}", ln=True)
        self.ln(2)

        # Add cargo description from the form
        description = data.get("description", "").strip()
        if description:
            self.set_font("Helvetica", "B", 10)
            self.cell(0, 6, "Cargo Description:", ln=True)
            self.set_font("Helvetica", "", 10)
            self.multi_cell(0, 6, description)
            self.ln(4)


    def vendor_table(self, quotes):
        self.set_font("Helvetica", "B", 10)
        self.cell(60, 8, "Vendor", border=1)
        self.cell(40, 8, "Service", border=1)
        self.cell(25, 8, "Days", border=1, align="C")
        self.cell(40, 8, "Rate (PHP)", border=1, align="R")
        self.ln()

        self.set_font("Helvetica", "", 10)
        for q in quotes:
            self.cell(60, 8, q["vendor"], border=1)
            self.cell(40, 8, q.get("service", "Economy"), border=1)
            self.cell(25, 8, str(q.get("days", 3)), border=1, align="C")
            self.cell(40, 8, f"{q['final_rate']:,}", border=1, align="R")
            self.ln()
        self.ln(5)

    def pricing_summary(self, quotes):
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, "Pricing Summary", ln=True)
        avg = sum(q["final_rate"] for q in quotes) / len(quotes)
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, f"Average Quoted Rate: PHP {avg:,.2f}", ln=True)

def generate_pdf(data, quotes, summary):
    pdf = StyledPDF()
    pdf.add_page()

    # Header content
    quote_id = f"AMZ-{uuid.uuid4().hex[:12].upper()}"
    pdf.add_quote_metadata(quote_id)

    # Shipment Info
    pdf.section_title("Shipment Details")
    pdf.shipment_details(data)

    # Vendor Quotes
    pdf.section_title("Vendor Quotes (PHP)")
    pdf.vendor_table(quotes)

    # Summary
    pdf.pricing_summary(quotes)

    # Save
    os.makedirs("quotes", exist_ok=True)
    file_path = f"quotes/{quote_id}.pdf"
    pdf.output(file_path)
    return file_path
