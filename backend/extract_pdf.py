import pymupdf
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent

LEGAL_DATA_DIR = BASE_DIR / "legal_data"
OUTPUT_DIR = BASE_DIR / "processed" / "extracted_text"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_pdf_text(pdf_path):
    """Extract text from a PDF and return text + statistics."""

    document = pymupdf.open(pdf_path)

    extracted_pages = []
    total_characters = 0
    pages_with_text = 0

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text").strip()

        if text:
            pages_with_text += 1
            total_characters += len(text)

        extracted_pages.append(
            f"\n--- PAGE {page_number} ---\n{text}"
        )

    total_pages = len(document)

    document.close()

    full_text = "\n".join(extracted_pages)

    return full_text, total_pages, pages_with_text, total_characters


def process_pdfs():

    pdf_files = list(LEGAL_DATA_DIR.rglob("*.pdf"))

    print("=" * 70)
    print("DIGILAW PDF EXTRACTION AND QUALITY CHECK")
    print("=" * 70)

    print(f"\nFound {len(pdf_files)} PDF files.\n")

    for pdf_path in pdf_files:

        print("-" * 70)
        print(f"Processing: {pdf_path.name}")

        try:

            text, total_pages, pages_with_text, total_characters = (
                extract_pdf_text(pdf_path)
            )

            output_file = OUTPUT_DIR / f"{pdf_path.stem}.txt"

            output_file.write_text(
                text,
                encoding="utf-8"
            )

            # Calculate percentage of pages containing text
            if total_pages > 0:
                text_page_percentage = (
                    pages_with_text / total_pages
                ) * 100
            else:
                text_page_percentage = 0

            print(f"Pages: {total_pages}")
            print(f"Pages with text: {pages_with_text}")
            print(f"Characters extracted: {total_characters}")
            print(f"Text coverage: {text_page_percentage:.1f}%")

            # Classify extraction quality
            if total_characters < 500:
                status = "OCR REQUIRED"

            elif text_page_percentage < 30:
                status = "LIKELY SCANNED / OCR NEEDED"

            elif text_page_percentage < 80:
                status = "PARTIAL TEXT / REVIEW"

            else:
                status = "TEXT PDF"

            print(f"Status: {status}")
            print(f"Saved: {output_file}")

        except Exception as error:

            print(f"ERROR: {error}")

    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    process_pdfs()