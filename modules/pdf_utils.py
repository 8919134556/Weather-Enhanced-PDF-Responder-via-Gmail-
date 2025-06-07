import io
import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def append_weather_to_pdf(input_pdf_path, weather_info, output_pdf_path=None):
    """
    Reads the PDF at input_pdf_path, draws a simple one‐row table at the top of each page,
    appends a footer at the bottom, and writes out to output_pdf_path. If output_pdf_path
    is None, overwrite in place.

    weather_info: dict with keys:
        city, description, temperature_celsius, humidity_percent,
        wind_speed_m_s, timestamp
    """
    if output_pdf_path is None:
        base, ext = os.path.splitext(input_pdf_path)
        output_pdf_path = f"{base}_updated{ext}"

    # Constants for positioning
    PAGE_WIDTH, PAGE_HEIGHT = letter
    TOP_MARGIN   = PAGE_HEIGHT - inch * 1      # 1" down from top
    BOTTOM_MARGIN = 0.5 * inch                  # 0.5" up from bottom
    LEFT_MARGIN   = inch * 0.5                  # 0.5" from left edge
    RIGHT_MARGIN  = PAGE_WIDTH - inch * 0.5      # 0.5" from right edge

    # Column definitions for table: 6 columns, evenly split
    num_columns = 6
    table_total_width = RIGHT_MARGIN - LEFT_MARGIN
    col_width = table_total_width / num_columns
    row_height = 0.4 * inch   # height of header+value row

    # Prepare header titles and corresponding values
    headers = ["City", "Description", "Temp (°C)", "Humidity (%)", "Wind (m/s)", "Timestamp"]
    values  = [
        weather_info["city"],
        weather_info["description"],
        f"{weather_info['temperature_celsius']:.2f}",
        f"{weather_info['humidity_percent']}",
        f"{weather_info['wind_speed_m_s']:.1f}",
        weather_info["timestamp"]
    ]

    # Read the existing PDF
    with open(input_pdf_path, "rb") as in_f:
        reader = PdfReader(in_f)
        writer = PdfWriter()

        for page_idx, orig_page in enumerate(reader.pages):
            # 1) Create a PDF “overlay” with both table at top and footer at bottom
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)

            # ---- Draw the TOP table ----
            # Draw cell outlines and text for header row
            y_top = TOP_MARGIN
            # Draw header cells
            can.setFont("Helvetica-Bold", 8)
            for col_idx, heading in enumerate(headers):
                x = LEFT_MARGIN + col_idx * col_width
                # Draw rectangle border of cell
                can.rect(x, y_top - row_height, col_width, row_height, stroke=1, fill=0)
                # Draw heading text centered-ish in that cell
                text_x = x + 0.05 * inch
                text_y = y_top - 0.25 * inch
                can.drawString(text_x, text_y, heading)

            # Draw value row immediately below header
            can.setFont("Helvetica", 8)
            y_values = y_top - row_height
            for col_idx, val in enumerate(values):
                x = LEFT_MARGIN + col_idx * col_width
                # Outline for value cell
                can.rect(x, y_values - row_height, col_width, row_height, stroke=1, fill=0)
                # Draw value text left‐aligned in cell, wrap/clip if too long
                text_x = x + 0.05 * inch
                text_y = y_values - 0.25 * inch
                # If the string is too long to fit in one line, truncate
                max_chars = int(col_width / (6))  # very rough estimate: ~6 pts per char
                if len(val) > max_chars:
                    val = val[: max_chars - 3] + "..."
                can.drawString(text_x, text_y, val)

            # ---- Draw the FOOTER ----
            footer_text = (
                f"{weather_info['city']} | {weather_info['description']} | "
                f"{weather_info['temperature_celsius']:.2f}°C | Humidity: {weather_info['humidity_percent']}% | "
                f"Wind: {weather_info['wind_speed_m_s']:.1f} m/s | {weather_info['timestamp']}"
            )
            can.setFont("Helvetica", 8)
            can.drawString(LEFT_MARGIN, BOTTOM_MARGIN, footer_text)

            can.save()
            packet.seek(0)

            # 2) Merge the overlay onto the original page
            overlay_pdf = PdfReader(packet)
            overlay_page = overlay_pdf.pages[0]
            orig_page.merge_page(overlay_page)

            # 3) Add merged page to writer
            writer.add_page(orig_page)

        # 4) Write the updated PDF to disk
        with open(output_pdf_path, "wb") as out_f:
            writer.write(out_f)

    return output_pdf_path
