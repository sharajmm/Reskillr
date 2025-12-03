import streamlit as st
import PyPDF2
import io
import os
import re
import base64
from xhtml2pdf import pisa
import requests
import json

# Load environment variable for OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Page configuration
st.set_page_config(
    page_title="ReSkillr - AI Resume Critiquer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with GitHub dark theme
def local_css():
    st.markdown("""
    <style>
        /* GitHub theme colors */
        :root {
            --gh-bg-color: #0d1117;
            --gh-secondary-bg: #161b22;
            --gh-header-bg: #2d333b;
            --gh-text-color: #c9d1d9;
            --gh-link-color: #58a6ff;
            --gh-border-color: #30363d;
            --gh-button-bg: #238636;
            --gh-button-hover: #2ea043;
            --gh-sidebar-bg: #161b22;
            --gh-sidebar-text: #c9d1d9;
            --gh-code-bg: #161b22;
            --gh-violet: #a371f7;
        }
        
        /* Global styles */
        body {
            color: var(--gh-text-color);
            background-color: var(--gh-bg-color);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        }
        
        /* Override Streamlit's base theme */
        .stApp {
            background-color: var(--gh-bg-color);
        }
        
        /* Fix excessive top padding */
        .block-container {
            padding-top: 0 !important;
            max-width: 100%;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: var(--gh-sidebar-bg);
            border-right: 1px solid var(--gh-border-color);
        }
        
        [data-testid="stSidebar"] .block-container {
            padding-top: 0.5rem !important;
        }
        
        /* Button styling to make it more responsive */
        [data-testid="stSidebar"] .stButton > button {
            background-color: var(--gh-button-bg);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.75rem;
            width: 100%;
            font-weight: 600;
            transition: background-color 0.2s;
            cursor: pointer;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: var(--gh-button-hover);
        }
        
        /* Fix button clicking issues */
        [data-testid="stSidebar"] .stButton {
            width: 100%;
            z-index: 1;
            position: relative;
        }
        
        /* Standard button styling */
        .stButton > button {
            background-color: var(--gh-button-bg) !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            transition: background-color 0.2s !important;
            cursor: pointer !important;
        }
        
        .stButton > button:hover {
            background-color: var(--gh-button-hover) !important;
        }
        
        /* Input styling */
        [data-testid="stSidebar"] .stTextInput > div > div > input {
            background-color: #0d1117;
            border: 1px solid var(--gh-border-color);
            color: var(--gh-text-color);
            border-radius: 6px;
        }
        
        /* File uploader styling */
        [data-testid="stFileUploader"] {
            background-color: #0d1117;
            border: 1px dashed var(--gh-border-color);
            border-radius: 6px;
            padding: 10px;
        }
        
        /* Logo styling */
        .logo-container {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--gh-border-color);
        }
        
        .logo-text {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            font-size: 2rem;
            font-weight: 700;
            color: var(--gh-text-color);
            margin: 0;
            padding: 0;
        }
        
        .logo-ai {
            color: var(--gh-violet);
            font-weight: 600;
        }
        
        /* Content area - reduced padding */
        .main .block-container {
            padding-top: 0 !important;
            max-width: 60rem;
            margin: 0 auto;
        }
        
        /* Feature box container */
        .feature-box {
            background-color: var(--gh-secondary-bg);
            border: 1px solid var(--gh-border-color);
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
        }
        
        /* File status - more compact */
        .file-status {
            font-size: 12px;
            color: #8b949e;
            margin-top: 8px;
            background-color: var(--gh-secondary-bg);
            border: 1px solid var(--gh-border-color);
            border-radius: 6px;
            padding: 8px;
        }
        
        /* API key warning */
        .api-warning {
            background-color: rgba(248, 81, 73, 0.1);
            color: #f85149;
            border: 1px solid #f85149;
            border-radius: 6px;
            padding: 12px;
            margin-top: 12px;
            font-size: 14px;
        }
        
        /* Results header and title */
        .results-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--gh-border-color);
        }
        
        .results-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            margin-right: 12px;
            background-color: var(--gh-violet);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
        }
        
        .results-title {
            font-size: 18px;
            font-weight: 600;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: var(--gh-bg-color);
        }

        .stTabs [data-baseweb="tab"] {
            background-color: var(--gh-secondary-bg);
            border: 1px solid var(--gh-border-color);
            border-radius: 6px 6px 0px 0px;
            color: var(--gh-text-color);
            padding: 10px 16px;
        }

        .stTabs [aria-selected="true"] {
            background-color: var(--gh-header-bg);
            border-bottom: 2px solid var(--gh-link-color);
            color: var(--gh-text-color);
            font-weight: 600;
        }
        
        /* Contact links */
        .contact-link {
            display: flex;
            align-items: center;
            padding: 8px;
            margin-bottom: 8px;
            background-color: var(--gh-secondary-bg);
            border: 1px solid var(--gh-border-color);
            color: var(--gh-text-color);
            text-decoration: none;
            border-radius: 6px;
            transition: all 0.2s;
            gap: 8px;
        }
        
        .contact-link:hover {
            background-color: var(--gh-header-bg);
            border-color: var(--gh-link-color);
            color: var(--gh-link-color);
        }
        
        /* Contact info (non-link) */
        .contact-info {
            display: flex;
            align-items: center;
            padding: 8px;
            margin-bottom: 8px;
            background-color: var(--gh-secondary-bg);
            border: 1px solid var(--gh-border-color);
            color: var(--gh-text-color);
            border-radius: 6px;
            gap: 8px;
        }
        
        /* Contact section */
        .contact-section {
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--gh-border-color);
        }
        
        /* Footer styling */
        .custom-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: var(--gh-secondary-bg);
            color: var(--gh-text-color);
            text-align: center;
            padding: 10px;
            border-top: 1px solid var(--gh-border-color);
            font-size: 14px;
            z-index: 100;
        }
        
        /* Add padding at the bottom to prevent content from being hidden behind footer */
        .bottom-padding {
            padding-bottom: 60px;
        }
        
        /* Hide Streamlit elements */
        #MainMenu, footer, header {
            visibility: hidden !important;
        }
        
        /* Remove top spacing */
        .css-18e3th9 {
            padding-top: 0 !important;
        }
        
        .css-1d391kg {
            padding-top: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Check if OpenRouter API key is available
api_key_available = OPENROUTER_API_KEY is not None and OPENROUTER_API_KEY != ""

# Initialize session state for button clicks
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False

def on_analyze_click():
    st.session_state.analyze_clicked = True

# Create main sidebar with GitHub styling for resume upload
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <div class="logo-text">ReSkillr<span class="logo-ai"> AI</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Resume")
    uploaded_file = st.file_uploader("Upload PDF or TXT file", type=["pdf", "txt"], label_visibility="collapsed")
    
    st.markdown("### Target Position")
    job_role = st.text_input("Job role", label_visibility="collapsed", 
                           placeholder="e.g., Software Engineer")
    
    # Only enable analyze button when both fields are filled and API key is available
    # Using on_click to handle button clicks consistently
    analyze_button = st.button("Analyze Resume", 
                            use_container_width=True, 
                            disabled=(not uploaded_file or not job_role or not api_key_available),
                            on_click=on_analyze_click)
    
    if not job_role and uploaded_file:
        st.markdown('<p class="missing-field-warning">Please enter a target position</p>', unsafe_allow_html=True)
    
    if not uploaded_file and job_role:
        st.markdown('<p class="missing-field-warning">Please upload a resume</p>', unsafe_allow_html=True)
    
    if not api_key_available:
        st.markdown('<div class="api-warning">API missing.</div>', unsafe_allow_html=True)
    
    if uploaded_file:
        file_size = uploaded_file.size / 1024
        st.markdown(f"""
        <div class="file-status">
            <span>📄 {uploaded_file.name}</span><br>
            <span style="color:#8b949e">{file_size:.1f} KB · {uploaded_file.type}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Add Contact Developer section in sidebar
    st.markdown('<div class="contact-section">', unsafe_allow_html=True)
    st.markdown("### Contact Developer")
    
    # Email as text, not as a link
    st.markdown("""
    <div class="contact-info">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M1.75 2h12.5c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0 1 14.25 14H1.75A1.75 1.75 0 0 1 0 12.25v-8.5C0 2.784.784 2 1.75 2ZM1.5 12.251c0 .138.112.25.25.25h12.5a.25.25 0 0 0 .25-.25V5.809L8.38 9.397a.75.75 0 0 1-.76 0L1.5 5.809v6.442Zm13-8.181v-.32a.25.25 0 0 0-.25-.25H1.75a.25.25 0 0 0-.25.25v.32L8 7.88Z"></path>
        </svg>
        simplysharaj@gmail.com
    </div>
    """, unsafe_allow_html=True)

# Add custom footer with new text
st.markdown("""
<div class="custom-footer">
     &copy 2025 ReSkillr AI - Made by Sharaj MM.
</div>
<div class="bottom-padding"></div>
""", unsafe_allow_html=True)

# Function to create PDF from HTML using xhtml2pdf
def create_pdf_from_html(html_content):
    """Convert HTML content to PDF."""
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Convert HTML to PDF and write to buffer
    pisa.CreatePDF(html_content, dest=buffer)
    
    # Get the value from the buffer
    buffer.seek(0)
    return buffer.getvalue()

# Function to convert markdown to HTML
def markdown_to_html(markdown_text):
    """Convert markdown to HTML for PDF conversion."""
    html = """
    <html>
    <head>
        <style>
            body {
                font-family: "Helvetica", "Arial", sans-serif;
                line-height: 1.4;
                margin: 40px;
            }
            h1 {
                font-size: 24px;
                margin-bottom: 20px;
            }
            h2 {
                font-size: 20px;
                margin-top: 20px;
                margin-bottom: 10px;
                border-bottom: 1px solid #eaecef;
                padding-bottom: 5px;
            }
            h3 {
                font-size: 16px;
                margin-top: 15px;
                margin-bottom: 10px;
            }
            ul {
                margin-top: 8px;
                margin-bottom: 15px;
            }
            li {
                margin-bottom: 5px;
            }
            .contact-info {
                margin-bottom: 15px;
            }
            .section {
                margin-bottom: 20px;
            }
            .bold {
                font-weight: bold;
            }
        </style>
    </head>
    <body>
    """
    
    # Process lines
    lines = markdown_text.split('\n')
    in_list = False
    
    for line in lines:
        # Replace problematic characters
        line = line.replace('—', '-')  # Replace em-dash with regular dash
        
        # Process headings
        if line.startswith('# '):
            html += f"<h1>{line[2:]}</h1>\n"
        elif line.startswith('## '):
            html += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith('### '):
            html += f"<h3>{line[4:]}</h3>\n"
        
        # Process bullet points
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            if not in_list:
                html += "<ul>\n"
                in_list = True
            html += f"<li>{line.strip()[2:]}</li>\n"
        
        # Close list if next line is not a bullet point
        elif in_list:
            html += "</ul>\n"
            in_list = False
            
            if line.strip():  # If it's not an empty line
                # Process bold
                if '**' in line:
                    parts = re.split(r'\*\*(.*?)\*\*', line)
                    html_line = ""
                    for i, part in enumerate(parts):
                        if i % 2 == 1:  # Odd indices are inside **
                            html_line += f"<span class='bold'>{part}</span>"
                        else:
                            html_line += part
                    html += f"<p>{html_line}</p>\n"
                else:
                    html += f"<p>{line}</p>\n"
        
        # Regular text
        elif line.strip():
            # Process bold
            if '**' in line:
                parts = re.split(r'\*\*(.*?)\*\*', line)
                html_line = ""
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Odd indices are inside **
                        html_line += f"<span class='bold'>{part}</span>"
                    else:
                        html_line += part
                html += f"<p>{html_line}</p>\n"
            else:
                html += f"<p>{line}</p>\n"
        
        # Empty line - add some spacing
        else:
            html += "<br>\n"
    
    # Close any open list
    if in_list:
        html += "</ul>\n"
    
    html += """
    </body>
    </html>
    """
    
    return html

# Functions for resume processing
def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            text_content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text_content if text_content.strip() else "Sorry, No text content could be extracted from this file."
        except Exception as e:
            return f"Error extracting PDF content: {str(e)}"
    else:
        try:
            # Try utf-8 first
            return uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            try:
                # Reset file position and try with latin-1
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("latin-1", errors="replace")
                return content
            except Exception as e:
                return f"Error reading text file: {str(e)}"

# Function for OpenRouter API using the DeepSeek model
def query_openrouter_api(prompt):
    """Using OpenRouter API with mistralai/mistral-small-3.1-24b-instruct:free"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://reskillr.ai", # To identify your app
        }
        
        data = {
            "model": "mistralai/mistral-small-3.1-24b-instruct:free",
            "messages": [
                {"role": "system", "content": "You are an experienced HR and resume reviewer. Respond only in plain text and well structured and well aligned. No markdown."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "top_p": 1.0,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"Error: AI returned status code {response.status_code}. {response.text}"
    
    except Exception as e:
        return f"Sorry, I couldn't analyze your resume due to an error. Please try again later."

# Function to generate improved version of the resume
def query_openrouter_improved_version(resume_text, job_role):
    """Request an improved version of the resume from OpenRouter API."""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://reskillr.streamlit.app/", # To identify your app
        }
        
        prompt = f"""
You are an experienced HR professional and resume writer. You need to create an improved version of the following resume
for the role of {job_role} and check if current version of resume is suitable for the job. Focus on enhancing the wording, structure, and impact without inventing new information.
Make it more professional, impactful, and targeted for the specific role.

Resume:
{resume_text}

Provide only the improved resume content without any explanations or comments. 
Format it professionally with clear sections using Markdown formatting.
Use # for main name, ## for section headers, ### for job titles, and * for bullet points.
Make sure to include proper spacing between sections for readability.
Avoid using special characters like em-dashes, use regular hyphens instead.
Use only ASCII characters to ensure compatibility.
"""
        
        data = {
            "model": "mistralai/mistral-small-3.1-24b-instruct:free",
            "messages": [
                {"role": "system", "content": "You are an experienced resume writer. Respond with the improved resume using markdown formatting with ASCII characters only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "top_p": 1.0,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"Error: AI returned status code {response.status_code}. {response.text}"
    
    except Exception as e:
        return f"Sorry, I couldn't generate an improved version of your resume due to an error. Please try again later."

# Clean AI response
def clean_response(text):
    if text is None:
        return "No response received from the AI. Please try again later."
        
    try:
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'`(.*?)`', r'\1', text)
        text = re.sub(r'\n\s*[-*+]\s*', '\n- ', text)
        text = re.sub(r'#+ ', '', text)
        return text.strip()
    except Exception as e:
        return f"Error formatting response: {str(e)}"

# Generate mock analysis for testing when API is not available
def generate_mock_analysis(job_role):
    return f"""
1. Overall Content Quality:
The resume has a clean structure with clear sections for professional experience, education, and skills. The content is generally well-organized but could benefit from more quantifiable achievements.

2. Key Strengths and Skills:
- Good education credentials relevant to the {job_role} position
- Technical skills are clearly listed and organized
- Career progression is evident from the work experience section
- Includes relevant certifications and training

3. Weak Areas or Missing Sections:
- Lacks quantifiable achievements and metrics to demonstrate impact
- Professional summary/objective statement could be more targeted
- Missing a dedicated projects section to showcase relevant work
- Skills section could be better categorized by proficiency level
- Limited demonstration of soft skills relevant to the position

4. Suggestions for {job_role} Position:
- Align your technical skills section more closely with the job requirements for {job_role}
- Add specific metrics and achievements that demonstrate your expertise
- Include relevant projects that showcase your abilities in this field
- Highlight collaborative experiences and team contributions
- Emphasize any domain-specific knowledge relevant to this role

5. Formatting and Professionalism Tips:
- Consider a more modern template with better use of white space
- Ensure consistent formatting of dates, job titles, and headings
- Use bullet points more effectively to highlight key achievements
- Consider adding a LinkedIn profile or portfolio link
- Keep the resume to 1-2 pages maximum

6. Overall Impression:
Your resume shows you have relevant experience for a {job_role} position, but it could better highlight your specific achievements and align more closely with the industry standards for this role. With some targeted improvements to showcase measurable impacts and specific technical skills, your resume would be significantly stronger for this position.
"""

# Generate mock improved resume
def generate_mock_improved_resume(job_role):
    return f"""
# JOHN DOE
Seattle, WA | (555) 123-4567 | johndoe@email.com | linkedin.com/in/johndoe | github.com/johndoe

## PROFESSIONAL SUMMARY
Results-driven {job_role} with 5+ years of experience developing scalable applications and optimizing system performance. Skilled in translating business requirements into technical solutions with a focus on code quality and user experience. Passionate about solving complex problems and driving innovation in collaborative environments.

## SKILLS
**Technical:** Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, CI/CD, Microservices, REST APIs
**Professional:** Agile Methodologies, Cross-functional Collaboration, Technical Leadership, Problem Solving

## PROFESSIONAL EXPERIENCE

### SENIOR {job_role.upper()} | Tech Innovations Inc. | Seattle, WA | 2020-Present
* Led development of a microservices-based application that increased system throughput by 45% and reduced latency by 30%
* Orchestrated migration of legacy monolith to cloud-native architecture, resulting in 60% reduction in operational costs
* Mentored 5 junior developers, implementing code review practices that reduced production bugs by 25%
* Designed and implemented CI/CD pipeline that decreased deployment time from days to hours

### {job_role.upper()} | Digital Solutions LLC | Portland, OR | 2018-2020
* Developed RESTful APIs consumed by mobile and web applications with 100,000+ daily active users
* Implemented performance optimizations that improved application response time by 40%
* Collaborated with UX designers to implement responsive interfaces, increasing mobile conversion by 22%
* Created comprehensive test suite that achieved 95% code coverage and reduced regression issues

### JUNIOR {job_role.upper()} | StartupTech | San Francisco, CA | 2016-2018
* Contributed to frontend and backend development for an e-commerce platform with $2M annual revenue
* Built data visualization dashboard that provided real-time insights for executive decision-making
* Participated in daily scrum meetings and bi-weekly sprint planning sessions
* Resolved 150+ bugs and implemented 30+ feature requests in an Agile environment

## EDUCATION
**Bachelor of Science in Computer Science**, University of Washington, 2016
* GPA: 3.8/4.0, Dean's List all semesters
* Senior Project: AI-powered recommendation engine with 92% accuracy

## PROJECTS
**Intelligent Task Manager** - Developed open-source productivity application with 2,000+ active users
**Data Visualization Library** - Created JavaScript library used in 15+ commercial applications
"""

# Main content flow - PURE STREAMLIT COMPONENTS
if not uploaded_file or not job_role:
    # Welcome screen - using only pure Streamlit components
    st.title("ReSkillr AI")
    st.write("Upload your resume for AI-powered feedback to enhance your job application success")
    
    # Getting Started section
    st.subheader("Getting Started")
    st.write("1. Upload your resume (PDF or TXT format) in the sidebar")
    st.write("2. Enter your target job position to receive tailored feedback")
    st.write("3. Click **Analyze Resume** to generate feedback")
    
    # What ReSkillr AI analyzes
    st.subheader("What ReSkillr AI analyzes:")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown("##### ✓  Content Quality")
            st.caption("Evaluates overall resume structure, clarity and effectiveness")
        
        with st.container():
            st.markdown("##### ✓  Detailed Feedback")
            st.caption("Provides specific insights on strengths, weaknesses and areas for improvement")
    
    with col2:
        with st.container():
            st.markdown("##### ✓  Improvement Areas")
            st.caption("Highlights missing sections and opportunities for enhancement")
        
        with st.container():
            st.markdown("##### ✓  Job-specific Tips")
            st.caption("Provides targeted suggestions for your desired position")
elif st.session_state.analyze_clicked:
    # Both resume and job role are provided and button was clicked
    try:
        resume_text = extract_text(uploaded_file)
        
        # Show a clean results panel
        with st.spinner("I'm analyzing your resume please give me couple of seconds ..."):
            # No intermediate analysis display - just show a simple spinner
            
            analysis_prompt = f"""
You are an expert HR resume reviewer. Carefully read the following resume and provide an in-depth, detailed critique in plain text with no formatting:

1. Overall content quality
2. Key strengths and skills
3. Weak areas or missing sections
4. Suggestions to improve for the role of '{job_role}' if applicable
5. Formatting or professionalism tips
6. Overall impression and improvement ideas

Resume:
{resume_text}
"""
            # Use OpenRouter API for analysis or fall back to mock data
            if api_key_available:
                raw_result = query_openrouter_api(analysis_prompt)
                # Also get improved version
                improved_version = query_openrouter_improved_version(resume_text, job_role)
            else:
                raw_result = generate_mock_analysis(job_role)
                improved_version = generate_mock_improved_resume(job_role)
            
            final_result = clean_response(raw_result)
        
        # Display results header
        st.markdown(f"""
        <div class="results-header">
            <div class="results-avatar">R</div>
            <div class="results-title">ReSkillr AI</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.title(f"Resume Analysis for {job_role} Position")
        
        # Create tabs for analysis and improved version
        tab1, tab2 = st.tabs(["Resume Analysis", "Improved Version"])
        
        # Analysis tab content
        with tab1:
            # Split the text by sections and display them with pure Streamlit components
            sections = re.split(r'^\d+\.\s+', final_result, flags=re.MULTILINE)[1:]
            
            if len(sections) < 3:  # If splitting didn't work well, show the whole text
                st.write(final_result)
            else:
                for i, section_content in enumerate(sections, start=1):
                    if not section_content.strip():
                        continue
                        
                    # Extract title
                    title_match = re.match(r'(.*?):(.*)', section_content, re.DOTALL) 
                    if title_match:
                        title = title_match.group(1).strip()
                        content = title_match.group(2).strip()
                    else:
                        title_match = re.match(r'(.*?)\n(.*)', section_content, re.DOTALL)
                        if title_match:
                            title = title_match.group(1).strip()
                            content = title_match.group(2).strip() 
                        else:
                            title = f"Section {i}"
                            content = section_content.strip()
                    
                    # Create styled section for each part of the analysis
                    with st.container():
                        st.markdown(f"### {i}. {title}")
                        
                        # Split content by bullet points
                        if '-' in content:
                            lines = content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue
                                if line.startswith('-'):
                                    st.markdown(f"• {line[1:].strip()}")
                                else:
                                    st.write(line)
                        else:
                            st.write(content)
        
        # Improved version tab content
        with tab2:
            st.markdown("<h3>Improved Resume Version</h3>", unsafe_allow_html=True)
            
            # Store the improved version in session_state so it persists
            if 'improved_resume' not in st.session_state:
                # Sanitize text by replacing problematic characters
                sanitized_version = improved_version.replace('\u2014', '-') # Replace em dash with hyphen
                sanitized_version = ''.join(c if ord(c) < 128 else '-' for c in sanitized_version) # Replace non-ASCII
                st.session_state.improved_resume = sanitized_version
            
            # Use code block with syntax highlighting for improved resume
            st.code(st.session_state.improved_resume, language="markdown")
            
            try:
                # Convert markdown to HTML
                html_content = markdown_to_html(st.session_state.improved_resume)
                
                # Create PDF from HTML content
                pdf_data = create_pdf_from_html(html_content)
                
                # Download button that won't refresh the page
                col1, col2 = st.columns([1, 3])
                with col1:
                    # Generate a filename based on job role
                    file_name = f"improved_resume_{job_role.lower().replace(' ', '_')}.pdf"
                    
                    # Create a download button that works without a page refresh
                    download_button_str = f"""
                    <a href="data:application/pdf;base64,{base64.b64encode(pdf_data).decode()}" 
                       download="{file_name}" 
                       style="display: inline-block; 
                              padding: 0.5rem 1rem; 
                              background-color: #238636; 
                              color: white; 
                              text-decoration: none; 
                              font-weight: 600; 
                              border-radius: 6px; 
                              text-align: center; 
                              cursor: pointer; 
                              margin-top: 1rem;">
                        📥 Download Unformatted PDF
                    </a>
                    """
                    st.markdown(download_button_str, unsafe_allow_html=True)
            
            except Exception as e:
                st.warning(f"PDF generation encountered an issue: {str(e)}")
                # Fallback to text download
                st.download_button(
                    label="📥 Download as Text File",
                    data=st.session_state.improved_resume,
                    file_name=f"improved_resume_{job_role.lower().replace(' ', '_')}.txt",
                    mime="text/plain",
                    key="download_improved_txt"
                )
            
    except Exception as e:
        st.error(f"Error processing your resume: {str(e)}")
else:
    # Files are uploaded but button wasn't clicked yet
    st.info("Please click 'Analyze Resume' again to start the analysis.")
