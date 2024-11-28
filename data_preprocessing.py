"""Renaming dataset that has already data augmentation such as contrast, brightness, sharpen, rotations etc."""
""" Replace "path" with you path """

import os

train_path = r'path\data\train\brown_bear'
val_path = r'path\data\val\brown_bear'
test_path= r'path\data\test\brown_bear'

train_files = os.listdir(train_path)
val_files = os.listdir(val_path)
test_files = os.listdir(test_path)

train_files.sort()
val_files.sort()
test_files.sort()

"""RENAMING TRAINING FILES TO TESTindex.jpg"""
for index, train_file_name in enumerate(train_files, start=1):
    old_train_file_path = os.path.join(train_path, train_file_name)

    if os.path.isfile(old_train_file_path):

        _, train_file_extension = os.path.splitext(train_file_name)

        new_train_file_name = f"train{index}{train_file_extension}"
        new_train_file_path = os.path.join(train_path, new_train_file_name)

        os.rename(old_train_file_path, new_train_file_path)
        print(f"Renamed: {train_file_name} -> {new_train_file_name}")

"""RENAMING VALIDATION DATASET TO VALindex.jpg"""
for index, val_file_name in enumerate(val_files, start=1):
    old_val_file_path = os.path.join(val_path, val_file_name)

    if os.path.isfile(old_val_file_path):
        _, val_file_extension = os.path.splitext(val_file_name)

        new_val_file_name = f"val{index}{val_file_extension}"
        new_val_file_path = os.path.join(val_path, new_val_file_name)

        os.rename(old_val_file_path, new_val_file_path)
        print(f"Renamed: {val_file_name} -> {new_val_file_name}")

"""RENAMING TEST DATASET TO TESTindex.jpg"""
for index, test_file_name in enumerate(test_files, start=1):
    old_test_file_path = os.path.join(test_path, test_file_name)

    if os.path.isfile(old_test_file_path):
        _, test_file_extension = os.path.splitext(test_file_name)

        new_test_file_name = f"test{index}{test_file_extension}"
        new_test_file_path = os.path.join(test_path, new_test_file_name)

        os.rename(old_test_file_path, new_test_file_path)
        print(f"Renamed: {test_file_name} -> {new_test_file_name}")
