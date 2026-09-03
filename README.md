# AutoAce AI — Voice Tone & Acoustic Metadata Classifier 🎙️

AutoAce AI is an automated audio evaluation pipeline designed for Customer Support Quality Assurance. It leverages **Google's Gemini 3.6 Flash** model and **Pydantic** structured schemas to perform multi-dimensional acoustic, emotional, and noise analysis on batch customer calls.

---

## 🚀 Live Demo & Tester Credentials

Evaluators can access the hosted web interface on Streamlit Community Cloud:

- **Deployment URL:** https://autoace-trial.streamlit.app/
- **Demo Username:** `autoace`
- **Demo Password:** `eval2026`

> **Note on API Limits:** If you encounter a `429 Rate Limit / Resource Exhausted` error during batch evaluation, enter your personal Google AI Studio API Key in the left sidebar drawer.

---

## ✨ Features

- **Batch Processing:** Upload a `.zip` file containing customer audio recordings (`.wav`, `.mp3`, `.m4a`, `.ogg`).
- **Structured Schema Enforcement:** Guarantees deterministic outputs for metrics using Pydantic typing and strictly validated enums:
  - **Emotional Tone:** `neutral`, `satisfied`, `frustrated`, `upset`, `distressed`
  - **Emotional Intensity:** `low`, `medium`, `high`
  - **Acoustic Noise Detection:** Identifies type, presence, and severity (`none`, `low`, `medium`, `high`)
  - **Quality & Structural Metrics:** Evaluates audio impairment, speaker overlap, dead air / long silences (>2s), and confidence scores.
- **Auto-Cleanup & Fault Tolerance:** Automatic remote file deletion on Google Cloud and exponential retry logic for API rate limits.
- **Exportable Metrics:** One-click CSV export containing structured JSON output for easy integration into downstream QA systems.

---

## 🛠️ Project Structure

```text
├── app.py              # Streamlit Web UI & Authentication System
├── pipeline.py         # Audio upload, Gemini client config, & output parsing
├── requirements.txt    # Production dependencies
└── README.md           # Project documentation
💻 Local Setup & Development
If you'd like to run AutoAce locally:

Clone the repository:

Bash
git clone [https://github.com/Steven-Mantilla2/AutoAce-trial.git](https://github.com/Steven-Mantilla2/AutoAce-trial.git)
cd AutoAce-trial
Create and activate a virtual environment:

Bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Launch the application:

Bash
streamlit run app.py

📄 License
Distributed under the MIT License.
