from django.shortcuts import render
from .models import ResultPDF, StudentResult
import pdfplumber
import re

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    text = text.replace("\n", " ")  # remove line breaks
    return text

# Parse PDF content and save StudentResult
def process_pdf(pdf_obj):
    text = extract_text_from_pdf(pdf_obj.file.path)

    # Match each student's result
    pattern = r'(\d+)\s*\{([^}]*)\}'
    matches = re.findall(pattern, text)

    for match in matches:
        roll = match[0]
        data = match[1]

        gpa_fields = {}
        # GPA: number or 'ref'
        gpa_pattern = r'gpa(\d+):\s*([\d.]+|ref)'
        for gpa_match in re.findall(gpa_pattern, data):
            sem, value = gpa_match
            gpa_fields[f"gpa{sem}"] = value

        # Ref subjects
        ref_match = re.search(r'ref_sub:\s*([0-9T,P, ,]+)', data)
        ref_subjects = ref_match.group(1).strip() if ref_match else ""

        # Save in DB
        student_data = {'pdf': pdf_obj, 'roll': roll, 'ref_subjects': ref_subjects}
        student_data.update(gpa_fields)
        StudentResult.objects.create(**student_data)

    pdf_obj.processed = True
    pdf_obj.save()


# Upload PDF view
def upload_pdf(request):
    message = ""
    if request.method == "POST":
        pdf_file = request.FILES['file']
        pdf_obj = ResultPDF.objects.create(file=pdf_file)
        process_pdf(pdf_obj)
        message = "PDF processed successfully!"
    return render(request, 'upload.html', {'message': message})


# Search by roll number
def search_result(request):
    query = request.GET.get('q', '')
    result = None
    if query:
        try:
            result = StudentResult.objects.get(roll=query)
        except StudentResult.DoesNotExist:
            result = None
    return render(request, 'search.html', {'result': result, 'q': query})
