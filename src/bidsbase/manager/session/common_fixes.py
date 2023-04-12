import logging
from pathlib import Path
from typing import Union
from bids.layout import parse_file_entities
import json


def update_fieldmap_json(
    files_mapping: dict,
    logger: logging.Logger,
    session_path: Union[str, Path],
) -> None:
    """
    Update the IntendedFor field of the fieldmap json files

    Parameters
    ----------
    files_mapping : dict
        A dictionary mapping the old file names to the new file names
    logger : logging.Logger
        The logger
    session_path : Union[str, Path]
        The path to the session directory

    Returns
    -------
    None
    """
    logger.info(f"Updating fieldmap json files in {session_path}")
    session_path = Path(session_path)
    for fieldmap_json in session_path.glob("fmap/*.json"):
        with open(fieldmap_json, "r") as f:
            fieldmap_json_dict = json.load(f)
        if "IntendedFor" in fieldmap_json_dict:
            intended_for = fieldmap_json_dict["IntendedFor"]
            for key, val in files_mapping.items():
                intended_for_key = str(
                    Path(key).relative_to(session_path.parent)
                )
                if intended_for_key in intended_for:
                    if val is not None:
                        intended_for_val = str(
                            Path(val).relative_to(session_path.parent)
                        )
                        logger.info(
                            f"Updating {intended_for_key} to {intended_for_val}"
                        )
                        intended_for[
                            intended_for.index(intended_for_key)
                        ] = intended_for_val
                    else:
                        logger.info(
                            f"Removing {intended_for_key} from {fieldmap_json}"
                        )
                        intended_for.remove(intended_for_key)
            fieldmap_json_dict["IntendedFor"] = intended_for
            with open(fieldmap_json, "w") as f:
                json.dump(fieldmap_json_dict, f, indent=4)
            logger.info(f"Updated {fieldmap_json}")


def fix_multiple_dwi_runs(
    logger: logging.Logger,
    session_path: Union[str, Path],
    auto_fix: bool = True,
) -> None:
    """
    Fix multiple DWI runs in a session directory

    Parameters
    ----------
    logger : logging.Logger
        The logger
    session_path : Union[str, Path]
        The path to the session directory
    auto_fix : bool, optional
        Whether to automatically fix the issue, by default False

    Returns
    -------
    None
    """
    logger.info(f"Searching for multiple DWI runs in {session_path}")
    session_path = Path(session_path)
    dwi_runs = list(session_path.glob("dwi/*run*_dwi.nii*"))
    n_runs = len(dwi_runs)
    if n_runs == 0:
        logger.info(
            f"No multiple DWI runs found in {session_path}. Skipping..."
        )
    if n_runs > 1:
        logger.warning(f"Multiple DWI runs found in {session_path}. Fixing...")
        logger.info(
            f"Configuration for fix_multiple_dwi_runs:\nauto_fix={auto_fix}"
        )
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
        # add a message to logger describing the dwi runs, their number of volumes, and the chosen run
        fix_message = (
            f"Multiple DWI runs found in {session_path}:\n"
            + "\n".join(
                [
                    f"{i+1}: {dwi_run} ({dwi_volumes[i]} volumes)"
                    for i, dwi_run in enumerate(dwi_runs)
                ]
            )
            + f"\nChosen run: {choice}"
        )
        logger.info(fix_message)
        files_mapping = rename_dwi(dwi_runs[choice - 1])
        logger.info(f"Renamed {files_mapping}")
        # remove the other runs
        for dwi_run in dwi_runs:
            for associated_file in dwi_run.parent.glob(
                f"{dwi_run.name.split('.')[0]}*"
            ):
                logger.info(f"Removing {associated_file}")
                associated_file.unlink()
                files_mapping[associated_file] = None
        update_fieldmap_json(files_mapping, logger, session_path)


def rename_dwi(dwi_file: Union[str, Path]) -> str:
    """
    Rename a DWI file to the BIDS standard

    Parameters
    ----------
    dwi_file : Union[str, Path]
        The path to the DWI file

    Returns
    -------
    dict
        A dictionary mapping the old file names to the new file names
    """
    dwi_file = Path(dwi_file)
    files_mapping = {}
    for associated_file in dwi_file.parent.glob(
        f"{dwi_file.name.split('.')[0]}*"
    ):
        run = parse_file_entities(str(associated_file)).get("run")
        new_name = associated_file.name.replace(f"_run-{run}", "")
        associated_file.rename(associated_file.parent / new_name)
        files_mapping[associated_file] = associated_file.parent / new_name
    return files_mapping
