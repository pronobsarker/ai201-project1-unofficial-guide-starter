import os
import re

data_folder = "data"

for filename in os.listdir(data_folder):
    if not filename.endswith(".txt"):
        continue
    
    filepath = os.path.join(data_folder, filename)
    
    with open(filepath, "r") as f:
        content = f.read()
    
    # Fix section labels onto their own lines
    content = re.sub(r'\s*REVIEW 1:', '\n\nREVIEW 1:', content)
    content = re.sub(r'\s*REVIEW 2:', '\n\nREVIEW 2:', content)
    content = re.sub(r'\s*REVIEW 3:', '\n\nREVIEW 3:', content)
    content = re.sub(r'\s*PROS:', '\n\nPROS:', content)
    content = re.sub(r'\s*CONS:', '\n\nCONS:', content)
    content = re.sub(r'\s*BEST FOR:', '\n\nBEST FOR:', content)
    content = re.sub(r'\s*SOURCE:', '\nSOURCE:', content)
    
    # Put each pro/con bullet on its own line
    # They appear after PROS: and CONS: as run-on sentences
    content = re.sub(r'(\w)\s+(Full |Lacks |No |Thin |Prone |High|Equipped|Exceptional|Historic|Modern|Fully|Complete|Communal|Strictly|Bedrooms|Features|Rooms|Highly|Private|In-room|Extreme|Unmatched|Outstanding|Rich|Vital|Crucial|Strong|Excellent|Beautiful|Massive|Two-story|Spectaular|Immediate|Unparalleled|Relocated)', r'\1\n- \2', content)
    
    # Clean up excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    
    with open(filepath, "w") as f:
        f.write(content)
    
    print(f"Cleaned: {filename}")

print("\nAll files cleaned!")