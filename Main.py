import pymupdf
import re
import json

doc = pymupdf.open("a.pdf")  # open a document

out = open("output.txt", "wb")  # create a text output
for page in doc:  # iterate the document pages
    text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
    out.write(text)  # write text of page
    out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)
out.close()

for page_index in range(len(doc)):  # iterate over pdf pages
    page = doc[page_index]  # get the page
    image_list = page.get_images()

    # print the number of images found on the page
    if image_list:
        print(f"Found {len(image_list)} images on page {page_index}")
    else:
        print("No images found on page", page_index)

    for image_index, img in enumerate(image_list, start=1):  # enumerate the image list
        xref = img[0]  # get the XREF of the image
        pix = pymupdf.Pixmap(doc, xref)  # create a Pixmap

        if pix.n - pix.alpha > 3:  # CMYK: convert to RGB first
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

        pix.save("page_%s-image_%s.png" % (page_index, image_index))  # save the image as png
        pix = None

url_regex = r"https?://\S+"

# Extract links from each page
all_links = []
for page_number in range(len(doc)):
    page = doc[page_number]
    text = page.get_text()
    links = re.findall(url_regex, text)
    all_links.extend(links)

# Write the extracted links to a new text file
with open("links.txt", "w", encoding="utf-8") as file:
    for link in all_links:
        file.write(link + "\n")

# Create a dictionary for each page
pages_data = []
for i in range(len(doc)):
    page = doc[i]
    images = [f"page_{i + 1}-image_{j + 1}.png" for j in range(len(page.get_images()))]
    links = [link for link in all_links if link in page.get_text()]
    pages_data.append({
        "page_number": i + 1,
        "text": page.get_text(),
        "images": images,
        "links": links
    })

# Write the data to a JSON file
with open("output.json", "w") as json_file:
    json.dump(pages_data, json_file, indent=4)

doc.close()
