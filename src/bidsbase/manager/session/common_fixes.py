from pathlib import Path
from typing import Union
from bids.layout import parse_file_entities

COMMON_FIXES = [
    {
        "name": "fix_multiple_dwi_runs",
        "description": "Fix multiple DWI runs in a session directory",
        "log": "Multiple DWI runs found in {session_path}:",
    },
]


def fix_multiple_dwi_runs(
    session_path: Union[str, Path], auto_fix: bool = False
):
    """
    Fix multiple DWI runs in a session directory
    """
    session_path = Path(session_path)
    dwi_runs = list(session_path.glob("dwi/*run*_dwi.nii*"))
    if len(dwi_runs) > 1:
        # locate the number of volumes in each run by looking at the corresponding .bval file
        dwi_volumes = [
            len(
                Path(dwi_run.parent / dwi_run.name.split(".")[0])
                .with_suffix(".bval")
                .read_text()
                .split()
            )
            for dwi_run in dwi_runs
        ]
        # sort the runs by number of volumes
        dwi_runs = [x for _, x in sorted(zip(dwi_volumes, dwi_runs))]
        if not auto_fix:
            # let the user choose which run to keep, based on the number of volumes
            print(
                f"Multiple DWI runs found in {session_path}. Please choose which run to keep:"
            )
            for i, dwi_run in enumerate(dwi_runs):
                print(f"{i+1}: {dwi_run} ({dwi_volumes[i]} volumes)")
            choice = int(input("Enter the number of the run to keep: "))
            # rename the chosen run to the BIDS standard and remove
        else:
            # "choose" the run with the most volumes
            choice = dwi_volumes.index(max(dwi_volumes)) + 1
        rename_dwi(dwi_runs[choice - 1])


def rename_dwi(dwi_file: Union[str, Path]):
    """
    Rename a DWI file to the BIDS standard
    """
    dwi_file = Path(dwi_file)
    for associated_file in dwi_file.parent.glob(
        f"{dwi_file.name.split('.')[0]}*"
    ):
        run = parse_file_entities(str(associated_file)).get("run")
        new_name = associated_file.name.replace(f"_run-{run}", "")
        print(
            f"Renaming {associated_file} to {associated_file.parent/new_name}"
        )
