import os
import glob
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pandas as pd

# Directory containing CSV files
data_dir = "data"
csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
# Output PDF file
# Output PDF in the 'data' directory
output_pdf = os.path.join(data_dir, "Plans.pdf")



# Create a canvas for the PDF
c = canvas.Canvas(output_pdf, pagesize=A4)
page_width_pts, page_height_pts = A4
cm_to_points = 72 / 2.54

# Loop over each CSV file
for csv_file in csv_files:
    # Read CSV
    df = pd.read_csv(csv_file)
    df = df.dropna(subset=['org x', 'org y', 'x', 'y'])

    # Check first rectangle's center
    first_x = df.iloc[0]['org x']
    first_y = df.iloc[0]['org y']
    first_x_size = df.iloc[0]['x']
    first_y_size = df.iloc[0]['y']

    first_rect_center_x = first_x + first_x_size / 2
    first_rect_center_y = first_y + first_y_size / 2

    # Calculate shift to center first rect
    page_width_cm = page_width_pts / cm_to_points
    page_height_cm = page_height_pts / cm_to_points

    shift_x_cm = (page_width_cm / 2) - first_rect_center_x
    shift_y_cm = (page_height_cm / 2) - first_rect_center_y

    # add title
    # Draw title for each page (filename)
    filename_full = os.path.basename(csv_file)
    filename_without_ext = os.path.splitext(filename_full)[0]

    # Then use filename_without_ext for the title:
    title_line1 = "Les Crêts Corniers"
    title_line2 = f"{filename_without_ext}"

    # Calculate the y position for the title
    title_y = page_height_pts - 60  # starting y position

    # Draw the first line centered
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_width_pts / 2, title_y, title_line1)

    # Draw the second line a few points below
    line_spacing = 18  # space between lines
    c.drawCentredString(page_width_pts / 2, title_y - line_spacing, title_line2)

    # add description
    # calculate y position of description from top of biggest rectangle
    y0_cm = first_y + shift_y_cm + first_y_size
    # Convert to points
    y0_pt = y0_cm * cm_to_points
    # add two lines
    description_y = y0_pt + 2 * line_spacing
    description = ["Disposition des pièces", "échelle - 1 : 100"]

    c.setFont("Helvetica", 12)
    for i, line in enumerate(description):
        y_position = description_y - i * line_spacing
        c.drawCentredString(page_width_pts / 2, y_position, line)



    # Draw rectangles
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

        # Calculate center
        center_x_pt = x0_pt + width_pt / 2
        center_y_pt = y0_pt + height_pt / 2

        # Add utilization (if exists)
        utilization_value = row.get('utilisation')
        if pd.isnull(utilization_value):
            utilization_text = ''
        else:
            utilization_text = str(utilization_value).strip()

        # Add area
        area_value = row.get('area')
        if pd.notnull(area_value):
            area_text = f"{area_value:.1f}"
        else:
            area_text = ''

        # Draw text inside rectangle
        if utilization_text:
            c.setFont("Helvetica", 8)
            c.drawCentredString(center_x_pt, center_y_pt + 4, utilization_text)
        if pd.notnull(area_value):
            c.setFont("Helvetica", 8)
            c.drawCentredString(center_x_pt, center_y_pt - 8, area_text)

    # Add some space before next page
    c.showPage()

# Save the PDF
c.save()

print(f"Multi-page PDF created: {output_pdf}")
