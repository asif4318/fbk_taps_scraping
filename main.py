import re
import pandas as pd


# Python script authored by Asif Islam on 10/2/2024
# Uses data copied and pasted from pdf of FBK Tapping Classes from 1923 - 2007


def clean_page_numbers_titles(data: list[str]):
    """
    Function that takes data from 'fbk_tapping_class.txt' and removes page numbers and page titles to parse data cleanly
    and returns a cleaned list of data
    """
    # This regex expression searches for lines starting with 1 or 2 numbers (Page Number Lines)
    regex = '\\b\\d{1,2}\\s'
    cleaned_data = []
    for val in data:
        is_page_number = re.search(regex, val)
        # Do not use Florida Blue Key Page Header Lines or Page Numbers
        if not (is_page_number or val.startswith('Florida')):
            cleaned_data.append(val)
    return cleaned_data


def get_honorary(string) -> bool:
    regex = "^H\\s[A-Z]"  # Searches for lines that begin with 'H ' followed by any capital letter
    is_honorary = re.search(regex, string)
    return is_honorary is not None


def strip_honors_text(fullname) -> str:
    stripped_name = fullname
    if get_honorary(fullname):
        stripped_name = fullname[2:]
    return stripped_name


def get_suffix(name) -> str | None:
    name_arr = name.split(',')
    # If no suffix, return None
    if len(name_arr) == 1:
        return None
    # Otherwise return value after the comma
    else:
        return name_arr[-1].strip()


def get_first_last(name) -> list[str]:
    cleaned_name = strip_honors_text(name).removesuffix(get_suffix(name) or '').replace(',', '')
    arr = cleaned_name.split()
    return arr


def create_semesters_list(data: list[str]):
    semesters = []
    for line_position, line in enumerate(data):
        is_year = re.search('^Spring|^Fall', line)
        if is_year:
            semesters.append(
                {"year": line.strip().split()[1], "semester": line.strip().split()[0], "index": line_position})
    return semesters


def export_csv(data: list[str]):
    '''
    Used to export data to csv
    :param data: Data List to be converted into csv
    :return:
    '''
    pd.DataFrame(data).to_csv('fbk_tapping_class.csv', index=False)


def create_final_data_entry(year: str, semester: str, full_name: str):
    split_name = get_first_last(full_name)
    entry = {
        "year": year,
        "semester": semester,
        "first_name": ' '.join(split_name[:-1]),
        "last_name": split_name[-1],
        "suffix": get_suffix(full_name),
        "honorary_status": get_honorary(full_name),
    }
    return entry


if __name__ == '__main__':
    # Open Data
    file = open('fbk_tapping_class.txt', 'r')

    # Clean Data
    tapping_class_data = clean_page_numbers_titles(file.readlines())

    # Write clean data to file for debugging purposes
    # output = open('fbk_clean.txt', 'w')
    # output.writelines(tapping_class_data)

    # Array to hold data to export
    final_data = []

    semester_list = create_semesters_list(tapping_class_data)

    for position, val in enumerate(semester_list):
        section_start = val['index'] + 1  # Next Line after semester header, ex: the line after Fall 1923
        # If last section, go to end of data list. Otherwise, end inner loop at the start of the next section
        section_end = len(tapping_class_data) if position == len(semester_list) - 1 \
            else semester_list[position + 1]['index']

        for x in range(section_start, section_end):
            currentLine = tapping_class_data[x].strip()
            data_row = create_final_data_entry(val['year'], val['semester'], currentLine)
            final_data.append(data_row)

    export_csv(final_data)
