from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.cell.text import RichText

# Create a workbook and select the active worksheet
wb = Workbook()
ws = wb.active

# Create a RichText object
rich_text = RichText()

# Add "Good " with normal formatting
rich_text.append("Good ", font=Font(bold=False))  # Explicitly non-bold (optional)

# Add "morning" with bold formatting
rich_text.append("morning", font=Font(bold=True))

# Assign the RichText object to cell A1
cell = ws['A1']
cell.value = rich_text

# Save the workbook
wb.save("formatted_text.xlsx")