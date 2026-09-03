import re
from pathlib import Path


# ---------------------------------------------------------
# PROJECT DIRECTORIES
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "processed" / "extracted_text"
OUTPUT_DIR = BASE_DIR / "processed" / "cleaned_text"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# TEXT CLEANING FUNCTION
# ---------------------------------------------------------

def clean_text(text):
    """
    Clean extracted legal text while preserving
    important legal information.
    """

    # 1. Remove page markers added by our extraction script
    text = re.sub(
        r"---\s*PAGE\s+\d+\s*---",
        "",
        text,
        flags=re.IGNORECASE
    )

    # 2. Normalize Windows line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # 3. Remove excessive spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # 4. Remove spaces at the beginning/end of lines
    lines = [line.strip() for line in text.split("\n")]

    # 5. Remove excessive blank lines
    cleaned_lines = []

    previous_blank = False

    for line in lines:

        if line == "":
            if not previous_blank:
                cleaned_lines.append("")

            previous_blank = True

        else:
            cleaned_lines.append(line)
            previous_blank = False

    text = "\n".join(cleaned_lines)

    # 6. Normalize excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 7. Remove spaces before punctuation
    text = re.sub(r"\s+([,.;:])", r"\1", text)

    # 8. Remove trailing spaces
    text = "\n".join(
        line.rstrip()
        for line in text.split("\n")
    )

    # 9. Remove leading/trailing whitespace
    text = text.strip()

    return text


# ---------------------------------------------------------
# PROCESS ALL TEXT FILES
# ---------------------------------------------------------

def process_text_files():

    text_files = list(INPUT_DIR.glob("*.txt"))

    print("=" * 70)
    print("DIGILAW TEXT CLEANING")
    print("=" * 70)

    print(f"\nFound {len(text_files)} text files.\n")

    for input_file in text_files:

        print("-" * 70)
        print(f"Cleaning: {input_file.name}")

        try:

            raw_text = input_file.read_text(
                encoding="utf-8"
            )

            cleaned = clean_text(raw_text)

            output_file = OUTPUT_DIR / input_file.name

            output_file.write_text(
                cleaned,
                encoding="utf-8"
            )

            print(f"Original characters: {len(raw_text)}")
            print(f"Cleaned characters: {len(cleaned)}")
            print(f"Saved: {output_file}")

        except Exception as error:

            print(f"ERROR: {error}")

    print("\n" + "=" * 70)
    print("TEXT CLEANING COMPLETE")
    print("=" * 70)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    process_text_files()
    