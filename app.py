import streamlit as st
import requests
from PyPDF2 import PdfReader
import base64
from docx import Document

API_KEY = st.secrets["API_KEY"]

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def analyze_documents(resume_text, job_description):
    custom_prompt = f"""
    Please analyze the following resume in the context of the job description provided. Strictly check every single line in job description and analyze my resume whether there is a match exactly. Strictly maintain high ATS standards and give scores only to the correct ones. Focus on hard skills which are missing and also soft skills which are missing. Provide the following details.:
    1. The match percentage of the resume to the job description. Display this.
    2. A list of missing keywords accurate ones.
    3. Final thoughts on the resume's overall match with the job description in 3 lines.
    4. Recommendations on how to add the missing keywords and improve the resume in 3-4 points with examples.
    Please display in the above order don't mention the numbers like 1. 2. etc and strictly follow ATS standards so that analysis will be accurate. Strictly follow the above templates omg. don't keep changing every time.
    Strictly follow the above things and template which has to be displayed and don't keep changing again and again. Don't fucking change the template from above.
    Title should be Resume analysis and maintain the same title for all. Also if someone uploads the same unchanged resume twice, keep in mind to give the same results. Display new ones only if they have changed their resume according to your suggestions or at least few changes.
    Job Description: {job_description}

    Resume: {resume_text}
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {"role": "user", "parts": [{"text": custom_prompt}]}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def rephrase_text(text):
    custom_prompt = f"""
    Please rephrase the following text according to ATS standards, including quantifiable measures and improvements where possible, also maintain precise and concise points which will pass ATS screening:
    The title should be Rephrased Text:, and then display the output.
    Original Text: {text}
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {"role": "user", "parts": [{"text": custom_prompt}]}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def display_resume(file):
    file_type = file.name.split('.')[-1].lower()
    if file_type == 'pdf':
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        st.text_area("Parsed Resume Content", text, height=400)
    elif file_type == 'docx':
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        st.text_area("Parsed Resume Content", text, height=400)
    else:
        st.error("Unsupported file type. Please upload a PDF or DOCX file.")

st.set_page_config(page_title="ATS Resume Evaluation System", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Resume Analyzer", "Magic Write", "ATS Templates"])

if page == "Resume Analyzer":
    st.title("📄🔍 ATS Resume Evaluation System")
    st.write("Welcome to the ATS Resume Evaluation System! Upload your resume and enter the job description to get a detailed evaluation of your resume's match with the job requirements.")

    job_description = st.text_area("Job Description:")
    resume = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

    if resume:
        st.write("Uploaded Resume:")
        display_resume(resume)

    if st.button("Percentage Match"):
        if job_description and resume:
            with st.spinner("Analyzing..."):
                resume.seek(0)  # Reset the file pointer to the start
                file_type = resume.name.split('.')[-1].lower()
                if file_type == 'pdf':
                    resume_text = extract_text_from_pdf(resume)
                elif file_type == 'docx':
                    resume_text = extract_text_from_docx(resume)
                analysis = analyze_documents(resume_text, job_description)
                
                if "candidates" in analysis:
                    for candidate in analysis["candidates"]:
                        if "content" in candidate and "parts" in candidate["content"]:
                            for part in candidate["content"]["parts"]:
                                response_text = part["text"]
                                
                                st.markdown(response_text)
                                
                                lines = response_text.split("\n")
                                for line in lines:
                                    if "match percentage" in line.lower():
                                        match_percentage = line.split(":")[-1].strip()
                                        match_percentage = ''.join(filter(str.isdigit, match_percentage))
                                        match_percentage = int(match_percentage)
                                        break

                                st.write(f"Your Resume Match Percentage: {match_percentage}%")
                                st.progress(match_percentage)

                st.success("Analysis Complete!")
        else:
            st.error("Please enter the job description and upload a resume.")

elif page == "Magic Write":
    st.title("🔮 Magic Write")
    st.write("Enter lines from your resume to rephrase them according to ATS standards with quantifiable measures.")

    text_to_rephrase = st.text_area("Text to Rephrase:")
    
    if st.button("Rephrase"):
        if text_to_rephrase:
            with st.spinner("Rephrasing..."):
                rephrase_response = rephrase_text(text_to_rephrase)
                
                # Extracting and displaying the rephrased text
                if "candidates" in rephrase_response:
                    for candidate in rephrase_response["candidates"]:
                        if "content" in candidate and "parts" in candidate["content"]:
                            for part in candidate["content"]["parts"]:
                                rephrased_text = part["text"]
                                st.write(rephrased_text)

                st.success("Rephrasing Complete!")
        else:
            st.error("Please enter the text you want to rephrase.")

elif page == "ATS Templates":
    st.title("📄📝 Free ATS Resume Templates")
    st.write("Download free ATS-friendly resume templates. Click on a template to download it.")

    templates = {
        "Sample 1": "https://docs.google.com/document/d/1NWFIz-EZ1ZztZSdXfrrcdffSzG-uermd/edit?usp=sharing&ouid=102272826109592952279&rtpof=true&sd=true",
        "Sample 2": "https://docs.google.com/document/d/1xO7hvK-RQSb0mjXRn24ri3AiDrXx6qt8/edit?usp=sharing&ouid=102272826109592952279&rtpof=true&sd=true",
        "Sample 3": "https://docs.google.com/document/d/1fAukvT0lWXns3VexbZjwXyCAZGw2YptO/edit?usp=sharing&ouid=102272826109592952279&rtpof=true&sd=true",
        "Sample 4": "https://docs.google.com/document/d/1htdoqTPDnG-T0OpTtj8wUOIfX9PfvqhS/edit?usp=sharing&ouid=102272826109592952279&rtpof=true&sd=true",
        "Sample 5": "https://docs.google.com/document/d/1uTINCs71c4lL1Gcb8DQlyFYVqzOPidoS/edit?usp=sharing&ouid=102272826109592952279&rtpof=true&sd=true",
        "Sample 6": "https://docs.google.com/document/d/1KO9OuhY7l6dn2c5xynpCOIgbx5LWsfb0/edit?usp=sharing&ouid=102272826109592952279&rtpof=true&sd=true"
    }

    cols = st.columns(3)
    for index, (template_name, template_link) in enumerate(templates.items()):
        col = cols[index % 3]
        col.markdown(f"""
            <div style="text-align:center">
                <iframe src="https://drive.google.com/file/d/{template_link.split('/')[-2]}/preview" width="200" height="250" allow="autoplay"></iframe>
                <br>
                <a href="{template_link}" target="_blank">{template_name}</a>
            </div>
        """, unsafe_allow_html=True)
