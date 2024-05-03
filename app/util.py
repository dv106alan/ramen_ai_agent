import csv
import re

def dict_to_csv2(dictionary, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = dictionary[0].keys() if isinstance(dictionary, list) and len(dictionary) > 0 else dictionary.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        if isinstance(dictionary, list):
            for item in dictionary:
                writer.writerow(item)
        else:
            writer.writerow(dictionary)

def dict_to_csv(dictionary, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['key', 'value'])
        
        for key, value in dictionary.items():
            writer.writerow([key, value])

def csv_to_dict_list(filename):
    dic_list = []
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for dictionary in reader:
            dic_list.append(dictionary)
    return dic_list

def dict_list_to_csv(dict_list, file_path):
    # Extract field names from the keys of the first dictionary
    field_names = dict_list[0].keys()

    # Write the data to a CSV file
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(dict_list)

def read_csv_line_by_line(file_path):
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            yield row

def remove_special_emoji(text):
    # Define a regular expression pattern to match special emojis
    pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
    # Replace special emojis with an empty string
    return pattern.sub('', text)