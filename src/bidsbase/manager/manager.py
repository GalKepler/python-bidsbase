from pathlib import Path
import json
from typing import Union
import pybids


class Manager:
    def __init__(self, bids_dir: Union[str, Path]):
        self.bids_dir = Path(bids_dir)
        self.layout = pybids.BIDSLayout(str(self.bids_dir))

    def validate(self) -> bool:
        """
        Validate the BIDS directory

        Returns
        -------
        bool
            True if the BIDS directory is valid, False otherwise
        """
        return self.layout.validate()

    def search(self, suffix: str) -> list:
        """
        Search for files with a specific suffix in the BIDS directory

        Parameters
        ----------
        suffix : str
            The suffix to search for

        Returns
        -------
        list
            A list of paths to files with the specified suffix
        """
        return list(self.bids_dir.glob(f'**/*{suffix}'))
