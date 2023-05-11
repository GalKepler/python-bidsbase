from bidsbase.manager.session.common_fixes import fix_multiple_dwi_runs
from bidsbase.manager.session.common_fixes import generate_fieldmap_from_dwi

COMMON_FIXES = [fix_multiple_dwi_runs, generate_fieldmap_from_dwi]
