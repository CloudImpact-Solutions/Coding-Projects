from fpdf import FPDF

# Function to create a sample PDF with text content
def create_text_pdf(filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "This is a sample PDF document with text content.")
    pdf.multi_cell(0, 10, "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
    pdf.output(filename)

# Function to create a sample PDF with invoice content
def create_invoice_pdf(filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Invoice")
    pdf.multi_cell(0, 10, "Part No: P1234")
    pdf.multi_cell(0, 10, "Fulfillment Plant: PLANT1")
    pdf.multi_cell(0, 10, "Shipping Method: FedEx")
    pdf.multi_cell(0, 10, "Vendor No: V9876")
    pdf.multi_cell(0, 10, "Customer No: C5432")
    pdf.multi_cell(0, 10, "PO No: PO7890")
    pdf.output(filename)

# Create PDFs
create_text_pdf("sample_text.pdf")
create_invoice_pdf("sample_invoice.pdf")
