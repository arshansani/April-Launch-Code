import csv
import glob
import re

def get_next_filename(pattern):
    # Create a regex pattern to extract the number
    regex_pattern = pattern.replace('{}', r'(\d+)')
    
    existing_files = glob.glob(pattern.replace('{}', '*'))
    max_number = 0
    for file in existing_files:
        # Extract the number using regex
        match = re.search(regex_pattern, file)
        if match:
            number = int(match.group(1))
            max_number = max(max_number, number)
    
    # Return the next filename
    next_filename = pattern.format(max_number + 1)
    return next_filename

def write_data_to_csv(data, filename):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data.values())