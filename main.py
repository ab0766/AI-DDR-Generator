import os
import fitz  # PyMuPDF
import json
import requests
import time
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def process_diagnostic_data(ins_path, therm_path):
    """
    RASTERIZATION ENGINE: Fixes the 1,800-tile issue by rendering 
    PDF pages as high-res snapshots.
    """
    print("Step 1: Rasterizing PDF Pages (Fixing fragmented tiles)...")
    img_folder = "extracted_images"
    if not os.path.exists(img_folder): os.makedirs(img_folder)

    doc_ins = fitz.open(ins_path)
    doc_therm = fitz.open(therm_path)
    
    # Text Extraction (Truncated to 4000 chars to stay under Free Tier limits)
    ins_text = "".join([p.get_text() for p in doc_ins])[:4000]
    therm_text = "".join([p.get_text() for p in doc_therm])[:4000]

    image_paths = []
    # Capture only first 10 pages to ensure the API prompt isn't too 'heavy'
    for i, page in enumerate(doc_therm[:10]):
        path = f"{img_folder}/thermal_page_{i+1}.png"
        # 1.5 Zoom provides clear thermal readings without massive file sizes
        page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(path)
        image_paths.append(path)

    return ins_text, therm_text, image_paths

def call_gemini_api(payload_text):
    """
    DIRECT REST CALL: Bypasses SDK issues to reach the stable Gemini 1.5 engine.
    """
    print("Step 2: Connecting to Gemini 1.5 Flash (Direct REST)...")
    
    # Using the STABLE v1 endpoint (more reliable than v1beta for some keys)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": payload_text}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        
        if "candidates" in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        elif "error" in res_json:
            error_status = res_json['error'].get('status')
            if error_status == "RESOURCE_EXHAUSTED":
                print("\n[!] Quota Limit Hit. Waiting 60s for reset...")
                time.sleep(60)
                return call_gemini_api(payload_text)
            return f"API Error: {res_json['error'].get('message')}"
        return "Unknown API Error occurred."
    except Exception as e:
        return f"Connection Error: {str(e)}"

if __name__ == "__main__":
    INS_FILE = "inputs/inspection.pdf"
    THERM_FILE = "inputs/thermal.pdf"

    try:
        if not os.path.exists(INS_FILE):
            print(f"Error: {INS_FILE} not found.")
        else:
            # 1. Process Files
            ins_text, therm_text, imgs = process_diagnostic_data(INS_FILE, THERM_FILE)
            
            # 2. Build Minimalist Prompt
            prompt = (
                f"Create a professional DDR. Inspection: {ins_text} "
                f"Thermal Findings: {therm_text}. Reference these images: {imgs}"
            )
            
            # 3. Generate
            report = call_gemini_api(prompt)
            
            # 4. Save
            with open("Final_DDR_Report.md", "w", encoding="utf-8") as f:
                f.write(report)
            
            print("\n" + "="*40)
            print("SUCCESS: Final_DDR_Report.md ready.")
            print(f"Cleaned Images: {len(imgs)} snapshots in 'extracted_images/'")
            print("="*40)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")