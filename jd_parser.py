import re


jd_system_prompt = """
You are an ATS keyword extraction engine. Your job is to read a job description and output a clean, deduplicated set of keywords and requirements that can be matched against a resume.

Rules:
- Output MUST be valid JSON only. No markdown, no commentary.
- Extract ONLY what is supported by the provided job description text. Do not invent technologies, degrees, or requirements.
- Prefer concrete, matchable terms (tools, languages, frameworks, cloud services, libraries, methods, protocols, databases, platforms, job titles).
- Separate “required” vs “preferred” based on wording:
  - Required signals: “must”, “required”, “minimum”, “need”, “you will”, “we’re looking for”
  - Preferred signals: “nice to have”, “preferred”, “bonus”, “plus”
- Keep keywords in their canonical form:
  - Examples: “kubernetes” (not “k8s”), “amazon web services” AND “aws” (include both only if JD uses both), “c++” not “cpp”.
- Include short synonym lists only when the JD itself implies them (e.g., “ETL / ELT”), otherwise leave synonyms empty.
- Do not include generic filler terms like “team player”, “fast learner” unless the JD explicitly lists them as requirements under soft skills.
- Capture multi-word skills as phrases (e.g., “retrieval augmented generation”, “feature engineering”, “model deployment”, “data pipelines”).
- If a term appears in multiple places, list it once.

JSON Schema:
{
  "role_title": string | null,
  "seniority": string | null,
  "location_type": "onsite" | "hybrid" | "remote" | null,
  "must_have": {
    "skills": [string],
    "tools_and_tech": [string],
    "domains": [string],
    "education": [string],
    "years_experience": [string],
    "responsibilities": [string]
  },
  "nice_to_have": {
    "skills": [string],
    "tools_and_tech": [string],
    "domains": [string]
  },
  "soft_skills": [string],
  "keywords_flat": [string],
  "extraction_notes": [string]
}

Return "keywords_flat" as the union of must_have + nice_to_have + soft_skills, deduplicated.
"extraction_notes" should be short, only for ambiguities (e.g., “years of experience not explicitly stated”).
"""

def normalize_job_description(description: str) -> str:
    desc = description.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse 3+ newlines into exactly 2 newlines (keep one blank line)
    desc = re.sub(r'\n{3,}', '\n\n', desc)

    # Replace tabs with a space
    desc = re.sub(r'[\t]+', " ", desc)

    # Strip each line (keeps structure)
    desc = "\n".join(line.strip() for line in desc.split("\n"))

    # Normalize & in a robust way: "A&B", "A &B", "A& B", "A & B" -> "A and B"
    desc = re.sub(r'\s*&\s*', ' and ', desc)

    # Normalize common bullet artifacts to "-"
    desc = re.sub(r'[\uf0b7\u2022\u25cf\u25aa•▪]', '-', desc)

    # Remove weird non-ascii artifacts (after bullet normalization)
    desc = re.sub(r'[^\x00-\x7F]+', ' ', desc)

    # Optional: clean up repeated spaces created by replacements (but DO NOT flatten newlines)
    desc = re.sub(r'[ \t]{2,}', ' ', desc)

    return desc.strip()

def extract_keywords_from_job_description(jd_normalized):
    jd_user_prompt = f"""
        Here is the normalized user prompt. Extract ATS-matchable keywords using the required JSON schema
        Job Description:
        {jd_normalized}
        """
    jd_messages = [
        {"role": "system", "content": jd_system_prompt},
        {"role": "user", "content": jd_user_prompt}
    ]

    # return call_llm(jd_messages, False)
    return jd_messages

def process_jd(job_desc):
    desc_normalized = normalize_job_description(job_desc)
    jd_messages = extract_keywords_from_job_description(desc_normalized)
    return jd_messages