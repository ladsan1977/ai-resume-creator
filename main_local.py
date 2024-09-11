from app import ClaudeAPIClient, XMLParser, PromptCache, ResumeGenerator
from app.utils import constants

def main():
    api_client = ClaudeAPIClient()
    xml_parser = XMLParser()
    prompt_cache = PromptCache()
    resume_generator = ResumeGenerator(prompt_cache)

    job_information = constants.JOB_POSTING
    result = resume_generator.generate_resume_package(job_information, api_client, xml_parser)

    # print("\nKeywords:")
    # print(result['keywords'])
    print("\nSummary:")
    print(result['summary'])
    print("\nResume:")
    print(result['resume'])
    print("\nCover Letter:")
    print(result['cover_letter'])

if __name__ == "__main__":
    main()