import utils
import os
from dotenv import load_dotenv 
from anthropic import Anthropic, APIStatusError, APIError
import xml.dom.minidom
import re
import logging
import xml.etree.ElementTree as ET

# Load environment variables from .env file
load_dotenv()

# Initialize the Anthropic client
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
client = Anthropic(api_key=anthropic_api_key)

# System prompt
BASE_SYSTEM_PROMPT = "You are a Counsel to advise a potential employee in the creation of a Canadian resume"
# Models that maintain context memory across interactions
MAINMODEL = "claude-3-5-sonnet-20240620"

class ResumeGenerator:
    def __init__(self):
        self.client = client
        self.base_system_prompt = BASE_SYSTEM_PROMPT
        self.model = MAINMODEL

    def generate_key_words(self, job_information):
        try:
            message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0,
            system=self.base_system_prompt,
            messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"You are tasked with analyzing a job posting and extracting relevant keywords. Follow these instructions carefully:\n\n1. Read the following information to access the job posting:\n<job_information>\n{job_information}\n</job_information>\n\n2. Read the entire job posting carefully, paying attention to all sections including job title, description, responsibilities, and requirements.\n\n3. As you read, identify and extract important keywords related to the following categories:\n   a. Job title and level\n   b. Required skills and competencies\n   c. Desired experience\n   d. Educational requirements\n   e. Industry-specific terminology\n   f. Company values or culture\n\n4. When extracting keywords, follow these guidelines:\n   - Focus on specific, descriptive words and phrases\n   - Include technical skills, soft skills, and qualifications\n   - Pay attention to repeated words or phrases\n   - Consider both explicit requirements and implied preferences\n\n5. After analyzing the job posting, present the extracted keywords in the following format:\n\n<keywords>\n<job_title_and_level>\n[List keywords related to the job title and level]\n</job_title_and_level>\n\n<required_skills>\n[List keywords related to required skills and competencies]\n</required_skills>\n\n<desired_experience>\n[List keywords related to desired experience]\n</desired_experience>\n\n<education>\n[List keywords related to educational requirements]\n</education>\n\n<industry_terms>\n[List industry-specific terminology]\n</industry_terms>\n\n<company_culture>\n[List keywords related to company values or culture]\n</company_culture>\n</keywords>\n\n6. After listing the keywords, provide a brief summary of the job posting in 2-3 sentences, highlighting the most important aspects of the position. Present this summary in the following format:\n\n<summary>\n[Your 2-3 sentence summary of the job posting]\n</summary>\n\nRemember to focus on extracting the most relevant and important keywords that accurately represent the job posting. Your analysis will help potential applicants quickly understand the key requirements and expectations of the position."
                            }
                        ]
                    },
                ]
            )
            
            # Assuming the message.content contains the XML-like structure
            # Wrap the content in a root element to ensure valid XML
            xml_content = f"<root>{message.content}</root>"
            
            # Parse the XML to ensure it's valid
            root = ET.fromstring(xml_content)
            
            # Return the XML as a string
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            logging.error(f"Error in generate_key_words: {e}")
            return None
   
def main():
    response_key_words = ResumeGenerator.generate_key_words(utils.job_posting)
    print(response_key_words)
main()


# para controlar los reintentos de la api

import time
import logging
from anthropic import APIStatusError, APIError

