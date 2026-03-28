import fitz  # PyMuPDF
from docx import Document
from io import BytesIO


async def extract_text(upload_file):

    filename = upload_file.filename.lower()
    file_bytes = await upload_file.read()

    # =========================
    # PDF (PyMuPDF)
    # =========================
    if filename.endswith(".pdf"):

        text = ""

        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()

        return text.strip()

    # =========================
    # DOCX
    # =========================
    elif filename.endswith(".docx"):

        doc = Document(BytesIO(file_bytes))

        text = ""
        for para in doc.paragraphs:
            text += para.text + " "

        return text.strip()

    else:
        raise ValueError("Unsupported file format")
