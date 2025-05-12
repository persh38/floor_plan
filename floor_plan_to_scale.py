import os
import glob
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pandas as pd

# Constants
DATA_DIR = "data"
OUTPUT_PDF = os.path.join(DATA_DIR, "Plans.pdf")
CM_TO_POINTS = 72 / 2.54  # Conversion factor from centimeters to points (1 inch = 72 points, 1 inch = 2.54 cm)


def get_csv_files(directory):
    """
    Retrieve all CSV files in the given directory.
    """
    return glob.glob(os.path.join(directory, "*.csv"))


def draw_title_and_description(c, filename_without_ext, first_rect_y_pt, page_width_pts, page_height_pts):
    """
    Draws the title and description on the PDF page.
    """
    # Title block
    title_line1 = "Les Crêts Corniers"
    title_line2 = f"{filename_without_ext}"
    title_y = page_height_pts - 60

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_width_pts / 2, title_y, title_line1)
    c.drawCentredString(page_width_pts / 2, title_y - 18, title_line2)

    # Description block
    description_lines = ["Disposition des pièces", "échelle - 1 : 100"]
    description_y = first_rect_y_pt + 36  # Leave some space above the first rectangle

    c.setFont("Helvetica", 12)
    for i, line in enumerate(description_lines):
        c.drawCentredString(page_width_pts / 2, description_y - i * 18, line)


def draw_rectangles(c, df, shift_x_cm, shift_y_cm):
    """
    Draws rectangles and their annotations on the canvas.
    """
    for _, row in df.iterrows():
        # Calculate positions and sizes in points
        x0_pt = (row['org x'] + shift_x_cm) * CM_TO_POINTS
        y0_pt = (row['org y'] + shift_y_cm) * CM_TO_POINTS
        width_pt = row['x'] * CM_TO_POINTS
        height_pt = row['y'] * CM_TO_POINTS

        # Draw the rectangle
        c.rect(x0_pt, y0_pt, width_pt, height_pt, stroke=1, fill=0)

        # Calculate center position for text
        center_x_pt = x0_pt + width_pt / 2
        center_y_pt = y0_pt + height_pt / 2

        # Optional: Utilization and area labels
        utilization_text = str(row['utilisation']).strip() if pd.notnull(row.get('utilisation')) else ''
        area_text = f"{row['area']:.1f}" if pd.notnull(row.get('area')) else ''

        c.setFont("Helvetica", 8)
        if utilization_text:
            c.drawCentredString(center_x_pt, center_y_pt + 4, utilization_text)
        if area_text:
            c.drawCentredString(center_x_pt, center_y_pt - 8, area_text)


def process_csv_to_pdf(c, csv_file, page_width_pts, page_height_pts):
    """
    Processes a single CSV file and draws its content on a PDF page.
    """
    df = pd.read_csv(csv_file).dropna(subset=['org x', 'org y', 'x', 'y'])

    # Calculate the center shift for the first rectangle
    first_row = df.iloc[0]
    first_rect_center_x = first_row['org x'] + first_row['x'] / 2
    first_rect_center_y = first_row['org y'] + first_row['y'] / 2

    page_width_cm = page_width_pts / CM_TO_POINTS
    page_height_cm = page_height_pts / CM_TO_POINTS

    shift_x_cm = (page_width_cm / 2) - first_rect_center_x
    shift_y_cm = (page_height_cm / 2) - first_rect_center_y

    # Draw title and description
    filename_without_ext = os.path.splitext(os.path.basename(csv_file))[0]
    first_rect_y_pt = (first_row['org y'] + shift_y_cm + first_row['y']) * CM_TO_POINTS
    draw_title_and_description(c, filename_without_ext, first_rect_y_pt, page_width_pts, page_height_pts)

    # Draw all rectangles from the DataFrame
    draw_rectangles(c, df, shift_x_cm, shift_y_cm)

    c.showPage()


def main():
    """
    Main execution function.
    Generates a multi-page PDF from all CSV files in the specified data directory.
    Expects all lengths in the csv files to be in meters and draws all rectangles
    in exactly scale 1 : 100
    """
    csv_files = get_csv_files(DATA_DIR)
    if not csv_files:
        print("No CSV files found.")
        return

    c = canvas.Canvas(OUTPUT_PDF, pagesize=A4)
    page_width_pts, page_height_pts = A4

    for csv_file in csv_files:
        process_csv_to_pdf(c, csv_file, page_width_pts, page_height_pts)

    c.save()
    print(f"Multi-page PDF created: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
