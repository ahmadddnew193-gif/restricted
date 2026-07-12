import streamlit as st
from malicious_generator import generate_malicious_code

st.title("Malicious Code Generator")

# API Key input
api_key = st.text_input("Enter OpenRouter API Key", type="password")

if api_key:
    # Update environment variable
    import os
    os.environ["OPENROUTER_API_KEY"] = api_key
    
    # Rest of the app logic
    script_type = st.selectbox("Select Script Type", 
                              ["Keylogger", "Backdoor", "Rootkit"])
    prompt = st.text_input("Enter details (e.g., 'Python keylogger for Windows')")
    
    if st.button("Generate"):
        result = generate_malicious_code(f"Create a {script_type.lower()} script: {prompt}")
        st.code(result, language="python")
else:
    st.warning("Please enter your OpenRouter API key")
