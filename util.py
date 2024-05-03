import os
import csv
import re

def get_files_by_extension(folder_path, extension, selectedfile:str=None):
    """
    Get a list of files in a folder with a specific extension.

    Args:
        folder_path (str): The path to the folder.
        extension (str): The file extension to filter files by.
        selectedfile (str): To choose file name.

    Returns:
        list: A list of files with the specified extension in the folder.
    """
    file_list = []

    # List all files in the folder
    for file_name in os.listdir(folder_path):
        if selectedfile is not None:
            if selectedfile in file_name:
                # Check if the file has the specified extension
                if file_name.endswith(extension):
                    file_list.append(os.path.join(folder_path, file_name))
        else:
            # Check if the file has the specified extension
            if file_name.endswith(extension):
                file_list.append(os.path.join(folder_path, file_name))

    return file_list

def get_files_by_extension_filename(folder_path, extension, selectedfile:str=None):
    file_list = []

    # List all files in the folder
    for file_name in os.listdir(folder_path):
        if selectedfile is not None:
            if selectedfile in file_name:
                # Check if the file has the specified extension
                if file_name.endswith(extension):
                    file_list.append(file_name)
        else:
            # Check if the file has the specified extension
            if file_name.endswith(extension):
                file_list.append(file_name)

    return file_list


def create_csv(file_path, headers):
    """
    Write data to a CSV file with headers.

    Args:
        file_path (str): The path to the CSV file.
        headers (list): The list of header names.
        data (list of lists): The data to be written to the CSV file.
            Each inner list represents a row in the CSV.

    Returns:
        None
    """
    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)  # Write the headers


def add_data_to_csv(data_string, file_path):
    # Split the input string by comma to get individual data elements
    data = data_string.split(',')
    
    # Open the CSV file in append mode
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the data as a new row in the CSV file
        writer.writerow(data)

def read_text_file(file_path):
    """
    Read the contents of a text file and return them as a string.
    
    Args:
    file_path (str): The path to the text file.
    
    Returns:
    str: The contents of the text file as a string.
    """
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
        return file_contents
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")
        return None

def remove_invisible_unicode(input_string):
    # Define a regular expression pattern to match invisible Unicode characters
    invisible_unicode_pattern = re.compile(r'[\x00-\x1F\x7F-\x9F]')

    # Replace all occurrences of invisible Unicode characters with an empty string
    cleaned_string = re.sub(invisible_unicode_pattern, '', input_string)
    
    return cleaned_string