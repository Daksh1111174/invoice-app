import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from datetime import date

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Mahavir Cycles Invoice",
    page_icon="🚲",
    layout="centered"
)

# ---------------- Branding CSS ----------------
st.markdown("""
<style>
.stApp {
    background-color: #121212;
    color: #F5F5F5;
}
h1, h2, h3 {
    color: #C9A227;
}
label, span {
    color: #F5F5F5 !important;
}
.stButton>button {
    background-color: #0F3D2E;
    color: #F5F5F5;
    border-radius: 8px;
    border: none;
}
.stDownloadButton>button {
    background-color: #C9A227;
    color: black;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Logo & Title ----------------
st.image("logo.png", width=220)
st.markdown(
    "<h2>Mahavir Cycles – Invoice System</h2>"
    "<p>Eco-Friendly • Trusted • Jain Values</p>",
    unsafe_allow_html=True
)

# ---------------- Seller Details ----------------
st.header("🏪 Seller Details")
seller_name = st.text_input("Business Name", "Mahavir Cycles")
seller_address = st.text_area("Address", "Ahmedabad, Gujarat, India")
seller_gst = st.text_input("GST Number", "24MAHAVIR1234Z5")

# ---------------- Customer Details ----------------
st.header("👤 Customer Details")
cust_name = st.text_input("Customer Name")
cust_address = st.text_area("Customer Address")
invoice_no = st.text_input("Invoice Number", "INV-001")
invoice_date = st.date_input("Invoice Date", date.today())

# ---------------- Items Section ----------------
st.header("🧾 Invoice Items")

if "items" not in st.session_state:
    st.session_state.items = []

col1, col2, col3 = st.columns(3)
item_name = col1.text_input("Item Name")
qty = col2.number_input("Quantity", min_value=1, value=1)
price = col3.number_input("Price (₹)", min_value=0.0)

if st.button("➕ Add Item"):
    if item_name:
        st.session_state.items.append([item_name, qty, price])

df = pd.DataFrame(st.session_state.items, columns=["Item", "Qty", "Price"])

if not df.empty:
    df["Total"] = df["Qty"] * df["Price"]
    st.table(df)

subtotal = df["Total"].sum() if not df.empty else 0
gst = subtotal * 0.18
grand_total = subtotal + gst

st.subheader(f"Subtotal: ₹{subtotal:.2f}")
st.subheader(f"GST (18%): ₹{gst:.2f}")
st.subheader(f"Grand Total: ₹{grand_total:.2f}")

# ---------------- PDF Generator ----------------
def generate_pdf():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Logo
    logo = ImageReader("logo.png")
    pdf.drawImage(logo, 40, height - 110, width=120, height=60, mask="auto")

    # Header
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180, height - 70, "MAHAVIR CYCLES")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(180, height - 90, "Eco-Friendly • Trusted • Jain Values")

    # Seller Info
    pdf.setFont("Helvetica", 9)
    pdf.drawString(50, height - 150, f"Seller: {seller_name}")
    pdf.drawString(50, height - 165, f"Address: {seller_address}")
    pdf.drawString(50, height - 180, f"GST: {seller_gst}")

    # Invoice Info
    pdf.drawString(350, height - 150, f"Invoice No: {invoice_no}")
    pdf.drawString(350, height - 165, f"Date: {invoice_date}")

    # Customer Info
    pdf.drawString(50, height - 215, f"Bill To: {cust_name}")
    pdf.drawString(50, height - 230, cust_address)

    # Table Header
    y = height - 270
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Item")
    pdf.drawString(250, y, "Qty")
    pdf.drawString(300, y, "Price")
    pdf.drawString(380, y, "Total")

    # Table Rows
    pdf.setFont("Helvetica", 10)
    y -= 20
    for _, row in df.iterrows():
        pdf.drawString(50, y, row["Item"])
        pdf.drawString(250, y, str(row["Qty"]))
        pdf.drawString(300, y, f"₹{row['Price']:.2f}")
        pdf.drawString(380, y, f"₹{row['Total']:.2f}")
        y -= 18

    # Totals
    y -= 20
    pdf.drawString(300, y, f"Subtotal: ₹{subtotal:.2f}")
    y -= 15
    pdf.drawString(300, y, f"GST (18%): ₹{gst:.2f}")
    y -= 18
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(300, y, f"Grand Total: ₹{grand_total:.2f}")

    # Footer
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(
        50, 40,
        "🙏 Thank you for choosing Mahavir Cycles – supporting Ahimsa & sustainable living"
    )

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer

# ---------------- Download Button ----------------
if st.button("📄 Generate Invoice PDF"):
    pdf_file = generate_pdf()
    st.download_button(
        "⬇ Download Invoice",
        data=pdf_file,
        file_name=f"{invoice_no}.pdf",
        mime="application/pdf"
    )
