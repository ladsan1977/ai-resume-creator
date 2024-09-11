import xml.dom.minidom
import re
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class XMLParser:
    @staticmethod
    def extract_xml_section(content, tag):
        try:
            root = ET.fromstring(content)
            section = root.find(tag)
            return ET.tostring(section, encoding='unicode') if section is not None else None
        except ET.ParseError as e:
            logger.error(f"Error extracting XML section: {e}")
            return None
        
    @staticmethod  
    def extract_and_format_xml(content, tag):
        pattern = f'<{tag}>(.*?)</{tag}>'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            xml_string = f'<{tag}>{match.group(1)}</{tag}>'
            dom = xml.dom.minidom.parseString(xml_string)
            return dom.toprettyxml(indent="  ")
        return None