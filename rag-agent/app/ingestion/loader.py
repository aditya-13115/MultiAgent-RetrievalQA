import fitz  # PyMuPDF
import re
import requests
from bs4 import BeautifulSoup
from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_metadata_from_corpus_pdf(pdf_path):
    """
    Uses PyMuPDF to extract text and find all 21 article IDs and URLs.
    """
    metadata_list = []
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            text = re.sub(r"\\", "", page.get_text())
            full_text += text
        doc.close()

        pattern = r"(\d{2})\s+(?:MARKET|SURVEY|CLINICAL|RESEARCH|ETHICS|BREAKING)"
        parts = re.split(pattern, full_text)

        for i in range(1, len(parts), 2):
            art_id = parts[i]
            content = parts[i + 1]

            url_match = re.search(r"https?://[^\s]+", content)

            if url_match:
                url = url_match.group(0)

                url = url.replace(" ", "")
                url = url.replace("\n", "")
                url = url.strip().rstrip(".,)")

                # ✅ HARD FIX FOR ARTICLE 11
                if art_id == "11":
                    url = "https://www.sciencedirect.com/science/article/pii/S0031699725075118/pdfft?md5=581315c2472a6567c95c9b674e966e0c&pid=1-s2.0-S0031699725075118-main.pdf"

                lines = [l.strip() for l in content.split("\n") if l.strip()]
                title = lines[0] if lines else f"Article {art_id}"

                metadata_list.append(
                    {"article_number": art_id, "title": title, "url": url}
                )

        print(f"--- Metadata Extraction: Found {len(metadata_list)}/21 articles ---")
    except Exception as e:
        logger.error(f"Error parsing corpus PDF with PyMuPDF: {e}")

    return metadata_list


def extract_text_from_html(url):
    """Scrapes text from a live URL using BeautifulSoup."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        # ✅ HANDLE PDF (for Article 11)
        if url.endswith(".pdf") or "pdfft" in url:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            with open("temp.pdf", "wb") as f:
                f.write(response.content)

            pdf = fitz.open("temp.pdf")
            text = ""
            for page in pdf:
                text += page.get_text()
            pdf.close()

            return text.strip()

        # Normal HTML
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()

        return soup.get_text(separator=" ", strip=True)

    except Exception as e:
        return ""


def load_documents(corpus_pdf_path):
    """
    Fetches article metadata from PDF and scrapes the content.
    """
    corpus_metadata = extract_metadata_from_corpus_pdf(corpus_pdf_path)

    docs = []
    success_count = 0
    fail_count = 0

    print(f"\n--- Starting Document Fetching (Total: {len(corpus_metadata)}) ---")

    for item in corpus_metadata:
        art_num = item["article_number"]
        url = item["url"]

        text = extract_text_from_html(url)

        if text.strip():
            print(f"SUCCESS: Fetched Art. {art_num} | {item['title'][:50]}...")
            success_count += 1
            docs.append(
                {
                    "text": text,
                    "metadata": {
                        "doc_id": f"Art. {art_num}",
                        "title": item["title"],
                        "url": url,
                    },
                }
            )
        else:
            print(f"FAIL: Could not fetch Art. {art_num} from {url}")
            fail_count += 1

    print(
        f"\n--- Fetching Complete: {success_count} Successes, {fail_count} Failures ---\n"
    )
    return docs
