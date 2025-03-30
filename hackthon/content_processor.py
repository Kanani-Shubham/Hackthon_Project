from typing import Dict, Any

class ContentProcessor:
    @staticmethod
    def clean_content(content: Dict[str, Any]) -> Dict[str, Any]:
        if 'generated_content' not in content:
            return content

        sections = content['generated_content']['sections']
        cleaned_sections = []

        for section in sections:
            lines = section['content'].split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # Replace Rupee symbol with Rs.
                    line = line.replace('₹', 'Rs. ')
                    # Remove other special characters
                    line = (line.replace('*', '')
                              .replace('**', '')
                              .replace('<b>', '')
                              .replace('</b>', '')
                              .strip())
                    
                    if line:
                        indent = len(line) - len(line.lstrip())
                        if indent > 2:
                            line = "    " + line.lstrip()
                        cleaned_lines.append(line)

            cleaned_content = '\n'.join(cleaned_lines)
            cleaned_sections.append({
                'title': section['title'],
                'content': cleaned_content
            })

        content['generated_content']['sections'] = cleaned_sections
        return content