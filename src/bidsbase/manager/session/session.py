from pathlib import Path
from typing import Union


class Session:
    """
    Session class for BIDSBase
    """

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)

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

    def fix(self):
        """
        Fix the session directory
        """
        # TODO: Implement this
        pass

    @property
    def name(self):
        return self.path.name.split('-')[-1]
