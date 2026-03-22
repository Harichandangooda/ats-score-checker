import os

from dotenv import load_dotenv
load_dotenv(override=True)

from resume_ats_score_builder import chat
import gradio as gr

if __name__ == "__main__":
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="slate",
        neutral_hue="slate",
    )
    custom_css = """
        .app-shell {
            max-width: 1360px;
            margin: 0 auto;
            padding-top: 20px;
        }
        .hero {
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 18px 20px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            margin-bottom: 14px;
        }
        .hint {
            font-size: 14px;
            color: #475569;
            margin-top: 6px;
        }
        .full-width-btn button {
            width: 100% !important;
        }
        """

    with gr.Blocks(title="ATS Score Checker") as demo:
        with gr.Column(elem_classes=["app-shell"]):
            gr.Markdown(
                """
                <div class="hero">
                  <h1 style="margin:0;">ATS Resume Match Analyzer</h1>
                  <p class="hint">
                    Upload your resume and paste a job description to generate a structured ATS match report.
                  </p>
                </div>
                """
            )

            with gr.Row(equal_height=True):
                with gr.Column(scale=4, min_width=420):
                    jd_text = gr.Textbox(
                        label="Job Description",
                        lines=16,
                        placeholder="Paste the full job description here...",
                    )
                    resume_file = gr.File(
                        label="Upload Resume",
                        type="filepath",
                        file_types=[".pdf", ".docx"],
                    )
                    run_btn = gr.Button(
                        "Analyze ATS Score",
                        variant="primary",
                        elem_classes=["full-width-btn"],
                    )
                    clear_btn = gr.Button(
                        "Clear",
                        variant="secondary",
                        elem_classes=["full-width-btn"],
                    )

                with gr.Column(scale=6, min_width=620):
                    chatbot = gr.Chatbot(
                        label="ATS Analysis",
                        height=640,
                        layout="bubble",
                        buttons=["copy"],
                    )

            def run_ats_analysis(resume_filename, job_description):
                fixed_message = "Evaluate this resume against the provided job description."
                chat_history = []
                stream = chat(fixed_message, chat_history, resume_filename, job_description)
                for chunk in stream:
                    yield [{"role": "assistant", "content": chunk}]

            run_btn.click(
                fn=run_ats_analysis,
                inputs=[resume_file, jd_text],
                outputs=chatbot,
            )

            clear_btn.click(
                fn=lambda: [],
                inputs=[],
                outputs=chatbot,
            )

    is_hf_space = os.getenv("SPACE_ID") is not None
    demo.launch(
        inbrowser=not is_hf_space,
        server_name="0.0.0.0" if is_hf_space else None,
        server_port=7860 if is_hf_space else None,
        theme=theme,
        css=custom_css,
    )