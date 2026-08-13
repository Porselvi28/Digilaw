import re
import json
from pathlib import Path


# =========================================================
# PROJECT DIRECTORIES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "processed" / "cleaned_text"
OUTPUT_DIR = BASE_DIR / "processed" / "chunks"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# DOCUMENT TYPE DETECTION
# =========================================================

def detect_document_type(filename):
    """
    Identify the type of legal document from its filename.
    """

    name = filename.lower()

    # -------------------------
    # ACTS
    # -------------------------

    if "bharatiya_nyaya_sanhita" in name:
        return "Act"

    if "bharatiya_nagarik_suraksha" in name:
        return "Act"

    if "bharatiya_sakshya_adhiniyam" in name:
        return "Act"

    if "constitution" in name:
        return "Act"

    if "act_" in name or "_act" in name:
        return "Act"

    # -------------------------
    # JUDGMENTS
    # -------------------------

    if any(word in name for word in [
        "kesavananda",
        "maneka_gandhi",
        "vishaka",
        "puttaswamy",
        "navtej"
    ]):
        return "Judgment"

    # -------------------------
    # PROCEDURES / GUIDES
    # -------------------------

    if any(word in name for word in [
        "procedure",
        "sop",
        "manual",
        "guide",
        "application_form"
    ]):
        return "Procedure"

    return "Other"


# =========================================================
# DOCUMENT ID
# =========================================================

def create_document_id(filename):
    """
    Create a clean document ID from the filename.
    """

    name = Path(filename).stem

    name = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        name
    )

    return name.upper()


# =========================================================
# SECTION DETECTION
# =========================================================

