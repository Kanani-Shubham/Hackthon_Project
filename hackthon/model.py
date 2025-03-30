from typing import Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class TenderGenerator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = "llama-3.1-8b-instant"

    def generate_tender_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            generated_sections = []
            
            sections = [
                ("Executive Summary", 2000),
                ("Project Overview and Objectives", 2500),
                ("Detailed Technical Specifications", 3000),
                ("Implementation Methodology", 2500),
                ("Quality Control and Standards", 2000),
                ("Risk Management Framework", 2000),
                ("Financial Terms and Conditions", 2000),
                ("Legal and Compliance Requirements", 2000),
                ("Performance Metrics and SLAs", 2000),
                ("Testing and Acceptance Criteria", 2000)
            ]

            for section_title, max_tokens in sections:
                prompt = f"""Generate a detailed {section_title} section for the following tender:
                Project: {data['tender_title']}
                Value: ₹{data['tender_amount']:,}
                Scope: {data['scope_of_work']}
                Requirements: {data['requirements']}
                
                Generate professional and comprehensive content focusing on {section_title}.
                Include specific details, metrics, and industry standards.
                Format the output with proper paragraphs and bullet points where appropriate."""

                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert tender document writer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=max_tokens,
                    top_p=1,
                    stream=False
                )
                
                content = completion.choices[0].message.content
                generated_sections.append({
                    'title': section_title,
                    'content': content
                })

            return {
                'generated_content': {
                    'sections': generated_sections,
                    'full_description': '\n\n'.join([
                        f"# {section['title']}\n{section['content']}"
                        for section in generated_sections
                    ])
                },
                'metadata': {
                    'generation_time': datetime.now().isoformat(),
                    'model': self.model,
                    'sections_generated': len(generated_sections)
                }
            }

        except Exception as e:
            print(f"Error in content generation: {str(e)}")
            raise

    def validate_tender_data(self, data: Dict[str, Any]) -> bool:
        """Validates the input tender data"""
        required_fields = [
            'tender_title', 'issuing_authority', 'tender_amount',
            'bid_start_date', 'bid_end_date', 'eligibility_criteria',
            'scope_of_work', 'requirements', 'contact_details'
        ]
        return all(field in data for field in required_fields)

# Usage example
if __name__ == "__main__":
    # Test data
    test_data = {
        "tender_id": "TND12345",
        "tender_title": "Construction of Municipal Building",
        "issuing_authority": "City Development Authority",
        "tender_amount": 5000000,
        "bid_start_date": "2024-03-28",
        "bid_end_date": "2024-04-28",
        "eligibility_criteria": "Minimum 5 years experience in similar projects",
        "scope_of_work": "Construction of 3-story municipal building",
        "requirements": "ISO 9001 certification required",
        "contact_details": "engineering.dept@city.gov",
        "mvp_details": "Detailed MVP specifications for the building",
        "milestone_deliverables": "Phase-wise deliverables for the project",
        "liquidated_damages": "Penalty for delays beyond agreed timelines",
        "boq_items": [
            {
                "item_name": "Cement",
                "quantity": 1000,
                "rate": 350
            }
        ]
    }

    # Generate tender document
    generator = TenderGenerator()
    if generator.validate_tender_data(test_data):
        result = generator.generate_tender_content(test_data)
        print(result)