from pathlib import Path
import json
from typing import Union
from bids.layout.validation import validate_root
from bidsbase.manager.utils.logger import initiate_logger


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
        self.logger = initiate_logger(Path(root).parent, name="BIDSBase")
        self.logger.info(f"Initializing BIDS Manager for {root}")
        self.logger.info(f"Validating BIDS dataset: {validate}")
        try:
            self.root, self.description = validate_root(
                root, validate=validate
            )
            self.logger.info(
                f"Successfully validated BIDS dataset: {self.description}"
            )
        except Exception as e:
            self.logger.error(f"Failed to validate BIDS dataset: {e}")
            raise e
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
