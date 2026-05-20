from __future__ import annotations

from pathlib import Path

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def build_receipt_pdf(donations, output_path: str | Path, donor_name: str = '', base_url: str = 'http://127.0.0.1:5000') -> Path:
    output_path = Path(output_path)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    y = height - 20 * mm
    pdf.setTitle('Sadaqah Receipt')
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(20 * mm, y, 'Sadaqah & Zakat Receipt Summary')
    y -= 10 * mm
    pdf.setFont('Helvetica', 11)
    if donor_name:
        pdf.drawString(20 * mm, y, f'Donor: {donor_name}')
        y -= 8 * mm
    total = 0.0
    by_type = {}
    for donation in donations:
        total += donation.amount
        by_type[donation.donation_type] = by_type.get(donation.donation_type, 0.0) + donation.amount
        pdf.drawString(20 * mm, y, f'{donation.date} | {donation.charity_name} | {donation.donation_type} | {donation.amount:.2f} {donation.currency}')
        y -= 7 * mm
        if y < 40 * mm:
            pdf.showPage()
            y = height - 20 * mm
    y -= 4 * mm
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(20 * mm, y, f'Total: {total:.2f}')
    y -= 8 * mm
    pdf.setFont('Helvetica', 11)
    for donation_type, amount in by_type.items():
        pdf.drawString(20 * mm, y, f'{donation_type}: {amount:.2f}')
        y -= 6 * mm
    if donations:
        charity_id = donations[0].charity_id or ''
        qr_payload = f'{base_url}/charities/{charity_id}' if charity_id else base_url
        image = qrcode.make(qr_payload)
        pdf.drawImage(ImageReader(image), width - 55 * mm, 20 * mm, 35 * mm, 35 * mm)
        pdf.drawString(width - 60 * mm, 18 * mm, 'QR: charity profile')
    pdf.save()
    return output_path
