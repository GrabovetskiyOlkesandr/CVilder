import json
import re
import os
from collections import Counter
from django.shortcuts import render
from django.conf import settings
from pypdf import PdfReader
from .forms import UploadFileForm


def home_page(request):
    return render(request, 'main/index.html')


def about(request):
    return render(request, 'main/about.html')


def contact(request):
    return render(request, 'main/contact.html')


def load_all_rules():
    combined_rules = set()
    rules_dir = os.path.join(settings.BASE_DIR, 'main', 'rules')

    if not os.path.exists(rules_dir):
        return combined_rules

    for filename in os.listdir(rules_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(rules_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        clean_line = line.strip().lower()
                        if clean_line and not clean_line.startswith('#'):
                            words = re.split(r'[,\s]+', clean_line)
                            combined_rules.update(w for w in words if w)
            except Exception:
                continue
    return combined_rules


STOP_WORDS = load_all_rules()


def load_sections():
    file_path = os.path.join(settings.BASE_DIR, 'main', 'rules', 'sections.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.lower()
    except Exception:
        return ""


def get_section_text(text, section_keywords, all_keywords):
    other_keywords = [k for k in all_keywords if k not in section_keywords]
    pattern = rf"({'|'.join(section_keywords)}).*?(?={'|'.join(other_keywords)}|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(0) if match else ""


def get_clean_words(text):
    words = []
    for w in text.lower().split():
        clean = w.strip('(),:;"\'!@$%^&*~`[]{}\\|/?><.—-')
        if clean and clean not in STOP_WORDS and not clean.isdigit():
            words.append(clean)
    return words


def calculate_weighted_score(resume_text, job_desc):
    sections = load_sections()

    if not sections:
        return 0

    resume_words = Counter(get_clean_words(resume_text))

    total_weighted_score = 0
    total_possible_weight = 0
    all_headers = [k for s in sections.values() for k in s['keywords']]
    sections_found = False

    for name, data in sections.items():
        section_content = get_section_text(job_desc, data['keywords'], all_headers)

        if not section_content:
            continue

        sections_found = True
        job_section_words = get_clean_words(section_content)

        if not job_section_words:
            continue

        job_section_counter = Counter(job_section_words)
        section_max_points = sum(job_section_counter.values())

        section_current_points = sum(count for word, count in job_section_counter.items() if word in resume_words)

        section_percent = section_current_points / section_max_points if section_max_points > 0 else 0
        total_weighted_score += section_percent * data['weight']
        total_possible_weight += data['weight']

    if not sections_found:
        job_section_words = get_clean_words(job_desc)
        if not job_section_words:
            return 0
        job_section_counter = Counter(job_section_words)
        section_max_points = sum(job_section_counter.values())
        section_current_points = sum(count for word, count in job_section_counter.items() if word in resume_words)
        return min(round((section_current_points / section_max_points) * 100, 1), 100)

    if total_possible_weight == 0:
        return 0

    final_score = (total_weighted_score / total_possible_weight) * 100
    return min(round(final_score, 1), 100)


def comparison(request):
    results = []
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        all_files = []
        for key in request.FILES.keys():
            all_files.extend(request.FILES.getlist(key))

        if not all_files:
            return render(request, 'main/comparison.html',
                          {'form': form, 'message': "No files received", 'msg_type': 'danger'})

        job_description = form.data.get('job_description', '')

        for file in all_files:
            text = extract_text_from_pdf(file)
            score = calculate_weighted_score(text, job_description)

            if score >= 50:
                color, status = 'success', 'High Match'
            elif score >= 25:
                color, status = 'warning', 'Average Match'
            else:
                color, status = 'danger', 'Low Match'

            results.append({'name': file.name, 'score': score, 'color': color, 'status': status})

        results.sort(key=lambda x: x['score'], reverse=True)
        return render(request, 'main/comparison.html', {
            'form': UploadFileForm(),
            'message': f"Analysis complete for {len(all_files)} resumes",
            'msg_type': 'success',
            'results': results
        })

    return render(request, 'main/comparison.html', {'form': UploadFileForm()})