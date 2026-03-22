# ATS Score Checker (LLM)

A Gradio-based ATS analysis app that compares a resume (`.pdf` or `.docx`) against a job description and returns a streamed, Markdown-formatted report.

## What This App Does

- Parses resume content from PDF or DOCX files.
- Extracts job requirements and keywords from the provided job description.
- Evaluates ATS alignment using an LLM with a scoring rubric.
- Displays a live, streamed analysis in a clean side-by-side UI.

## Tech Stack

- Python
- Gradio
- OpenAI API
- `pdfplumber` for PDF parsing
- `python-docx` for DOCX parsing

## Project Files

- `app.py` - UI layout and app launch entrypoint.
- `resume_ats_score_builder.py` - Main ATS scoring and chat/stream logic.
- `jd_parser.py` - Job description normalization and keyword extraction prompt setup.
- `document_parser.py` - Resume file text extraction and section parsing.
- `llm_handler.py` - OpenAI client initialization and API call wrapper.
- `requirements.txt` - Python dependencies.

## Prerequisites

- Python 3.10+
- OpenAI API key

## Local Setup

1. Clone the repository and enter the project folder.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

5. Run the app:

```bash
python app.py
```

## How to Use

1. Paste the full job description in the **Job Description** box.
2. Upload your resume in PDF or DOCX format.
3. Click **Analyze ATS Score**.
4. View streamed ATS analysis in the right panel.

## Deploy to Hugging Face Spaces

1. Create a new Space and select **Gradio** SDK.
2. Push this project (including `app.py` and `requirements.txt`) to the Space repo.
3. In Space settings, add secret:
   - `OPENAI_API_KEY`
4. Open the Space logs if build/runtime issues appear.

## Notes

- The app uses environment variables for secrets; do not commit `.env`.
- The UI is optimized for side-by-side desktop usage and streams responses progressively.
