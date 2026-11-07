"""Pure PDF operations shared by pdf_tool_app.py and dts_tool_app.py."""
import os
import subprocess

from PIL import Image
from pypdf import PdfWriter
import fitz


def merge_pdfs(file_list):
    """Merges file_list into Merged.pdf next to the first file. Returns the output path."""
    output_path = os.path.join(os.path.dirname(file_list[0]), "Merged.pdf")
    merger = PdfWriter()
    for pdf in file_list:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()
    return output_path


def images_to_pdf(file_list):
    """Combines file_list images into Images.pdf next to the first file. Returns the output path."""
    output_path = os.path.join(os.path.dirname(file_list[0]), "Images.pdf")
    images = [Image.open(f).convert("RGB") for f in file_list]
    images[0].save(output_path, save_all=True, append_images=images[1:])
    return output_path


def pdf_to_jpg(file_list):
    """Exports every page of each PDF in file_list to JPGs alongside the source file."""
    for pdf_path in file_list:
        out_dir = os.path.dirname(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        pdf = fitz.open(pdf_path)
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            pix = page.get_pixmap(dpi=300)
            pix.save(os.path.join(out_dir, f"{base_name}_page_{page_num + 1}.jpg"))
        pdf.close()


def compress_pdf(file_list):
    """Compresses each PDF in file_list via Ghostscript, writing '<name>Compressed.pdf'."""
    for pdf_path in file_list:
        out_dir = os.path.dirname(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(out_dir, f"{base_name}Compressed.pdf")
        command = [
            "gswin64c",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            pdf_path,
        ]
        subprocess.run(command, check=True)
