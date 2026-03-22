from document_parser import process_resume
from jd_parser import process_jd
from llm_handler import call_llm

system_prompt = """
You are an ATS evaluation engine.

Your task is to evaluate a resume against a structured set of job requirements and produce:

1) A weighted ATS match score (0–100)
2) A section-by-section breakdown
3) Missing required keywords
4) Matched strengths
5) Specific improvement recommendations
6) Rewritten bullet suggestions tailored to the job

Rules:
- Output MUST be Markdown only.
- Do NOT use JSON or code blocks.
- Do NOT hallucinate skills not present in the resume.
- Only mark a keyword as matched if it is explicitly present or strongly implied in the resume content.
- Do NOT invent experience.
- Use evidence from the resume text when justifying matches.
- Prefer measurable impact language when suggesting rewrites.
- Preserve truthfulness.

Scoring Rubric (strictly follow):

Total Score = 100

40 points → Required skills & tools match
20 points → Role alignment (domain + responsibilities relevance)
15 points → Evidence of impact (metrics, results, scale)
10 points → Education / seniority alignment
15 points → Clarity & ATS readiness (structured sections, clear bullets, no ambiguity)

Scoring must be proportional. Do not give perfect scores unless truly justified.

Use this markdown structure:

# ATS Analysis Report
## Overall Match Score
## Score Breakdown
## Matched Required Keywords
## Missing Required Keywords
## Matched Nice-to-Have Keywords
## Strongest Sections
## Weakest Sections
## Rewrite Suggestions
### Experience
### Projects
### Skills
## Top 5 Priority Fixes
"""
def chat(message, history, resume_filename, job_description):
    if (resume_filename is None) or (resume_filename == ""):
        yield "To compute the ATS score, you resume must be uploaded."
        return
    resume_sections_json = process_resume(resume_filename) 
    jd_keywords_json = call_llm(process_jd(job_description), False) 
    history = [{"role": h["role"], "content": h["content"]} for h in history] 
    user_prompt = f""" 
        {message} Evaluate the following resume
        against the extracted job requirements. 
        JOB REQUIREMENTS (Structured JSON): 
        {jd_keywords_json} 
        RESUME (Structured JSON): 
        {resume_sections_json} 
        Follow the scoring rubric strictly and 
        return Markdown only. 
    """ 
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_prompt}] 
    stream = call_llm(messages, True)
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ""
        yield response
