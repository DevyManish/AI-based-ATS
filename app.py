import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import pandas as pd
import plotly.express as px

load_dotenv()  # Load all environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and
the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_files = st.file_uploader("Upload Your Resumes", type="pdf", accept_multiple_files=True, help="Please upload multiple PDFs")

submit = st.button("Submit")

if submit:
    if uploaded_files:
        results = []

        for uploaded_file in uploaded_files:
            text = input_pdf_text(uploaded_file)
            response = get_gemini_response(input_prompt.format(text=text, jd=jd))
            
            # Parse the response
            try:
                response_data = json.loads(response)
                jd_match = response_data.get("JD Match", "N/A")
                missing_keywords = response_data.get("MissingKeywords", [])
                profile_summary = response_data.get("Profile Summary", "N/A")

                # Append the results to the list
                results.append({
                    "Resume Name": uploaded_file.name,
                    "JD Match": jd_match.replace('%', '').strip(),  # Store as integer for sorting
                    "Missing Keywords": ', '.join(missing_keywords),
                    "Profile Summary": profile_summary
                })

            except json.JSONDecodeError:
                st.error("Error decoding JSON response for {}. Please check the response format.".format(uploaded_file.name))
            except Exception as e:
                st.error(f"An error occurred while processing {uploaded_file.name}: {str(e)}")

        # Create a DataFrame for the results
        df = pd.DataFrame(results)

        # Sort by JD Match (convert to int for sorting)
        df['JD Match'] = pd.to_numeric(df['JD Match'], errors='coerce')
        df = df.sort_values(by='JD Match', ascending=False)

        # Display the sorted table
        st.subheader("ATS Evaluation Results")
        st.table(df)

        # Create a bar chart for JD Match
        bar_chart_data = df[['Resume Name', 'JD Match']]
        bar_chart_fig = px.bar(bar_chart_data, x='Resume Name', y='JD Match', title='JD Match Percentage', labels={'JD Match': 'Match Percentage'})
        st.plotly_chart(bar_chart_fig)

    else:
        st.error("Please upload at least one resume.")
