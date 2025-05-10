from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Path to your image
image_path = "a4_square.png"

# Output PDF filename
pdf_path = "output_with_text.pdf"

# Create a canvas with A4 size
c = canvas.Canvas(pdf_path, pagesize=A4)

# Get A4 dimensions in points (1 point = 1/72 inch)
# reportlab uses points, A4 is 595x842 points
page_width, page_height = A4

# Size of your image in points
# Since your image is 10cm x 10cm, convert to points:
# 1 inch = 2.54 cm, 1 inch = 72 points
cm_to_points = 72 / 2.54
image_width_points = 10 * cm_to_points
image_height_points = 10 * cm_to_points

# Position the image at the center of the page
x_center = page_width / 2
y_center = page_height / 2

x_image = x_center - (image_width_points / 2)
y_image = y_center - (image_height_points / 2)

# Draw the image
c.drawImage(image_path, x_image, y_image, width=image_width_points, height=image_height_points)

# Add some text above the image
text_x = x_center
text_y = y_image + image_height_points + 20  # 20 points above the image

c.setFont("Helvetica", 12)
c.drawCentredString(text_x, text_y, "This is a 10x10 cm square centered on the page.")

# Save the PDF
c.save()

print(f"PDF created: {pdf_path}")
