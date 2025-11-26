import requests

# ----------------- CONFIG -----------------
BACKEND_URL = "http://localhost:8000/upload-pdf/"  # backend endpoint
ADMIN_TOKEN = "MySuperSecretToken123"  # same token as in .env
PDF_PATH = r"D:\Uploads\Pune university Certificate.pdf"  # path to your PDF
# -----------------------------------------

def upload_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path.split("\\")[-1], f, "application/pdf")}
        headers = {"x-admin-token": ADMIN_TOKEN}
        response = requests.post(BACKEND_URL, files=files, headers=headers)
        return response.json()

if __name__ == "__main__":
    result = upload_pdf(PDF_PATH)
    print(result)
