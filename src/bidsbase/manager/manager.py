import json
import os
import shutil
from pathlib import Path
from typing import Union

from bids.layout.validation import validate_root

from bidsbase.manager.session import COMMON_FIXES
from bidsbase.manager.session.session import Session
from bidsbase.manager.utils.logger import initiate_logger


class Manager:
    FIXES = COMMON_FIXES.copy()

    def __init__(
        self,
        root: Union[str, Path],
        validate: bool = True,
        copy_to: Union[str, Path] = None,
        force_copy: bool = False,
        auto_fix: bool = True,
        work_dir: Union[str, Path] = None,
        stop_on_first_crash: bool = False,
    ):
        """
        Initialize a BIDS Manager

        Parameters
        ----------
        root : Union[str, Path]
            The root directory of the BIDS dataset
        validate : bool, optional
            Whether to validate the BIDS dataset, by default True
        """
        self.work_dir = Path(work_dir) if work_dir is not None else Path(root).parent / "BIDSBase"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.stop_on_first_crash = stop_on_first_crash
        self.logger = initiate_logger(Path(root).parent, name="BIDSBase")
        self.logger.info(f"Initializing BIDS Manager for {root}")
        self.logger.info(f"Validating BIDS dataset: {validate}")
        try:
            self.root, self.description = validate_root(root, validate=validate)
            self.logger.info("Successfully validated BIDS dataset:" + "\n" + json.dumps(self.description, indent=4))
        except Exception as e:
            self.logger.error(f"Failed to validate BIDS dataset: {e}")
            raise e
        self._copy_to = self.root.parent / f"{self.root.name}_BIDSBase" if copy_to is None else Path(copy_to)
        self.auto_fix = auto_fix
        self.create_copy(force=force_copy)

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

    def create_copy(self, force=False):
        """
        Create a copy of the BIDS dataset in a new directory
        """
        self.logger.info("Creating copy of BIDS dataset")
        for subject in self.subjects:
            for session in self.root.glob(f"sub-{subject}/ses-*"):
                new_path = Path(self.copy_to / session.relative_to(self.root))
                if new_path.exists() and not force:
                    self.logger.info(f"Copy of session {session} already exists: {new_path}")
                    continue
                elif new_path.exists() and force:
                    self.logger.info(f"Removing existing copy of session {session}")
                    shutil.rmtree(new_path)
                self.logger.info(f"Copying session {session} to {new_path}")
                new_path.mkdir(parents=True, exist_ok=True)
                os.system(f"rsync -azPL {session}/* {new_path}")
                self.logger.info(f"Successfully copied session {session} to {new_path}")
        for additional_file in self.root.glob("*"):
            if not additional_file.name.startswith("sub-*"):
                os.system(f"rsync -azPL {additional_file} {self.copy_to}")
        self.logger.info("Successfully created copy of BIDS dataset")

    def fix_dataset(self):
        """
        Fix the BIDS dataset according to known issues
        """
        self.logger.info("Fixing BIDS dataset")
        for subject in self.subjects:
            for session in self.sessions[subject].values():
                try:
                    changed_files = session.fix(fixes=self.FIXES)
                except Exception as e:
                    self.logger.error(f"Failed to fix BIDS dataset for subject {subject}, " f"session {session}: {e}")
                    if self.stop_on_first_crash:
                        raise e
                    continue
                if session.fixed:
                    session_work_dir = self.work_dir / session.path.relative_to(self.copy_to)
                    session_work_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.info(
                        f"Fixed BIDS dataset for subject {subject}, "
                        f"session {session}.\n"
                        "Summary of changed files can be located at "
                        f"{session_work_dir / 'fixes.json'}",
                    )
                    with open(session_work_dir / "fixes.json", "w") as f:
                        json.dump(changed_files, f, indent=4)

    @property
    def subjects(self) -> list:
        """
        Get a list of subjects in the BIDS dataset

        Returns
        -------
        list
            A list of subjects
        """
        return [i.name.split("-")[-1] for i in self.root.glob("sub-*")]

    @property
    def sessions(self) -> dict:
        """
        Get a dictionary of sessions for each subject in the BIDS dataset

        Returns
        -------
        dict
            A dictionary of sessions for each subject
        """
        return {
            subject: {
                i.name.split("-")[-1]: Session(path=i, auto_fix=self.auto_fix, logger=self.logger)
                for i in self.copy_to.glob(f"sub-{subject}/ses-*")
            }
            for subject in self.subjects
        }

    @property
    def copy_to(self):
        return self._copy_to

    @copy_to.setter
    def copy_to(self, value: Union[str, Path]):
        if value is None:
            self._copy_to = None
        else:
            self._copy_to = Path(value)
