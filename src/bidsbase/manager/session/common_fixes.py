import json
import logging
import subprocess
from pathlib import Path
from typing import Union

from bids.layout import parse_file_entities


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
                intended_for_key = str(Path(key).relative_to(session_path.parent))
                if intended_for_key in intended_for:
                    if val is not None:
                        intended_for_val = str(Path(val).relative_to(session_path.parent))
                        logger.info(f"Updating {intended_for_key} to {intended_for_val}")
                        intended_for[intended_for.index(intended_for_key)] = intended_for_val
                    else:
                        logger.info(f"Removing {intended_for_key} from {fieldmap_json}")
                        intended_for.remove(intended_for_key)
            fieldmap_json_dict["IntendedFor"] = intended_for
            with open(fieldmap_json, "w") as f:
                json.dump(fieldmap_json_dict, f, indent=4)
            logger.info(f"Updated {fieldmap_json}")


def fix_multiple_dwi_runs(
    logger: logging.Logger,
    session_path: Union[str, Path],
    auto_fix: bool = True,
) -> bool:
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
    bool
        Whether the session directory was fixed
    """
    fixed = False
    files_mapping = {}
    logger.info(f"Searching for multiple DWI runs in {session_path}")
    session_path = Path(session_path)
    dwi_runs = list(session_path.glob("dwi/*run*_dwi.nii*"))
    n_runs = len(dwi_runs)
    if n_runs == 0:
        logger.info(f"No multiple DWI runs found in {session_path}. Skipping...")
    if n_runs > 1:
        logger.warning(f"Multiple DWI runs found in {session_path}. Fixing...")
        logger.info(f"Configuration for fix_multiple_dwi_runs:\nauto_fix={auto_fix}")
        # locate the number of volumes in each run by looking at the corresponding .bval file
        dwi_volumes = [
            len(Path(dwi_run.parent / dwi_run.name.split(".")[0]).with_suffix(".bval").read_text().split()) for dwi_run in dwi_runs
        ]
        # sort the volumns and runs by number of volumes
        dwi_runs, dwi_volumes = zip(*sorted(zip(dwi_runs, dwi_volumes), key=lambda x: x[1]))
        if not auto_fix:
            # let the user choose which run to keep, based on the number of volumes
            print(f"Multiple DWI runs found in {session_path}. Please choose which run to keep:")
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
            + "\n".join([f"{i+1}: {dwi_run} ({dwi_volumes[i]} volumes)" for i, dwi_run in enumerate(dwi_runs)])
            + f"\nChosen run: {choice}"
        )
        logger.info(fix_message)
        files_mapping = rename_dwi(dwi_runs[choice - 1])
        logger.info(f"Renamed {files_mapping}")
        # remove the other runs
        for dwi_run in dwi_runs:
            for associated_file in dwi_run.parent.glob(f"{dwi_run.name.split('.')[0]}*"):
                logger.info(f"Removing {associated_file}")
                associated_file.unlink()
                files_mapping[associated_file] = None
        update_fieldmap_json(files_mapping, logger, session_path)
        fixed = True
    return fixed, files_mapping


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
    for associated_file in dwi_file.parent.glob(f"{dwi_file.name.split('.')[0]}*"):
        run = parse_file_entities(str(associated_file)).get("run")
        new_name = associated_file.name.replace(f"_run-{run}", "")
        associated_file.rename(associated_file.parent / new_name)
        files_mapping[associated_file] = associated_file.parent / new_name
    return files_mapping


def generate_fieldmap_from_dwi(
    logger: logging.Logger,
    session_path: Union[str, Path],
    auto_fix: bool = True,
):
    """
    Generate a fieldmap from a DWI file

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
    bool
        Whether the session directory was fixed
    """
    fixed = False
    files_mapping = {}
    logger.info(f"Searching for reversed-phased DWIs in {session_path}")
    session_path = Path(session_path)
    forwared_phased_dwis = list(session_path.glob("dwi/*dir-FWD*_dwi.nii*"))
    reversed_phased_dwis = list(session_path.glob("dwi/*dir-REV*_dwi.nii*"))
    n_reversed_phased_dwis = len(reversed_phased_dwis)
    if n_reversed_phased_dwis == 0:
        logger.info(f"No reversed-phased DWIs found in {session_path}. Skipping...")
    else:
        reversed_phased_dwi = reversed_phased_dwis[0]
        logger.info(f"Found reversed-phased DWI: {reversed_phased_dwi}")
        bvec, bval, json_file = get_bvec_bval_json(reversed_phased_dwi)
        base_entities = parse_file_entities(str(reversed_phased_dwi))
        base_entities.update({"suffix": "epi", "datatype": "fmap", "acquisition": "dwi"})
        new_base_name = generate_fieldmap_name(base_entities)
        out_nifti = session_path / f"{new_base_name}.nii.gz"
        new_json_file = session_path / f"{new_base_name}.json"
        if out_nifti.exists() and new_json_file.exists():
            logger.info(f"Fieldmap already exists in {session_path}. Skipping...")
        else:
            extract_b0(reversed_phased_dwi, bvec, bval, out_nifti, logger=logger)
            files_mapping[reversed_phased_dwi] = out_nifti
            logger.info(f"Extracted b0 from {reversed_phased_dwi} to {out_nifti}")
            # copy the json file and edit it to match the new file
            copy_and_edit_fieldmap_json(
                json_file,
                new_json_file,
                forwared_phased_dwis,
                session_path.parent,
            )
            files_mapping[json_file] = new_json_file
            logger.info(f"Copied {json_file} to {new_json_file}")
            # remove dwis from acq-rest fieldmaps
            for fmap in session_path.glob("fmap/*_acq-rest_*.json"):
                logger.info(f"Removing forward phased dwi from {fmap}")
                with open(fmap, "r") as f:
                    json_data = json.load(f)
                intended_for = json_data["IntendedFor"]
                json_data["IntendedFor"] = [i for i in intended_for if parse_file_entities(i)["datatype"] != "dwi"]
                with open(fmap, "w") as f:
                    json.dump(json_data, f, indent=4)

            fixed = True
    return fixed, files_mapping


def copy_and_edit_fieldmap_json(
    json_file: Union[str, Path],
    new_json_file: Union[str, Path],
    intended_for: list[Path],
    relative_to: Path,
):
    """
    Copy a fieldmap json file and edit it to match the new file

    Parameters
    ----------
    json_file : Union[str, Path]
        The path to the original json file
    new_json_file : Union[str, Path]
        The path to the new json file
    intended_for : list[Path]
        The list of files the new json file is intended for
    relative_to : Path
        The path to the directory the new json file is relative to
    """
    with open(json_file, "r") as f:
        json_data = json.load(f)
    json_data["IntendedFor"] = [str(file.relative_to(relative_to)) for file in intended_for]
    with open(new_json_file, "w") as f:
        json.dump(json_data, f, indent=4)


def extract_b0(in_file: str, bvec: str, bval: str, out_file: str, logger: logging.Logger):
    """
    Extract the b0 volumes from a dwi file

    Parameters
    ----------
    in_file : str
        The dwi file
    bvec : str
        The bvec file
    bval : str
        The bval file
    out_file : str
        The output file
    """
    cmd = f"dwiextract {in_file} -bzero -fslgrad {bvec} {bval} {out_file}"
    logger.info(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def generate_fieldmap_name(entities: dict) -> str:
    """
    Based on the entities, generate a name for the fieldmap

    Parameters
    ----------
    entities : dict
        The entities

    Returns
    -------
    str
        The name of the fieldmap
    """
    return f"{entities['datatype']}/sub-{entities['subject']}_ses-{entities['session']}_acq-{entities['acquisition']}_dir-{entities['direction']}_{entities['suffix']}"  # noqa


def get_bvec_bval_json(in_file: Path):
    """
    Gets the corresponding bvec, bval and json files for a given dwi file

    Parameters
    ----------
    in_file : Path
        The dwi file

    Returns
    -------
    Tuple(Path,Path,Path)
        The bvec, bval and json files
    """
    bvec = in_file.parent / ".".join([in_file.name.split(".")[0], "bvec"])
    bval = in_file.parent / ".".join([in_file.name.split(".")[0], "bval"])
    json_file = in_file.parent / ".".join([in_file.name.split(".")[0], "json"])
    return bvec, bval, json_file
