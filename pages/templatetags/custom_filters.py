from django import template
from bs4 import BeautifulSoup
import re

register = template.Library()

@register.filter(name='custom_split')
def custom_split(value):
    """
    Splits a string into a list using a specified delimiter.
    """
    result = []
    if "Text part:" in value and "Example code part:" in value:
        all_txt = value.split("Text part:")[1]
        result.append(all_txt.split("Example code part:")[0])
        code_part = all_txt.split("Example code part:")[1]

        # print("===================code=======>", code_part)
        code_part1 = "".join(re.findall(r'<[^>]+>', code_part))
        result.append(code_part1)

        code_part2 = BeautifulSoup(code_part, 'html.parser').get_text()
        result.append(code_part2)
        # print("===================code1=======>", code_part1)
        # print("===================code2=======>", code_part2)
    elif "Text part:" in value:
        result.append(value.split("Text part:")[1])
    elif "Example code part:" in value:
        value.split("Example code part:")[1]
    else:
        result.append(value)
    # split("Example code part:")
    # tmp = value.split("Text part:")[1]
    return result 
