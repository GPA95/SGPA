import csv
import os
from datetime import datetime, timezone, timedelta
import uuid
import streamlit as st

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "usage_log.csv")

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_session_id():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def extract_topic(prompt_text: str, max_length: int = 50) -> str:
    """
    Extract a concise topic/keyword from the prompt.
    Takes the first meaningful chunk (first sentence or ~50 chars).
    """
    if not prompt_text:
        return "N/A"
    
    text = prompt_text.strip()
    
    # Try to extract first sentence
    first_sentence = text.split(".")[0] if "." in text else text
    first_sentence = first_sentence.split("?")[0] if "?" in first_sentence else first_sentence
    
    # Limit length
    topic = first_sentence[:max_length].strip()
    return topic if topic else "N/A"

def detect_visual_types(response_text: str) -> str:
    """
    Detect which visual types are present in the response.
    Returns a comma-separated string of detected types: 'table', 'mermaid', 'flow', or 'none'.
    """
    if not response_text:
        return "none"
    
    detected = []
    
    # Check for Markdown tables (| ... | format)
    if "|" in response_text and response_text.count("\n") > 1:
        lines = response_text.split("\n")
        table_lines = [l for l in lines if "|" in l]
        if len(table_lines) >= 2:
            detected.append("table")
    
    # Check for Mermaid diagrams (```mermaid ... ```)
    if "```mermaid" in response_text or "flowchart" in response_text or "graph " in response_text:
        detected.append("mermaid")
    
    # Check for numbered/bulleted flows (1→ or 1. followed by →)
    if ("→" in response_text or "->") in response_text or (response_text.count("\n") and any(
        line.strip()[0].isdigit() for line in response_text.split("\n") if line.strip()
    )):
        detected.append("flow")
    
    return ",".join(detected) if detected else "none"

def log_usage(mode, sub_mode, had_pdf, prompt_text, response_text="", visuals_enabled=None):
    """
    Log usage with visual tracking and topic extraction.
    Timestamps are converted to IST (UTC+5:30).
    
    Args:
        mode: Selected mode (e.g., "💡 Explainer")
        sub_mode: Sub-mode if applicable (e.g., "📝 Generate Questions")
        had_pdf: Whether PDF was used
        prompt_text: User's input text
        response_text: Assistant's response text
        visuals_enabled: Boolean or None; whether visuals toggle was enabled
    """
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Convert UTC to IST
        utc_now = datetime.now(timezone.utc)
        ist_now = utc_now.astimezone(IST)
        
        # Detect visual types in response
        visual_types_detected = detect_visual_types(response_text)
        visuals_used = 0 if visual_types_detected == "none" else 1
        
        # Extract topic from prompt
        topic = extract_topic(prompt_text)
        
        # Handle None visuals_enabled (backward compatibility)
        if visuals_enabled is None:
            visuals_enabled = st.session_state.get("include_visuals", False)
        
        row = {
            "timestamp_ist": ist_now.isoformat(),
            "session_id": get_session_id(),
            "mode": mode,
            "sub_mode": sub_mode or "",
            "topic": topic,
            "had_pdf": int(bool(had_pdf)),
            "prompt_chars": len(prompt_text or ""),
            "response_chars": len(response_text or ""),
            "visuals_enabled": int(bool(visuals_enabled)),
            "visuals_detected": visual_types_detected,
            "visuals_used": visuals_used,
        }
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception:
        pass  # Logging must never break the app