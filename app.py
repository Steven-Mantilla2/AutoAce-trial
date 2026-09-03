import streamlit as st
import pandas as pd
import zipfile
import os
import json
import tempfile
from pipeline import analyze_audio

st.set_page_config(page_title="AutoAce Audio Classifier", layout="wide")

# Basic Auth Check
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("AutoAce Trial - Dashboard Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                # Hardcoded demo credentials for reviewer
                if username == "autoace" and password == "eval2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        return False
    return True

if check_password():
    # Logout Control in Sidebar
    with st.sidebar:
        st.markdown("### 👤 User Session")
        st.caption("Logged in as **autoace**")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()
        st.divider()

    st.title("AutoAce AI - Voice Tone & Noise Batch Evaluator")
    
    api_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    
    st.markdown("### Upload Evaluation Batch (ZIP)")
    uploaded_zip = st.file_uploader("Upload a ZIP containing audio clips (.wav/.mp3) and labels.csv", type=["zip"])

    if uploaded_zip and api_key:
        if st.button("Start Batch Processing"):
            results = []
            
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "batch.zip")
                with open(zip_path, "wb") as f:
                    f.write(uploaded_zip.read())
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Get list of audio files
                audio_files = [f for f in os.listdir(temp_dir) if f.endswith(('.wav', '.mp3', '.m4a', '.ogg'))]
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, file_name in enumerate(audio_files):
                    status_text.text(f"Processing {file_name} ({idx+1}/{len(audio_files)})...")
                    file_path = os.path.join(temp_dir, file_name)
                    
                    try:
                        # Perform analysis via pipeline.py
                        analysis_result = analyze_audio(file_path, api_key)
                        
                        res_entry = {
                            "name": file_name,
                            "status": "SUCCESS",
                            "result_json": json.dumps(analysis_result)
                        }
                        if isinstance(analysis_result, dict):
                            res_entry["tone"] = analysis_result.get("emotional_tone", "N/A")
                            res_entry["intensity"] = analysis_result.get("emotional_intensity", "N/A")
                            res_entry["confidence"] = analysis_result.get("confidence", 0.0)
                        
                        results.append(res_entry)
                    except Exception as e:
                        results.append({
                            "name": file_name,
                            "status": "FAILED",
                            "tone": "ERROR",
                            "intensity": "N/A",
                            "confidence": 0.0,
                            "result_json": json.dumps({"error": str(e)})
                        })
                    
                    progress_bar.progress((idx + 1) / len(audio_files))

                status_text.text("Batch processing complete!")
                
                # Metrics Dashboard
                df_results = pd.DataFrame(results)
                st.divider()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Processed", len(results))
                success_count = sum(1 for r in results if r["status"] == "SUCCESS")
                m2.metric("Successful Evaluations", f"{success_count}/{len(results)}")
                
                flagged = sum(1 for r in results if r.get("tone") in ["frustrated", "upset"])
                m3.metric("Flagged Tone Calls", flagged)
                
                st.markdown("### Processed Results")
                st.dataframe(df_results, use_container_width=True)
                
                csv_data = df_results[["name", "result_json"]].to_csv(index=False)
                st.download_button(
                    label="📥 Download Results CSV",
                    data=csv_data,
                    file_name="evaluation_results.csv",
                    mime="text/csv"
                )