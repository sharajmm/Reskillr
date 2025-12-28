# ReSkillr AI - Resume Analyzer

## Live at - https://reskillr.streamlit.app/

![ReSkillr AI](https://img.shields.io/badge/ReSkillr-AI-blueviolet)

## Overview

ReSkillr AI is a streamlit-based web application that uses AI to analyze and improve resumes. The tool provides personalized feedback and suggestions tailored to specific job roles, helping users enhance their job application success rate.

## Features

- **Resume Analysis**: Detailed critique of your resume's strengths and weaknesses
- **Job-Specific Feedback**: Tailored suggestions based on your target position
- **Improved Resume Version**: AI-generated enhanced version of your resume
- **PDF Export**: Download your improved resume as a professionally formatted PDF

## Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenRouter API key with access to the DeepSeek model

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sharajmaruthu/reskillr.git
cd reskillr
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set your OpenRouter API key as an environment variable:
```bash
export OPENROUTER_API_KEY=your_api_key_here
```

4. Run the application:
```bash
streamlit run main.py
```

## Usage

1. Upload your resume (PDF or TXT format)
2. Specify your target job position
3. Click "Analyze Resume" to generate feedback
4. View the analysis and improved version in the tabs
5. Download your enhanced resume as a PDF

## Technology Stack

- **Streamlit**: Frontend framework
- **OpenRouter API**: Used for AI analysis
- **PyPDF2**: PDF processing
- **xhtml2pdf**: PDF generation

## Project Structure

```
reskillr-ai/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .gitignore          # Git ignore file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact Developer

- **Email**: simplysharaj@gmail.com
- **LinkedIn**: [Sharaj MM](https://www.linkedin.com/in/sharajmm/)


## Acknowledgements

- Developed by Sharaj MM