def call_claude_api_with_retry(client, job_information, retries=5, backoff_factor=1.5):
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                temperature=0,
                system="You are a Counsel to advise a potential employee in the creation of a Canadian resume",
                messages=[
                    {
                        "role": "user",
                        "content": job_information,
                    },
                ]
            )
            return response
        except (APIStatusError, APIError) as e:
            if "overloaded_error" in str(e):
                wait_time = backoff_factor ** attempt
                logging.warning(f"API is overloaded, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e
    logging.error("Exceeded maximum retries due to API overload.")
    return None

# anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
# if not anthropic_api_key:
#     raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
# client = Anthropic(api_key=anthropic_api_key)
# version # 2

# class ResumeGenerator:
#     def __init__(self):
#         self.client = client
#         self.base_system_prompt = BASE_SYSTEM_PROMPT
#         self.model = MAINMODEL

#     def generate_resume_package(self, job_info):
#         prompt = f"""
#         1. Analyze the following job information and extract relevant keywords:
#         {job_info}

#         2. Based on the extracted keywords, generate a resume and cover letter using the following guidelines:
#         {self.resume_guidelines}
#         {self.cover_letter_guidelines}

#         3. Present the results in the following format:
#         <keywords>
#         [Extracted keywords here]
#         </keywords>

#         <resume>
#         [Generated resume here]
#         </resume>

#         <coverLetter>
#         [Generated cover letter here]
#         </coverLetter>
#         """

#         response = self.api_client.generate_text(prompt, self.model, max_tokens=2048, temperature=0)
        
#         # Parse the response to extract keywords, resume, and cover letter
#         # Return the parsed results

#     def generate_key_words(self, job_information):
#         # Analyzes a job posting and extracts relevant keywords.
#         try:
#             message = self.client.messages.create(
#             model=self.model,
#             max_tokens=1024,
#             temperature=0,
#             system=self.base_system_prompt,
#             messages=[
#                     {
#                         "role": "user",
#                         "content": [
#                             {
#                                 "type": "text",
#                                 "text": f"You are tasked with analyzing a job posting and extracting relevant keywords. Follow these instructions carefully:\n\n1. Read the following information to access the job posting:\n<job_information>\n{job_information}\n</job_information>\n\n2. Read the entire job posting carefully, paying attention to all sections including job title, description, responsibilities, and requirements.\n\n3. As you read, identify and extract important keywords related to the following categories:\n   a. Job title and level\n   b. Required skills and competencies\n   c. Desired experience\n   d. Educational requirements\n   e. Industry-specific terminology\n   f. Company values or culture\n\n4. When extracting keywords, follow these guidelines:\n   - Focus on specific, descriptive words and phrases\n   - Include technical skills, soft skills, and qualifications\n   - Pay attention to repeated words or phrases\n   - Consider both explicit requirements and implied preferences\n\n5. After analyzing the job posting, present the extracted keywords in the following format:\n\n<keywords>\n<job_title_and_level>\n[List keywords related to the job title and level]\n</job_title_and_level>\n\n<required_skills>\n[List keywords related to required skills and competencies]\n</required_skills>\n\n<desired_experience>\n[List keywords related to desired experience]\n</desired_experience>\n\n<education>\n[List keywords related to educational requirements]\n</education>\n\n<industry_terms>\n[List industry-specific terminology]\n</industry_terms>\n\n<company_culture>\n[List keywords related to company values or culture]\n</company_culture>\n</keywords>\n\n6. After listing the keywords, provide a brief summary of the job posting in 2-3 sentences, highlighting the most important aspects of the position. Present this summary in the following format:\n\n<summary>\n[Your 2-3 sentence summary of the job posting]\n</summary>\n\nRemember to focus on extracting the most relevant and important keywords that accurately represent the job posting. Your analysis will help potential applicants quickly understand the key requirements and expectations of the position."
#                             }
#                         ]
#                     },
#                 ]
#             )
            
#             # Assuming the message.content contains the XML-like structure
#             # Wrap the content in a root element to ensure valid XML
#             xml_content = f"<root>{message.content[0].text}</root>"
            
#             # Parse the XML to ensure it's valid
#             root = ET.fromstring(xml_content)
            
#             # Return the XML as a string
#             return ET.tostring(root, encoding='unicode')
#         except Exception as e:
#             logging.error(f"Error in generate_key_words: {e}")
#             return None
        
#     def generate_resume_and_cover_letter(self, key_words_xml):
#         try:
#             root = ET.fromstring(key_words_xml)
            
#             # Extract information from the XML
#             keywords = {}
#             for category in root.find('keywords'):
#                 keywords[category.tag] = category.text.strip()
            
#             summary = root.find('summary').text.strip()
            
#             # Use the extracted information to create the prompt
#             prompt = f"""
#             1. Based on the following keywords:
#             Job Title and Level: {keywords.get('job_title_and_level', '')}
#             Required Skills: {keywords.get('required_skills', '')}
#             Desired Experience: {keywords.get('desired_experience', '')}
#             Education: {keywords.get('education', '')}
#             Industry Terms: {keywords.get('industry_terms', '')}
#             Company Culture: {keywords.get('company_culture', '')}
#             Summary: {summary}

#             2. Read the following guidelines to build a properly resume: 

#             <guidelines>
#             {utils.guidelines_info}
#             </guidelines>

#             3. Read the following profile of the candidate for the position:

#             <profile>
#             {utils.profile_pdf}
#             </profile>

#             4. After analyzing the Canadian resume guidelines, the profile, and the job posting conclusions that you made, present the resume in the following XML format: 

#             <resume>
#             <personalInfo></personalInfo>,
#             <professionalSummary></professionalSummary>
#             <workExperience></workExperience>
#             <education></education>
#             <skills></skills>
#             <certifications></certifications>
#             </resume>


#             5. Create a cover letter taking into account the following tips and structure:

#             <cover>
#             {utils.cover_letter}
#             </cover>

#             6. Present your results in the following XML format:

#             <coverLetter>
#             <header></header>
#             <content></content>
#             <salutationAndSignature></salutationAndSignature>
#             </coverLetter>

#             Remember to focus on the guidelines to elaborate a powerful resume. To do so, take into account the guidelines provided and how the profile of the candidate fits with the requirements and the relevant keywords. 
#             Do not include any skills or experiences that are not explicitly mentioned in the candidate's profile, even if they are listed as requirements in the job proposal. However, if a skill or experience is mentioned in both the candidate's profile and the job proposal, you may enhance and expand on these points in the skills section or work experience descriptions to better align with the job requirements. Focus on showcasing how these relevant skills and experiences make the candidate an ideal fit for the position, but ensure that all enhancements are grounded in the candidate's actual experience.
#             Please don't show any summary.  You only need to display the XML formats clearly separated.                        
#             """
            
#             # Make the API call with the constructed prompt
#             message = self.client.messages.create(
#                 model=self.model,
#                 max_tokens=1524,
#                 temperature=0,
#                 system=self.base_system_prompt,
#                 messages=[
#                         {
#                             "role": "user",
#                             "content": [
#                                 {
#                                     "type": "text",
#                                     "text": f"Your task is to analyze the CV of an applicant for a job posting and write a Canadian resume with the cover letter according with the relevant keywords and with the analysis of the job posting. {prompt}"
#                                 }
#                             ]
#                         },
#                     ]
#             )
            
#             # Process and return the response
#             return message.content[0].text
#         except ET.ParseError as e:
#             logging.error(f"Error parsing XML in generate_resume_and_cover_letter: {e}")
#             return None
#         except Exception as e:
#             logging.error(f"Error in generate_resume_and_cover_letter: {e}")
#             return None

# def main():
#     # Instanciar la clase ResumeGenerator
#     resume_generator = ResumeGenerator()

#     # Usar el método generate_key_words de la instancia creada
#     job_information = utils.job_posting
#     response_key_words = resume_generator.generate_key_words(job_information)
    
#     # Imprimir la respuesta obtenida
#     print(response_key_words)

#     response_resume_cover = resume_generator.generate_resume_and_cover_letter(response_key_words)
#     print(response_resume_cover)

#     # resume_xml = extract_and_format_xml(response_resume_cover, 'resume')
#     # cover_letter_xml = extract_and_format_xml(response_resume_cover, 'coverLetter')

#     # print("Formatted Resume XML:")
#     # print(resume_xml)

#     # print("\nFormatted Cover Letter XML:")
#     # print(cover_letter_xml)
