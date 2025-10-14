import pdfplumber
import re
from .models import StudentResult

def process_pdf(pdf_obj):
    text = ""
    with pdfplumber.open(pdf_obj.file.path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    # Example pattern for multiple semesters (1-8)
    # e.g., 748010 { gpa1: 3.12, gpa3: ref, gpa5: 2.90, ref_sub: 27141(T) }
    pattern = r'(\d+)\s*\{([^\}]+)\}'
    matches = re.findall(pattern, text)

    for match in matches:
        roll = match[0]
        data = match[1]

        # Extract GPA and ref_subjects
        gpa_fields = {}
        ref_subjects = ""
        gpa_pattern = r'gpa(\d+):\s*([\d.]+|ref)'
        for gpa_match in re.findall(gpa_pattern, data):
            sem, value = gpa_match
            gpa_fields[f"gpa{sem}"] = value

        ref_match = re.search(r'ref_sub:\s*([0-9T,P, ]+)', data)
        if ref_match:
            ref_subjects = ref_match.group(1).strip()

        # Create StudentResult with only available GPA
        student_data = {
            'pdf': pdf_obj,
            'roll': roll,
            'ref_subjects': ref_subjects
        }
        student_data.update(gpa_fields)

        StudentResult.objects.create(**student_data)

    pdf_obj.processed = True
    pdf_obj.save()
