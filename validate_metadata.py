#!/usr/bin/env python3

import argparse
import csv


class DataConstants:
    """Data: contains the constants needed to parse the csv files"""

    asset_type_or_class_list = [
        'archive',
        'Audio Stem',
        'Dubbed Audio',
        'OV Audio',
        'package',
        'Restored Audio'
    ]

    folder_names_exclude_list = [
        'Trailer'
    ]

    missing_metadata_columns = [
        'title_gpms_ids',
        'custom_metadata.content_details.language_dubbed',
        'custom_metadata.dcs.dcs_vendor',
        'custom_metadata.format_details.audio_configuration',
        'custom_metadata.format_details.audio_element'
    ]

    # code | Metadata value
    audio_code_map = {
        '20': 'Standard Stereo',
        '51': '5.1 (Discrete)',
        '50': '5.0 (Discrete)',
        'DS': 'Lt-Rt (Dolby Surround)',
        'ATM': 'Atmos'
    }


def get_empty_metadata_columns(output_row: dict) -> list:
    """Return a list of empty metadata columns.
    Cell must have a length greater than 0."""
    return [col_name for col_name in DataConstants.missing_metadata_columns
            if len(output_row[col_name]) == 0]


def get_missing_columns_str(missing_cols: list) -> str:
    """Return a concatenated string with all column names seperated by a space"""
    return ' '.join((str(col) for col in missing_cols))


def has_metadata_discrepancy(output_row: dict) -> bool:
    """Return True if the audio code does not match the metadata code located in """
    file_name_zip = str(output_row['name']).split('.')

    # double check that all filenames must end with .zip or else this will be wrong!
    if file_name_zip[-1] != 'zip':
        return False

    # audio code index in str appear to be 4
    audio_code_idx = 4

    # split the filename according the underscores
    file_name = str(output_row['name']).split('_')

    # get the audio code
    audio_code = file_name[audio_code_idx]

    # Return True if the audio code in the file name does not match the metadata
    return DataConstants.audio_code_map.get(audio_code) != \
        output_row['custom_metadata.format_details.audio_configuration']


def has_folder_exclusion_name(output_row: dict) -> bool:
    """If the folder exclusion name (ex. 'Trailer')
    is in the 'folder_name' column, don't save it"""
    result = [True for exclusion_name in DataConstants.folder_names_exclude_list
              if exclusion_name in output_row['folder_names']]
    return any(result)


def main(source_file, output_file):
    with open(source_file, 'r', encoding='utf-8-sig', newline='') as source_io, \
            open(output_file, 'w', encoding='utf-8', newline='') as output_io:

        # read in source file as CSV
        reader = csv.DictReader(source_io)

        # copy fieldnames from reader for writer
        # fieldnames = reader.fieldnames + []

        # Am I allowed to do this?
        fieldnames = reader.fieldnames + \
            ['missing_metadata', 'metadata_discrepancy'] + []

        # open output file as CSV
        writer = csv.DictWriter(output_io, fieldnames=fieldnames)

        # write the fieldnames
        writer.writeheader()

        for row in reader:
            # copy the row
            output_row = row.copy()

            # Continue if the row value is in asset_type_or_class_list
            if output_row['asset_type_or_class'] not in DataConstants.asset_type_or_class_list:
                continue

            if has_folder_exclusion_name(output_row):
                continue

            missing_cols = get_empty_metadata_columns(output_row)
            missing_cols_str = get_missing_columns_str(missing_cols)
            output_row['missing_metadata'] = missing_cols_str

            if has_metadata_discrepancy(output_row):
                output_row['metadata_discrepancy'] = 'True'

            # Do Something -> (Hopefully I did something right)
            writer.writerow(output_row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'source_file',
        help='Runner inventory CSV report'
    )
    parser.add_argument(
        'output_file',
        help='Filename of the resulting report'
    )
    args = parser.parse_args()
    main(args.source_file, args.output_file)
