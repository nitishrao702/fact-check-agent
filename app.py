import streamlit as st
import pypdf
import json
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Fact-Check Agent | Truth Layer", page_icon="🛡️", layout="wide")

st.title("🛡️ The 'Fact-Check' Agent — Truth Layer App")
st.subheader("Automated Claim Verification Platform")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("Configuration")
st.sidebar.markdown("Provide a Gemini API Key to power the Fact-Checking Agent.")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    """Extracts raw text content from an uploaded PDF file."""
    pdf_reader = pypdf.PdfReader(uploaded_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

def isolate_claims(text, api_key):
    """Uses Gemini to identify specific numerical, statistical, or financial claims."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    prompt = f"""
    You are an expert fact-checking compiler. Analyze the text below and extract exactly 3 to 5 critical statements that contain hard statistics, specific dates, technical milestones, or financial claims that can be objectively cross-referenced on the live internet.
    
    Format your response STRICTLY as a valid JSON array of objects, where each object has two fields:
    "claim": "The exact claim text or precise paraphrase"
    "search_query": "An optimized short search engine query to verify this specific fact"
    
    Text to analyze:
    {text}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().lstrip("```json").rstrip("```").strip()
        return json.loads(cleaned_text)
    except Exception as e:
        st.error(f"Error parsing claims: {e}")
        return []

def query_live_web(search_query):
    """Performs a live web search using DuckDuckGo to pull context snippets."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(search_query, max_results=3)]
            combined_context = "\n".join([f"- {res['body']} (Source: {res['href']})" for res in results])
            return combined_context if combined_context else "No real-time web results found."
    except Exception:
        return "Search utility temporarily unavailable."

def evaluate_claim(claim, web_context, api_key):
    """Cross-references a claim against live web data using Gemini."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    You are an impartial objective factual truth engine. 
    Cross-reference the given claim against the gathered Live Web Context.
    
    Claim: {claim}
    Live Web Context: {web_context}
    
    Determine the verdict. Select exactly one of these labels:
    - VERIFIED: If the context directly supports or precisely matches the claim figures and facts.
    - INACCURATE: If the statistic is outdated, slightly miscalculated, or distorted compared to facts.
    - FALSE: If the claim contradicts the real facts, or absolutely no matching evidence is found.
    
    Provide your response in JSON format matching this schema:
    {{
       "verdict": "VERIFIED" or "INACCURATE" or "FLASE",
       "reasoning": "A concise, 2-sentence explanation of why, stating the real factual figures found on the web if the claim was inaccurate."
    }}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().lstrip("```json").rstrip("```").strip()
        return json.loads(cleaned_text)
    except Exception:
        return {"verdict": "FALSE", "reasoning": "Unable to complete evaluation validation loop."}

# --- MAIN APP LOGIC ---
uploaded_file = st.file_uploader("Upload Your Marketing/Product Document (PDF)", type=["pdf"])

if uploaded_file is not None:
    if not api_key:
        st.warning("Please supply a valid Gemini API Key in the sidebar to begin automated analysis.")
    else:
        with st.spinner("Step 1: Extracting text structure from document..."):
            raw_text = extract_text_from_pdf(uploaded_file)
        
        if raw_text.strip() == "":
            st.error("No valid text could be processed from this PDF. Please verify document formatting.")
        else:
            with st.spinner("Step 2: Isolating key statistical claims via AI..."):
                claims_list = isolate_claims(raw_text, api_key)
            
            if not claims_list:
                st.info("No specific verifiable statistical claims were isolated from the document.")
            else:
                st.success(f"Isolated {len(claims_list)} target claims for live validation testing.")
                st.markdown("---")
                
                for idx, item in enumerate(claims_list):
                    claim_text = item.get("claim")
                    query = item.get("search_query")
                    
                    st.markdown(f"### Claim #{idx+1}")
                    st.info(f"**Target Claim:** {claim_text}")
                    
                    with st.spinner(f"Querying live web index for: '{query}'..."):
                        web_data = query_live_web(query)
                    
                    with st.spinner("Evaluating structural synchronization with truth database..."):
                        analysis = evaluate_claim(claim_text, web_data, api_key)
                    
                    verdict = analysis.get("verdict", "FALSE").upper()
                    reasoning = analysis.get("reasoning", "No confirmation breakdown generated.")
                    
                    # Color coding logic for verdicts
                    if verdict == "VERIFIED":
                        st.markdown(f"**Verdict:** :green[{verdict}]")
                    elif verdict == "INACCURATE":
                        st.markdown(f"**Verdict:** :orange[{verdict}]")
                    else:
                        st.markdown(f"**Verdict:** :red[{verdict}]")
                        
                    st.write(f"**Analysis Insight:** {reasoning}")
                    st.markdown("---")
