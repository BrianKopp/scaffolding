import os
from typing import List
from pathlib import Path
import logging

def find_files(in_path: str, matching: List[str]) -> List[str]:
    """finds files in path recursively matching patterns
    
    Arguments:
        in_path {str} -- path to search recursively
        matching {list} -- list of strings matching pattern
    
    Returns:
        list -- files matching pattern, with path relative to in_path
    """
    files = []
    path = Path(in_path)
    for pattern in matching:
        files.extend(path.glob(pattern))
    return list(set(files))


def find_files_with_text(in_path: str, matching_file_names: List[str],
                         search_text: str) -> List[str]:
    """finds files in path which has the search_text
    
    Arguments:
        in_path {str} -- path to search recursively
        matching_file_names {List[str]} -- file patterns to match
        search_text {str} -- text to search for
    
    Returns:
        List[str] -- list of files with the search text
    """
    files = []
    matching_files = find_files(in_path, matching_file_names)
    for f in matching_files:
        with open(os.path.join(in_path, f), 'r') as fh:
            contents = fh.read()
        if search_text in contents:
            files.append(f)
    return list(set(files))


def find_and_replace(in_path: str, matching_file_names: List[str],
                     search_text: str, replace_text: str) -> List[str]:
    """finds and replaces text in files
    
    Arguments:
        in_path {str} -- path to search recursively
        matching_file_names {List[str]} -- file name patterns
        search_text {str} -- text to search for and replace
        replace_text {str} -- replace text
    
    Returns:
        List[str] -- files affected
    """
    found_files = find_files_with_text(in_path, matching_file_names, search_text)
    for ff in found_files:
        with open(os.path.join(in_path, found_files), 'r') as f:
            contents = f.read()
        new_contents = contents.replace(search_text, replace_text)
        with open(os.path.join(in_path, found_files), 'w') as f:
            f.write(new_contents)
    return found_files


def create_file(in_path: str, file_path: str, text: str):
    """Creates a file with the text. Raises exception if there are any issues
    
    Arguments:
        in_path {str} -- starting path
        file_path {str} -- file path relative to in_path
        text {str} -- text for file
    """
    full_path = os.path.join(in_path, file_path)
    path = os.path.dirname(full_path)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(full_path, 'w') as f:
        f.write(text)
    return


def delete_file(in_path: str, file_path: str):
    """Deletes a file. If not found, raises exception
    
    Arguments:
        in_path {str} -- starting path
        file_path {str} -- path to file to delete
    """
    os.remove(os.path.join(in_path, file_path))
    return
