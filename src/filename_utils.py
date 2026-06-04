import os
import re

# for highpass filtering (cleaning)
def get_cleaned_filename(filename):
    base, ext = os.path.splitext(filename)
    return f"{base}-cleaned{ext}"

# for npy
def get_npy_filename(cleaned_filename):
    base, _ = os.path.splitext(cleaned_filename)
    return f"{base}.npy"


# for csv (edit pa base sa format)
def extract_metadata(filename):
    base = os.path.splitext(filename)[0]
    
    match = re.match(r"egg(\d+)-(\d)-(cracked|uncracked)-(\d)-p(\d)-sv(\d)", base) # egg(ikapila siya)-fold-targetstatus-p(pointnum)-s

    if not match:
        raise ValueError("Filename format invalid")
    
    fold = int(match.group(2))
    target_status = match.group(3)
    target = int(match.group(4))
    point = int(match.group(5))
    sv = int(match.group(6))
    
    return {
        "fold": fold,
        "target_status": target_status,
        "target": target,
        "point": point,
        "sv": sv,
    }

# filename = "test1-p1-cracked-1.wav"

# cleaned = get_cleaned_filename(filename)
# npy_file = get_npy_filename(cleaned)
# metadata = extract_metadata(filename)

# print(cleaned)
# print(npy_file)
# print(metadata)