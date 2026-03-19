# AI-Powered Property Diagnostic Report (DDR) Generator

A specialized Python pipeline designed to merge physical property inspection data with thermal imaging reports into a unified, AI-generated Diagnostic Report.

## 🛠️ The Challenge: "The 1,800-Image Problem"
During initial development, the source thermal PDFs revealed a complex "tiled" vector structure. Standard extraction methods resulted in **1,800+ fragmented micro-images**, making automated analysis impossible.

### The Solution: Rasterization Pipeline
I engineered a **Page-to-Pixmap Rasterization engine** using `PyMuPDF`. Instead of extracting raw assets, the system renders each page as a high-resolution (1.5x zoom) snapshot. This preserves the visual context of thermal anomalies while maintaining a clean, 1-to-1 data mapping for the AI.



## 🚀 Key Features
* **Resilient API Layer:** Integrated a **Recursive Backoff Algorithm** to handle `429 RESOURCE_EXHAUSTED` errors, ensuring the system stays stable under Free Tier rate limits.
* **Contextual Mapping:** Automatically aligns extracted text observations with the corresponding thermal page snapshots.
* **Security First:** Implemented `.gitignore` protocols to protect sensitive API keys and prevent large data bloat in version control.

## 📦 Tech Stack
* **Language:** Python 3.10+
* **Libraries:** `PyMuPDF (fitz)`, `Requests`, `python-dotenv`
* **AI Engine:** Google Gemini 1.5 Flash (via REST API)

## 🚦 How to Run
1. Clone the repository.
2. Create a `.env` file and add `GEMINI_API_KEY=your_key_here`.
3. Place your `inspection.pdf` and `thermal.pdf` in the `/inputs` folder.
4. Run: `python main.py`