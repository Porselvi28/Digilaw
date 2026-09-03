import json
from pathlib import Path


# ---------------------------------------------------------
# PROJECT DIRECTORIES
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "chunks"
    / "all_chunks.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "processed"
    / "chunks"
    / "chunks_with_metadata.json"
)


# ---------------------------------------------------------
# DOCUMENT METADATA
# ---------------------------------------------------------

DOCUMENT_METADATA = {

    "BHARATIYA_NYAYA_SANHITA_2023": {
        "title": "Bharatiya Nyaya Sanhita, 2023",
        "document_type": "Act",
        "year": 2023,
        "category": "Criminal Law",
        "source": "India Code"
    },

    "BHARATIYA_NAGARIK_SURAKSHA_SANHITA_2023": {
        "title": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "document_type": "Act",
        "year": 2023,
        "category": "Criminal Procedure",
        "source": "India Code"
    },

    "BHARATIYA_SAKSHYA_ADHINIYAM_2023": {
        "title": "Bharatiya Sakshya Adhiniyam, 2023",
        "document_type": "Act",
        "year": 2023,
        "category": "Evidence Law",
        "source": "India Code"
    },

    "CONSTITUTION_OF_INDIA": {
        "title": "Constitution of India",
        "document_type": "Constitution",
        "year": 1950,
        "category": "Constitutional Law",
        "source": "India Code"
    },

    "INFORMATION_TECHNOLOGY_ACT_2000": {
        "title": "Information Technology Act, 2000",
        "document_type": "Act",
        "year": 2000,
        "category": "Cyber Law",
        "source": "India Code"
    },

    "CONSUMER_PROTECTION_ACT_2019": {
        "title": "Consumer Protection Act, 2019",
        "document_type": "Act",
        "year": 2019,
        "category": "Consumer Law",
        "source": "India Code"
    },

    "MOTOR_VEHICLES_ACT_1988": {
        "title": "Motor Vehicles Act, 1988",
        "document_type": "Act",
        "year": 1988,
        "category": "Motor Vehicle Law",
        "source": "India Code"
    },

    "RIGHT_TO_INFORMATION_ACT_2005": {
        "title": "Right to Information Act, 2005",
        "document_type": "Act",
        "year": 2005,
        "category": "Right to Information",
        "source": "India Code"
    },

    "SEXUAL_HARASSMENT_OF_WOMEN_AT_WORKPLACE_ACT_2013": {
        "title": "Sexual Harassment of Women at Workplace Act, 2013",
        "document_type": "Act",
        "year": 2013,
        "category": "Women and Workplace Law",
        "source": "India Code"
    },
 

    "KESAVANANDA_BHARATI_V_STATE_OF_KERALA_1973": {
        "title": "Kesavananda Bharati v State of Kerala",
        "document_type": "Judgment",
        "year": 1973,
        "category": "Constitutional Law",
        "court": "Supreme Court of India",
        "source": "Supreme Court of India"
    },

    "MANEKA_GANDHI_V_UNION_OF_INDIA_1978": {
        "title": "Maneka Gandhi v Union of India",
        "document_type": "Judgment",
        "year": 1978,
        "category": "Constitutional Law",
        "court": "Supreme Court of India",
        "source": "Supreme Court of India"
    },

    "VISHAKA_V_STATE_OF_RAJASTHAN_1997": {
        "title": "Vishaka v State of Rajasthan",
        "document_type": "Judgment",
        "year": 1997,
        "category": "Women and Workplace Law",
        "court": "Supreme Court of India",
        "source": "Supreme Court of India"
    },

    "PUTTASWAMY_V_UNION_OF_INDIA_2017": {
        "title": "Justice K.S. Puttaswamy v Union of India",
        "document_type": "Judgment",
        "year": 2017,
        "category": "Privacy and Constitutional Law",
        "court": "Supreme Court of India",
        "source": "Supreme Court of India"
    },

    "NAVTEJ_SINGH_JOHAR_V_UNION_OF_INDIA_2018": {
        "title": "Navtej Singh Johar v Union of India",
        "document_type": "Judgment",
        "year": 2018,
        "category": "Constitutional and Human Rights Law",
        "court": "Supreme Court of India",
        "source": "Supreme Court of India"
    },

    "CONSUMER_COMPLAINT_FILING_GUIDE": {
        "title": "Consumer Complaint Filing Guide",
        "document_type": "Procedure",
        "year": 2025,
        "category": "Consumer Complaint",
        "source": "e-Jagriti"
    },

    "LEGAL_AID_APPLICATION_FORM": {
        "title": "Legal Aid Application Form",
        "document_type": "Form",
        "category": "Legal Aid",
        "source": "NALSA"
    },

    "CYBER_CRIME_COMPLAINT_PROCEDURE": {
        "title": "Cyber Crime Complaint Procedure",
        "document_type": "Procedure",
        "category": "Cyber Crime",
        "source": "Government of India"
    },

    "FIR_REGISTRATION_SOP": {
        "title": "SOP Regarding Registration of FIR and Preliminary Enquiry",
        "document_type": "Procedure",
        "category": "Police / FIR",
        "source": "BPR&D, Ministry of Home Affairs"
    },

    "RTI_ONLINE_USER_MANUAL": {
        "title": "RTI Online User Manual",
        "document_type": "Procedure",
        "category": "Right to Information",
        "source": "Government of India"
    }
}


# ---------------------------------------------------------
# ADD METADATA
# ---------------------------------------------------------

def add_metadata():

    print("=" * 70)
    print("DIGILAW METADATA ENRICHMENT")
    print("=" * 70)

    # Read chunks
    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    print(f"\nLoaded chunks: {len(chunks)}")

    updated_chunks = []

    unknown_documents = set()

    for chunk in chunks:

        document_id = chunk["metadata"]["document_id"]

        # Get predefined metadata
        extra_metadata = DOCUMENT_METADATA.get(
            document_id,
            {}
        )

        if not extra_metadata:
            unknown_documents.add(document_id)

        # Add metadata
        chunk["metadata"].update(
            extra_metadata
        )

        updated_chunks.append(chunk)

    # Save enriched chunks
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            updated_chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"\nMetadata added to {len(updated_chunks)} chunks."
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    # Report unknown documents
    if unknown_documents:

        print("\nWARNING: Metadata not found for:")

        for document in sorted(unknown_documents):
            print(f" - {document}")

    else:

        print(
            "\nAll documents received metadata successfully."
        )

    print("\n" + "=" * 70)
    print("METADATA ENRICHMENT COMPLETE")
    print("=" * 70)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    add_metadata()