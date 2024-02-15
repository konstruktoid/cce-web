#!/usr/bin/env python3
"""Convert the CCE Excel file to various formats."""

import os
import re
import urllib.request
from pathlib import Path

import pandas as pd

CCE_URL = "https://csrc.nist.gov/CSRC/media/Projects/national-vulnerability-database/documents/CCE"
CCE_FILE = "cce-COMBINED-5.20220713.xlsx"

# Generate basic HTML header
html_header = "<!DOCTYPE html>\n"
html_head = """
<html lang="en">
<head>
<title>CCE Lists</title>
<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
<meta http-equiv="content-style-type" content="text/css" />
<meta http-equiv="content-script-type" content="text/javascript" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

"""
html_header += html_head


# Generate CSS directory if it doesn't exist
css_directory = "./css"
css_file = "./css/basic.css"

if not os.path.exists(css_directory):
    os.makedirs(css_directory)

# Generate CSS variable
css_variable = (
    "<link href='../css/basic.css' type='text/css' rel='stylesheet' />\n</head>"
)

directories = ["cce_excel", "cce_csv", "cce_json", "cce_html", "cce_markdown"]
for directory in directories:
    Path(directory).mkdir(parents=True, exist_ok=True)

excel_file_path = f"./cce_excel/{CCE_FILE}"
if not os.path.exists(excel_file_path):
    url = f"{CCE_URL}/{CCE_FILE}"
    urllib.request.urlretrieve(url, excel_file_path)

# Read the Excel file
excel_file = pd.ExcelFile(f"./cce_excel/{CCE_FILE}")

# Iterate over each sheet in the Excel file
for sheet_name in excel_file.sheet_names:
    # Read the sheet into a DataFrame

    sheet = excel_file.parse(sheet_name)

    # Save the DataFrame as a CSV file
    csv_file = f"./cce_csv/{sheet_name}.csv"
    sheet.to_csv(csv_file, index=None, header=True)

    # Save the DataFrame as a JSON file
    json_file = f"./cce_json/{sheet_name}.json"
    sheet.to_json(json_file)

    # Generate Markdown file
    markdown_file = f"./cce_markdown/{sheet_name}.md"
    with open(markdown_file, "w") as file:
        file.write(f"# {sheet_name}\n\n")
        file.write(sheet.to_markdown())

    # Save the DataFrame as an HTML file
    html_sheet = sheet.replace("\n", " ", regex=True)

    html_file = f"./cce_html/{sheet_name}.html"
    html_sheet.to_html(html_file, index=False, header=True)

    # Write HTML header and CSS variable to the HTML file
    with open(html_file, "r+") as file:
        content = file.read()
        content = re.sub(r"<table.*?>", "<table>", content)
        content = re.sub(r"<tr.*?>", "<tr>", content)
        content = re.sub(r"&amp;", "&", content)

        file.seek(0, 0)
        file.write(html_header)
        file.write(css_variable)
        file.write("\n<body>\n")
        file.write(content)
        file.write("\n</body>\n</html>")
        file.close()

    # Generate index.html with links to the generated HTML files
    index_file = "./index.html"
    with open(index_file, "w") as file:
        file.write(html_header)
        file.write(
            "<link href='./css/basic.css' type='text/css' rel='stylesheet' />\n</head>",
        )
        file.write("\n<body>\n")
        file.write("<h1>NIST NCP CCE lists</h1>\n")
        file.write(
            '<p><a href="https://ncp.nist.gov/cce">NIST NCP CCE lists</a> converted to various formats</p>\n',
        )
        for sheet_name in excel_file.sheet_names:
            file.write(
                f'<b>{sheet_name.upper()}</b> <a href="./cce_html/{sheet_name}.html">html</a> <a href="./cce_markdown/{sheet_name}.md">markdown</a> <a href="./cce_json/{sheet_name}.json">json</a> <a href="./cce_csv/{sheet_name}.csv">csv</a><br>\n',
            )
        file.write("\n</body>\n</html>")
        file.close()
