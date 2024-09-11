from app.utils import constants

class ResumeGenerator:
    def __init__(self, prompt_cache):
        self.base_system_prompt = constants.BASE_SYSTEM_PROMPT
        self.prompt_cache = prompt_cache

    def build_resume_prompt(self, job_information, profile_pdf):

    # PARA LOCAL QUITAR COMENTARIO A LAS SIGUIENTES 4 LINEAS
    # def build_resume_prompt(self, job_information):
        
        # profile_pdf = f"""<profile>
        # {constants.PROFILE_PDF}
        # </profile>"""

        cached_guidelines = self.prompt_cache.get_cached_prompt('guidelines')
        cached_guidelines_cover = self.prompt_cache.get_cached_prompt('guidelines_cover')

        if not cached_guidelines:
            cached_guidelines = f"""
            <guidelines>
            {constants.GUIDELINES_INFO}
            </guidelines>
            """
            self.prompt_cache.add_to_cache('guidelines', cached_guidelines)

        if not cached_guidelines_cover:
            cached_guidelines_cover = f"""
            <cover>
            {constants.COVER_LETTER}
            </cover>
            """
            self.prompt_cache.add_to_cache('guidelines_cover', cached_guidelines_cover)
        
        return f"""You are tasked with analyzing a job posting, extracting relevant keywords, and then creating a tailored resume and cover letter. Follow these steps carefully:

        1. Analyze the following job posting:
        <job_information>
        {job_information}
        </job_information>

        2. Extract relevant keywords from the job posting. Don't present them.  Just keep those in the context taking in consideration:
        job title and level, required skills, desired experience, education and company culture.
        
        3. Provide a brief summary of the job posting in 2-3 sentences:
        <summary>[Your 2-3 sentence summary of the job posting]</summary>

        4. Now, using the extracted keywords and summary, create a resume based on the following candidate profile and guidelines:

        <profile>
        {profile_pdf}
        </profile>

        <guidelines>
        {cached_guidelines}
        </guidelines>

        Present the resume in the following XML format:
        <resume>
        <personalInfo></personalInfo>
        <professionalSummary></professionalSummary>
        <workExperience></workExperience>
        <education></education>
        <skills></skills>
        <certifications></certifications>
        </resume>

        5. Create a cover letter using the following guidelines:
        <cover>
        {cached_guidelines_cover}
        </cover>

        Present the cover letter in the following XML format:
        <coverLetter>
        <header></header>
        <content></content>
        <salutationAndSignature></salutationAndSignature>
        </coverLetter>

        Important notes:
        - Focus on the guidelines to create a powerful resume.
        - Ensure that the resume and cover letter align with the candidate's profile and the job requirements.
        - Do not include skills or experiences not explicitly mentioned in the candidate's profile.
        - Do not include certifications not explicitly mentioned in the candidate's profile.
        - You may enhance and expand on points mentioned in both the candidate's profile and the job posting.
        - Showcase how the candidate's relevant skills and experiences make them an ideal fit for the position.
        - Ensure all enhancements are grounded in the candidate's actual experience.
        - Present only the XML formats for summary, resume, and cover letter, clearly separated.
        """

    # PARA LOCAL
    # def generate_resume_package(self, job_information, api_client, xml_parser):
    # PARA API
    def generate_resume_package(self, job_information, profile_pdf, api_client, xml_parser):
        
        # PARA API
        prompt = self.build_resume_prompt(job_information, profile_pdf)

        # PARA LOCAL
        # prompt = self.build_resume_prompt(job_information)

        response = api_client.generate_text(self.base_system_prompt, prompt, max_tokens=2048, temperature=0)
        return self.parse_response(response, xml_parser)

    def parse_response(self, response, xml_parser):
        # keywords = xml_parser.extract_and_format_xml(response, 'keywords')
        summary = xml_parser.extract_and_format_xml(response, 'summary')
        resume = xml_parser.extract_and_format_xml(response, 'resume')
        cover_letter = xml_parser.extract_and_format_xml(response, 'coverLetter')

        return {
            # 'keywords': keywords,
            'summary': summary,
            'resume': resume,
            'cover_letter': cover_letter
        }
