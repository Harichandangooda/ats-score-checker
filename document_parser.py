import re
import pdfplumber
from docx import Document
from pathlib import Path

canonical_sections_aliases = {
    "contact": [
        "contact",
        "contact information",
        "personal information"
    ],

    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career summary",
        "objective",
        "career objective",
        "about me"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
        "industry experience"
    ],

    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "technical competencies",
        "key skills",
        "technologies",
        "technical expertise",
        "competencies",
        "skills and tools",
        "tools",
        "technical skills and tools",
        "technologies and tools"
    ],

    "projects": [
        "projects",
        "project experience",
        "selected projects",
        "academic projects",
        "personal projects",
        "research projects"
    ],

    "education": [
        "education",
        "academic background",
        "academics",
        "educational background",
        "qualifications"
    ],

    "certifications": [
        "certifications",
        "licenses",
        "licenses and certifications",
        "professional certifications",
        "certificates"
    ],

    "publications": [
        "publications",
        "research publications",
        "papers",
        "journal publications"
    ],

    "awards": [
        "awards",
        "honors",
        "honors and awards",
        "achievements"
    ],

    "leadership": [
        "leadership",
        "leadership experience",
        "positions of responsibility",
        "activities"
    ],

    "other": []
}


def extract_text_from_pdf(path):
    with pdfplumber.open(str(path)) as pdf:
            text = ""
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    return text

def extract_text_from_docx(path):
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_file(file_path_obj):
    path = Path(file_path_obj)
    suffix = path.suffix.lower()

    if suffix not in [".pdf", ".docx"]:
        raise ValueError(f"Unsupported file type: {suffix}. Please upload a PDF or DOCX resume.")

    if suffix == ".pdf":
        return extract_text_from_pdf(path)
        
    elif suffix == ".docx":
        return extract_text_from_docx(path)
    
    return f"Unsupported suffix {suffix}"

def normalize_spacing(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r'[ \t]+', ' ', text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def light_clean(text):
    # normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # remove tab space
    text = re.sub(r"[\t]+", " ", text)
    # remove extra whitespaces
    text = "\n".join(line.strip() for line in text.split("\n"))
    # allow atmost 1 blank line between content blocks
    text = re.sub(r"\n{3,}", "\n\n", text)
    # remove \uf0b7
    text = re.sub(r'[\uf0b7\u2022\u25cf\u25aa•▪]', '-', text)
    # return text
    return text.strip()

def normalize_header(line):
    # Normalize header for header matching
    line = line.strip().lower()
    line = re.sub(r"\s+", " ", line)
    line = line.rstrip(":")
    line = line.replace(" & ", " and ")
    return line

def build_reverse_map(canonical_sections_aliases):
    alias_to_section = {}
    for canonical, aliases in canonical_sections_aliases.items():
        # include canonical name itself as a valid alias
        all_aliases = set(aliases) | {canonical}
        for alias in all_aliases:
            key = normalize_header(alias)
            alias_to_section[key] = canonical
    return alias_to_section


def detect_and_separate_contents(text):
    # Detect and separate
        # contact info
        # summary
        # projects
        # skills
        # education
    alias_to_section = build_reverse_map(canonical_sections_aliases)
    
    current_section = "contact"
    section_to_lines = {current_section: []}

    for line in text.split("\n"):
        header_key = normalize_header(line)

        if header_key in alias_to_section:
            current_section = alias_to_section[header_key]
            section_to_lines.setdefault(current_section, [])
            continue
        section_to_lines.setdefault(current_section, [])
        section_to_lines[current_section].append(line)
    
    section_to_content = {
        section: "\n".join(lines).strip()
        for section, lines in section_to_lines.items()
        if "\n".join(lines).strip()  # drop empty sections
    }   
        
    return section_to_content

def deep_clean(sections):
    for key, content in sections.items():
        # text lower case
        cleaned_content = content.lower()
        # remove irrelevant special characters
        cleaned_content = re.sub(r'[^\x00-\x7F]+', ' ', cleaned_content)
        # remove all kinds of whitespaces
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
        # return text
        sections[key] = cleaned_content.strip()
    return sections


def process_content(raw_text):
    # light clean for easier header detection
    text_light_cleaned = light_clean(raw_text)
    # split the resume into logical sections
    section_to_content = detect_and_separate_contents(text_light_cleaned)
    # deep clean
    sections_deep_cleaned = deep_clean(section_to_content)

    return sections_deep_cleaned

def process_resume(resume_filename):
    resume_raw_text = extract_text_from_file(resume_filename)
    resume_section_wise_content = process_content(resume_raw_text)
    return resume_section_wise_content