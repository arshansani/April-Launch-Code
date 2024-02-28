import csv
import glob

def get_next_filename():
    existing_files = glob.glob('sensor_data_*.csv')
    max_number = 0
    for file in existing_files:
        # Extract the part of the filename that should contain the number
        file_number_part = file.replace('sensor_data_', '').replace('.csv', '')
        
        # Check if this part is a number
        if file_number_part.isdigit():
            number = int(file_number_part)
            max_number = max(max_number, number)

    # Return the next file name
    file_number = max_number + 1
    filename = f'sensor_data_{file_number}.csv'
    return filename

def write_data_to_csv(data, filename):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data.values())