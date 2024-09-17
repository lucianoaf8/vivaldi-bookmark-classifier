import os
import json
import csv
import sys
from pathlib import Path
import datetime

def load_bookmarks(bookmarks_path):
    """
    Loads and parses the bookmarks JSON file.
    Args:
        bookmarks_path: Path to the Bookmarks file.
    Returns:
        Parsed JSON data.
    """
    try:
        with open(bookmarks_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Bookmarks file not found at {bookmarks_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading bookmarks file: {e}")
        sys.exit(1)

def traverse_bookmarks(node, bookmarks_list, path=''):
    """
    Recursively traverses the bookmarks tree to extract bookmark entries.
    Args:
        node: Current node in the bookmarks tree.
        bookmarks_list: List to accumulate bookmarks.
        path: String representing the current path in the bookmarks hierarchy.
    """
    if node.get('type') == 'folder':
        # Update the current path
        current_path = f"{path}/{node.get('name', 'Unnamed Folder')}" if path else node.get('name', 'Unnamed Folder')
        for child in node.get('children', []):
            traverse_bookmarks(child, bookmarks_list, current_path)
    elif node.get('type') == 'url':
        bookmark = {
            'name': node.get('name', 'Unnamed Bookmark'),
            'url': node.get('url', ''),
            'date_added': node.get('date_added', ''),
            'date_modified': node.get('date_modified', ''),
            'path': path
        }
        # Include any additional fields you want from the bookmark node
        for key, value in node.items():
            if key not in bookmark and key != 'children':
                bookmark[key] = value
        bookmarks_list.append(bookmark)

def get_all_bookmarks(data):
    """
    Extracts all bookmarks from the parsed JSON data.
    Args:
        data: Parsed JSON data from the bookmarks file.
    Returns:
        List of bookmarks with their details.
    """
    bookmarks = []
    roots = ['bookmark_bar', 'other', 'synced']

    # Access the 'roots' key first
    roots_data = data.get('roots', {})
    if not roots_data:
        print("No 'roots' key found in the bookmarks file.")
        return bookmarks  # Empty list

    for root_key in roots:
        root = roots_data.get(root_key, {})
        if not root:
            print(f"No '{root_key}' key found under 'roots'.")
            continue
        traverse_bookmarks(root, bookmarks, path=root.get('name', root_key))

    return bookmarks

def export_to_csv(bookmarks, output_file):
    """
    Exports the list of bookmarks to a CSV file.
    Args:
        bookmarks: List of bookmark dictionaries.
        output_file: Path to the output CSV file.
    """
    if not bookmarks:
        print("No bookmarks to export.")
        return

    # Determine all unique keys across all bookmarks for CSV headers
    headers = set()
    for bm in bookmarks:
        headers.update(bm.keys())
    headers = sorted(headers)  # Optional: sort headers alphabetically

    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for bm in bookmarks:
                writer.writerow(bm)
        print(f"Bookmarks successfully exported to {output_file}")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        sys.exit(1)

def convert_webkit_timestamp(webkit_timestamp):
    """
    Converts WebKit timestamp to a readable datetime format.
    Args:
        webkit_timestamp (str): Timestamp in microseconds since 1601-01-01.
    Returns:
        str: Human-readable datetime string.
    """
    try:
        timestamp_int = int(webkit_timestamp)
        # Convert from microseconds to seconds
        timestamp_sec = timestamp_int / 1_000_000
        # WebKit timestamp starts from January 1, 1601
        epoch_start = datetime.datetime(1601, 1, 1)
        readable_time = epoch_start + datetime.timedelta(seconds=timestamp_sec)
        return readable_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return webkit_timestamp  # Return original if conversion fails

def main():
    # Define the path to the Bookmarks file
    bookmarks_path = r"C:\Users\Luciano\AppData\Local\Vivaldi\User Data\Default\Bookmarks"

    # Check if the path exists
    if not Path(bookmarks_path).exists():
        print(f"The specified bookmarks file does not exist:\n{bookmarks_path}")
        sys.exit(1)

    # Load and parse the bookmarks
    data = load_bookmarks(bookmarks_path)
    bookmarks = get_all_bookmarks(data)

    if not bookmarks:
        print("No bookmarks found in the specified file.")
        sys.exit(0)

    # Convert WebKit timestamps to readable format
    for bm in bookmarks:
        bm['date_added'] = convert_webkit_timestamp(bm.get('date_added', ''))
        bm['date_modified'] = convert_webkit_timestamp(bm.get('date_modified', ''))

    # Define the output CSV file path
    script_directory = Path(__file__).parent
    output_file = script_directory / "vivaldi_bookmarks.csv"

    # Export bookmarks to CSV
    export_to_csv(bookmarks, output_file)

if __name__ == '__main__':
    main()
