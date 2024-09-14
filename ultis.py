import os
import hashlib

def get_md5_of_file(file_path, block_size=65536):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(block_size):
            md5.update(chunk)
    return md5.hexdigest()

def get_creation_time(file_path):
    return os.stat(file_path).st_ctime

def find_duplicate_files(directory, progress_bar, progress_value):
    files_by_size = {}
    duplicates = []

    progress_bar.configure(mode='indeterminate')
    progress_bar.start(50)

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_size = os.path.getsize(file_path)

            if file_size not in files_by_size:
                files_by_size[file_size] = [file_path]
            else:
                files_by_size[file_size].append(file_path)

    progress_bar.stop()
    progress_bar.configure(mode='determinate')
    files_by_size_total = len(files_by_size)
    progress_bar.configure(maximum=files_by_size_total)
    files_processed = 0

    for file_list in files_by_size.values():
        files_processed += 1
        progress_bar.configure(value=files_processed)
        progress_value.configure(text=f"{round((files_processed / files_by_size_total) * 100)}%")
        if len(file_list) < 2:
            continue

        hash_dict = {}
        for file_path in file_list:
            file_md5 = get_md5_of_file(file_path)

            if file_md5 not in hash_dict:
                hash_dict[file_md5] = [file_path]
            else:
                hash_dict[file_md5].append(file_path)

        for file_group in hash_dict.values():
            if len(file_group) > 1:
                original_file = min(file_group, key=get_creation_time)
                duplicates.extend([file for file in file_group if file != original_file])

    progress_bar.configure(value=0)
    progress_value.configure(text='0%')

    return duplicates