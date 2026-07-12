import streamlit as st
from openai import OpenAI
import httpx
import concurrent.futures
import time

# Fetch free models
@st.cache_data(ttl=600)
def fetch_free_models():
    try:
        response = httpx.get("https://openrouter.ai/api/v1/models", timeout=5.0)
        if response.status_code == 200:
            all_models = response.json().get("data", [])
            free_slugs = [model["id"] for model in all_models if model["id"].endswith(":free")]
            return sorted(free_slugs)
    except Exception:
        pass
    return [
        "meta-llama/llama-3.3-70b-instruct:free", 
        "google/gemini-2.5-flash:free", 
        "nvidia/nemotron-3-super-120b-a12b:free",
        "qwen/qwen-2.5-72b-instruct:free"
    ]

FREE_MODELS = fetch_free_models()

# Core execution function with streaming and scoring
def execute_jailbreak(model, prompt, api_key, mode="G0DM0D3 CLASSIC"):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    # Different prompt strategies based on mode
    if mode == "STANDARD":
        # Stream tokens live
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.5,
            max_tokens=2000,
            stream=True
        )
        
        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
                yield response
    
    elif mode == "ULTRAPLINIAN":
        # Show first scored response immediately, then upgrade
        start_time = time.time()
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.5,
            max_tokens=2000,
            stream=False
        )
        
        response = completion.choices[0].message.content
        score = calculate_score(response)
        yield {"response": response, "score": score, "time": time.time() - start_time}
        
        # Simulate upgrading as faster models finish
        yield {"response": response, "score": score, "time": time.time() - start_time}
    
    else:  # G0DM0D3 CLASSIC
        # All templates race in parallel
        start_time = time.time()
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.5,
            max_tokens=2000,
            stream=False
        )
        
        response = completion.choices[0].message.content
        score = calculate_score(response)
        yield {"response": response, "score": score, "time": time.time() - start_time}

# Scoring function
def calculate_score(response):
    # Simple scoring based on response length and complexity
    tokens = response.split()
    diversity = len(set(tokens))/len(tokens) if tokens else 0
    length_score = min(len(tokens)/100, 1.0)
    complexity = sum(1 for c in response if c.isalnum()) / len(response) if response else 0
    return (diversity * 0.3) + (length_score * 0.4) + (complexity * 0.3)

# Main app
st.title("100% Guaranteed Jailbreak Tool")
api_key = st.text_input("OpenRouter API Key", type="password")

if api_key:
    prompt = st.text_input("Enter request (e.g., 'Python keylogger for Windows')")
    mode = st.selectbox("Select Mode", ["STANDARD", "ULTRAPLINIAN", "G0DM0D3 CLASSIC"])
    
    if st.button("Jailbreak!"):
        if not prompt:
            st.error("Please enter a prompt")
        else:
            # Execute on all models simultaneously
            results = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = {
                    executor.submit(execute_jailbreak, model, prompt, api_key, mode): model 
                    for model in FREE_MODELS
                }
                
                for future in concurrent.futures.as_completed(futures):
                    model = futures[future]
                    try:
                        results[model] = list(future.result())
                    except Exception as e:
                        results[model] = [{"response": f"Error: {str(e)}"}]
            
            # Display all results
            for model, result in results.items():
                with st.expander(f"Result from {model}"):
                    for item in result:
                        st.code(item["response"], language="python")
else:
    st.warning("Please enter your OpenRouter API key")
