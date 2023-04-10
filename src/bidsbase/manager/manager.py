from pathlib import Path
import json
from typing import Union
import pybids


class Manager:
    def __init__(self, bids_dir: Union[str, Path]):
        self.bids_dir = Path(bids_dir)
        self.layout = pybids.BIDSLayout(str(self.bids_dir))

    def validate(self):
        # Validate the BIDS directory
        return self.layout.validate()

    def search(self, suffix):
        # Use glob to search for files with a specific suffix in the BIDS directory
        return list(self.bids_dir.glob(f'**/*{suffix}'))

    def read_json(self, filename):
        # Read a JSON file from the BIDS directory
        with open(self.bids_dir / filename, 'r') as f:
            data = json.load(f)
        return data

    def write_json(self, data, filename):
        # Write a JSON file to the BIDS directory
        with open(self.bids_dir / filename, 'w') as f:
            json.dump(data, f)

    def rename_file(self, old_filename, new_filename):
        # Rename a file in the BIDS directory
        (self.bids_dir / old_filename).rename(self.bids_dir / new_filename)

    def rename_dir(self, old_dirname, new_dirname):
        # Rename a directory in the BIDS directory
        (self.bids_dir / old_dirname).rename(self.bids_dir / new_dirname)
