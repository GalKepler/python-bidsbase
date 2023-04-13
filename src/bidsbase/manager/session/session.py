import logging
from pathlib import Path
from typing import Union

from bidsbase.manager.session import COMMON_FIXES
from bidsbase.manager.utils.logger import initiate_logger


class Session:
    """
    Session class for BIDSBase
    """

    def __init__(
        self,
        path: Union[str, Path],
        auto_fix: bool = True,
        logger: logging.Logger = None,
    ):
        """
        Initialize a Session object

        Parameters
        ----------
        path : Union[str, Path]
            The path to the session directory
        """
        self.path = Path(path)
        self.auto_fix = auto_fix
        self.logger = logger if logger is not None else initiate_logger(self.path.parent.parent.parent, name="Session")
        self.logger.info(f"Initializing Session object for {self.path}")
        self.fixed = False

    def __repr__(self) -> str:
        """
        Representation of the Session object

        Returns
        -------
        str
            The representation of the Session object
        """
        return f"<Session {self.name}>"

    def __str__(self) -> str:
        """
        String representation of the Session object

        Returns
        -------
        str
            The string representation of the Session object
        """
        return self.name

    def fix(self, fixes: list = COMMON_FIXES):
        """
        Fix the session directory

        Parameters
        ----------
        fixes : list, optional
            The list of fixes to apply, by default COMMON_FIXES
        """
        self.logger.info(f"Fixing session {self.name}")
        files_changed = {}
        for fix in fixes:
            self.logger.info(f"Applying fix {fix.__name__}")
            fixed, fix_changed = fix(
                logger=self.logger,
                session_path=self.path,
                auto_fix=self.auto_fix,
            )
            if fixed:
                self.fixed = True
                self.logger.info(f"Successfully applied fix {fix.__name__}")
                files_changed.update(fix_changed)
        # change files changed keys and values to be strings
        files_changed = {str(k): str(v) if v is not None else "deleted" for k, v in files_changed.items()}
        return files_changed

    @property
    def name(self):
        return self.path.name.split('-')[-1]
