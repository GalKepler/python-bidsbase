from pathlib import Path
import json
from typing import Union
from bids.layout.validation import validate_root


class Manager:
    def __init__(self, root: Union[str, Path], validate: bool = True):
        """
        Initialize a BIDS Manager

        Parameters
        ----------
        root : Union[str, Path]
            The root directory of the BIDS dataset
        validate : bool, optional
            Whether to validate the BIDS dataset, by default True
        """
        self.root, self.description = validate_root(root, validate=validate)
        self._copy_to = None

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
        return list(self.root.glob(f'**/*{suffix}'))

    @property
    def copy_to(self):
        return self._copy_to

    @copy_to.setter
    def copy_to(self, value: Union[str, Path]):
        if value is None:
            self._copy_to = None
        else:
            self._copy_to = Path(value)
