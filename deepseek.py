from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pandas as pd

# Read CSV
csv_path = "data/rez.csv"
df = pd.read_csv(csv_path)

# Drop rows with missing data
df = df.dropna(subset=['org x', 'org y', 'x', 'y'])

# Check first rectangle's center
first_x = df.iloc[0]['org x']
first_y = df.iloc[0]['org y']
first_x_size = df.iloc[0]['x']
first_y_size = df.iloc[0]['y']

first_rect_center_x = first_x + first_x_size / 2
first_rect_center_y = first_y + first_y_size / 2

# Page size in points
page_width_pts, page_height_pts = A4

# Convert page size to cm
cm_to_points = 72 / 2.54
page_width_cm = page_width_pts / cm_to_points
page_height_cm = page_height_pts / cm_to_points

# Calculate shift in cm so that first rect center aligns with page center
shift_x_cm = (page_width_cm / 2) - first_rect_center_x
shift_y_cm = (page_height_cm / 2) - first_rect_center_y

print("Shift in cm:", shift_x_cm, shift_y_cm)

# Create PDF
pdf_path = "rectangles_centered_with_text.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)

# Loop through rectangles
for _, row in df.iterrows():
    if pd.isnull(row['org x']) or pd.isnull(row['org y']) or pd.isnull(row['x']) or pd.isnull(row['y']):
        continue

    # Shift origins
    x0_cm = row['org x'] + shift_x_cm
    y0_cm = row['org y'] + shift_y_cm

    # Convert to points
    x0_pt = x0_cm * cm_to_points
    y0_pt = y0_cm * cm_to_points
    width_pt = row['x'] * cm_to_points
    height_pt = row['y'] * cm_to_points

    # Draw rectangle
    c.rect(x0_pt, y0_pt, width_pt, height_pt, stroke=1, fill=0)

    # Calculate the center of the rectangle
    center_x_pt = x0_pt + width_pt / 2
    center_y_pt = y0_pt + height_pt / 2

    # Text lines
    #utilization_text = row.get('utilisation', '').strip()
    utilisation_value = row.get('utilisation')
    if pd.isnull(utilisation_value):
        utilization_text = ''
    else:
        utilization_text = str(utilisation_value).strip()

    area_value = row.get('area', None)
    if pd.notnull(area_value):
        area_text = f"{area_value:.1f} m2"

    # Add utilization if available
    if utilization_text:
        c.setFont("Helvetica", 8)
        c.drawCentredString(center_x_pt, center_y_pt + 4, utilization_text)

    # Add area
    if pd.notnull(area_value):
        c.setFont("Helvetica", 8)
        c.drawCentredString(center_x_pt, center_y_pt - 8, area_text)

# Add a title
# Example: multiple lines of title
title_lines = ["Les Crêts Corniers", "Disposition des pieces", "échelle 1 : 100]"]
title_y = page_height_pts - 100  # start y position
line_spacing = 14  # space between lines in points

c.setFont("Helvetica", 12)
for i, line in enumerate(title_lines):
    y_position = title_y - i * line_spacing
    c.drawCentredString(page_width_pts / 2, y_position, line)

# c.setFont("Helvetica", 12)
# c.drawCentredString(page_width_pts / 2, page_height_pts - 100, "Les Crêts Corniers Distribution des pièces – échelle 1 : 100")
c.save()

print(f"PDF with text annotations saved: {pdf_path}")