def detect_section(text):
    """
    Detect a legal section number from the beginning
    of a chunk.
    """

    patterns = [

        # Example:
        # Section 103 ...
        r"^Section\s+(\d+[A-Za-z]?)",

        # Example:
        # 103. Punishment...
        r"^(\d+[A-Za-z]?)\.\s+[A-Z]",

        # Example:
        # 103. ...
        r"^(\d+[A-Za-z]?)\.\s+"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


# =========================================================
# ACT CHUNKING
# =========================================================

def chunk_act(text, document_id, filename):
    """
    Split an Act using actual section boundaries.

    The table of contents / arrangement of sections is
    removed before section detection.
    """

    # -----------------------------------------------------
    # REMOVE TABLE OF CONTENTS
    # -----------------------------------------------------

    # India Code Acts usually contain the actual Act after:
    #
    # BE it enacted by Parliament...
    #
    # Everything before this is not treated as a legal
    # section.

    enactment_match = re.search(
        r"BE\s+it\s+enacted\s+by\s+Parliament",
        text,
        re.IGNORECASE
    )

    if enactment_match:

        text = text[
            enactment_match.start():
        ]

    # -----------------------------------------------------
    # SECTION PATTERN
    # -----------------------------------------------------

    section_pattern = (
        r"(?m)"
        r"(?=^"
        r"(?:Section\s+)?"
        r"\d+[A-Za-z]?\.\s+"
        r")"
    )

    sections = re.split(
        section_pattern,
        text
    )

    chunks = []

    chunk_number = 1

    # -----------------------------------------------------
    # PROCESS SECTIONS
    # -----------------------------------------------------

    for section_text in sections:

        section_text = section_text.strip()

        if not section_text:
            continue

        section_number = detect_section(
            section_text
        )

        # Ignore content that is not a numbered section
        if section_number is None:
            continue

        # -------------------------------------------------
        # MAXIMUM CHUNK SIZE
        # -------------------------------------------------

        max_characters = 2500

        # -------------------------------------------------
        # NORMAL SECTION
        # -------------------------------------------------

        if len(section_text) <= max_characters:

            chunks.append({

                "chunk_id": (
                    f"{document_id}_"
                    f"{chunk_number:04d}"
                ),

                "text": section_text,

                "metadata": {

                    "document_id": document_id,

                    "document_type": "Act",

                    "source_file": filename,

                    "section": section_number
                }
            })

            chunk_number += 1

        # -------------------------------------------------
        # LARGE SECTION
        # -------------------------------------------------

        else:

            start = 0

            part_number = 1

            while start < len(section_text):

                end = start + max_characters

                chunk_text = section_text[
                    start:end
                ].strip()

                chunks.append({

                    "chunk_id": (
                        f"{document_id}_"
                        f"{chunk_number:04d}_"
                        f"PART_{part_number}"
                    ),

                    "text": chunk_text,

                    "metadata": {

                        "document_id": document_id,

                        "document_type": "Act",

                        "source_file": filename,

                        "section": section_number,

                        "part": part_number
                    }
                })

                # -------------------------------------------------
                # OVERLAP
                # -------------------------------------------------

                start = end - 200

                part_number += 1

                chunk_number += 1

    return chunks


# =========================================================
# GENERAL DOCUMENT CHUNKING
# =========================================================

def chunk_general_document(
    text,
    document_id,
    document_type,
    filename
):
    """
    Chunk judgments, procedures, forms and other
    non-Act documents using paragraphs.
    """

    # -----------------------------------------------------
    # SPLIT INTO PARAGRAPHS
    # -----------------------------------------------------

    paragraphs = re.split(
        r"\n\s*\n",
        text
    )

    chunks = []

    current_chunk = ""

    chunk_number = 1

    max_characters = 2500

    # -----------------------------------------------------
    # BUILD CHUNKS
    # -----------------------------------------------------

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # -------------------------------------------------
        # ADD TO CURRENT CHUNK
        # -------------------------------------------------

        if (
            len(current_chunk)
            + len(paragraph)
            + 2
            <= max_characters
        ):

            if current_chunk:

                current_chunk += "\n\n"

            current_chunk += paragraph

        # -------------------------------------------------
        # CURRENT CHUNK FULL
        # -------------------------------------------------

        else:

            if current_chunk:

                chunks.append({

                    "chunk_id": (
                        f"{document_id}_"
                        f"{chunk_number:04d}"
                    ),

                    "text": current_chunk,

                    "metadata": {

                        "document_id": document_id,

                        "document_type": document_type,

                        "source_file": filename
                    }
                })

                chunk_number += 1

            # Start a new chunk
            current_chunk = paragraph

    # -----------------------------------------------------
    # SAVE FINAL CHUNK
    # -----------------------------------------------------

    if current_chunk:

        chunks.append({

            "chunk_id": (
                f"{document_id}_"
                f"{chunk_number:04d}"
            ),

            "text": current_chunk,

            "metadata": {

                "document_id": document_id,

                "document_type": document_type,

                "source_file": filename
            }
        })

    return chunks


# =========================================================
# PROCESS ALL DOCUMENTS
# =========================================================

def process_documents():

    text_files = list(
        INPUT_DIR.glob("*.txt")
    )

    print("=" * 70)

    print(
        "DIGILAW DOCUMENT CHUNKING"
    )

    print("=" * 70)

    print(
        f"\nFound {len(text_files)} cleaned documents.\n"
    )

    all_chunks = []

    # -----------------------------------------------------
    # PROCESS EACH FILE
    # -----------------------------------------------------

    for input_file in text_files:

        print("-" * 70)

        print(
            f"Processing: {input_file.name}"
        )

        try:

            # ---------------------------------------------
            # READ TEXT
            # ---------------------------------------------

            text = input_file.read_text(
                encoding="utf-8"
            )

            # ---------------------------------------------
            # DOCUMENT INFORMATION
            # ---------------------------------------------

            document_id = create_document_id(
                input_file.name
            )

            document_type = detect_document_type(
                input_file.name
            )

            # ---------------------------------------------
            # CHUNK DOCUMENT
            # ---------------------------------------------

            if document_type == "Act":

                chunks = chunk_act(
                    text,
                    document_id,
                    input_file.name
                )

            else:

                chunks = chunk_general_document(
                    text,
                    document_id,
                    document_type,
                    input_file.name
                )

            # ---------------------------------------------
            # ADD TO GLOBAL LIST
            # ---------------------------------------------

            all_chunks.extend(
                chunks
            )

            print(
                f"Document type: {document_type}"
            )

            print(
                f"Chunks created: {len(chunks)}"
            )

        except Exception as error:

            print(
                f"ERROR: {error}"
            )

    # =====================================================
    # SAVE ALL CHUNKS
    # =====================================================

    output_file = (
        OUTPUT_DIR
        / "all_chunks.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    # =====================================================
    # FINAL OUTPUT
    # =====================================================

    print("\n" + "=" * 70)

    print(
        "CHUNKING COMPLETE"
    )

    print("=" * 70)

    print(
        f"\nTotal chunks created: "
        f"{len(all_chunks)}"
    )

    print(
        f"Saved to: {output_file}"
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    process_documents()