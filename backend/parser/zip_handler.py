import zipfile
from io import BytesIO


def extract_files_from_zip(zip_upload):

    files = []

    with zipfile.ZipFile(BytesIO(zip_upload)) as z:

        for name in z.namelist():

            if name.lower().endswith((".pdf", ".docx")):
                files.append((name, z.read(name)))

    return files
