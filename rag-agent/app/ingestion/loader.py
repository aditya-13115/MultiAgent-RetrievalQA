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
            # FIX: Clean out the tags specifically to avoid ID confusion 
            text = re.sub(r'\\', '', page.get_text())
            full_text += text
        doc.close()

        # Split the text by Article ID patterns (01 through 21) followed by thematic badges 
        pattern = r'(\d{2})\s+(?:MARKET|SURVEY|CLINICAL|RESEARCH|ETHICS|BREAKING)'
        parts = re.split(pattern, full_text)

        # parts[0] is header info; then [id1, content1, id2, content2...]
        for i in range(1, len(parts), 2):
            art_id = parts[i]
            content = parts[i+1]
            
            # Extract the first URL found in this block [cite: 253]
            url_match = re.search(r'(https?://[^\s\n]+)', content)
            if url_match:
                url = url_match.group(1).strip().rstrip('.,')
                
                # Title is typically the first non-empty line after the ID [cite: 253]
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                title = lines[0] if lines else f"Article {art_id}"
                
                metadata_list.append({
                    "article_number": art_id,
                    "title": title,
                    "url": url
                })
        
        print(f"--- Metadata Extraction: Found {len(metadata_list)}/21 articles ---")
    except Exception as e:
        logger.error(f"Error parsing corpus PDF with PyMuPDF: {e}")
    
    return metadata_list

def extract_text_from_html(url):
    """Scrapes text from a live URL using BeautifulSoup."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Clean the HTML to extract only relevant text [cite: 259, 260]
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
            
        return soup.get_text(separator=' ', strip=True)
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
        art_num = item['article_number']
        url = item['url']
        
        text = extract_text_from_html(url)
        
        if text.strip():
            print(f"SUCCESS: Fetched Art. {art_num} | {item['title'][:50]}...")
            success_count += 1
            docs.append({
                "text": text,
                "metadata": {
                    "doc_id": f"Art. {art_num}", 
                    "title": item["title"],
                    "url": url
                }
            })
        else:
            print(f"FAIL: Could not fetch Art. {art_num} from {url}")
            fail_count += 1

    print(f"\n--- Fetching Complete: {success_count} Successes, {fail_count} Failures ---\n")
    return docs