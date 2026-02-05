import json import os import 
shutil import sqlite3 from 
dataclasses import dataclass 
from pathlib import Path from 
typing import List, Optional, 
Dict, Any @dataclass class 
IdentityRecord:
    id_type: str # 'PYN' | 'SID' 
| 'CID'
    id_value: str # artifact_id 
    pyn_id: Optional[str] 
    sid_count: int cid_count: 
    int capability: 
    Optional[str] use_env_last: 
    Optional[str] cid_sequence: 
    Optional[List[str]] 
    source_path: Optional[Path]
def 
_parse_metadata(metadata_json: 
Optional[str]) -> Dict[str, 
Any]:
    if not metadata_json:
        return {}
    try:
        return 
json.loads(metadata_json)
    except json.JSONDecodeError:
        return {} def 
load_identities_from_registry(registry_db: 
Path) -> List[IdentityRecord]:
    """ Load the latest 
    (non-superseded) artifacts 
    from scan_events and decode 
    metadata_json into 
    structured IdentityRecord 
    objects. This matches the 
    current scan_events schema:
      artifact_type TEXT -- 
'PYN' | 'SID' | 'CID'
      artifact_id TEXT pyn_id 
      TEXT sid_count INTEGER 
      cid_count INTEGER 
      capability TEXT 
      metadata_json TEXT -- 
      should contain 
      'source_path' and, for 
      SID, 'cid_sequence' 
      use_env_last TEXT -- usage 
      environment this artifact 
      is currently used in
    """ conn = 
    sqlite3.connect(str(registry_db)) 
    cur = conn.cursor() 
    cur.execute(
        """ SELECT
            artifact_type, 
            artifact_id, pyn_id, 
            sid_count, 
            cid_count, 
            capability, 
            use_env_last, 
            metadata_json
        FROM scan_events WHERE 
        superseded_by_id IS 
        NULL; """
    ) records: 
    List[IdentityRecord] = [] 
    for (
        artifact_type, 
        artifact_id, pyn_id, 
        sid_count, cid_count, 
        capability, 
        use_env_last, 
        metadata_json,
    ) in cur.fetchall():
        meta = 
_parse_metadata(metadata_json)
        cid_sequence = 
meta.get("cid_sequence")
        source_path_raw = 
meta.get("source_path")
        source_path: 
Optional[Path] = None
        if 
isinstance(source_path_raw, str) 
and source_path_raw.strip():
            source_path = 
Path(source_path_raw)
        rec = IdentityRecord(
            
id_type=str(artifact_type),
            
id_value=str(artifact_id),
            pyn_id=str(pyn_id) 
if pyn_id is not None else None,
            
sid_count=int(sid_count or 0),
            
cid_count=int(cid_count or 0),
            
capability=str(capability) if 
capability is not None else 
None,
            
use_env_last=str(use_env_last) 
if use_env_last is not None else 
None,
            
cid_sequence=list(cid_sequence) 
if isinstance(cid_sequence, 
list) else None,
            
source_path=source_path,
        ) records.append(rec)
    conn.close() return records 
def _ensure_dir(path: Path) -> 
None:
    path.mkdir(parents=True, 
exist_ok=True) def 
_place_artifact_file(
    source_path: Optional[Path], 
    dest_dir: Path,
) -> None:
    """ Place an artifact file 
    into dest_dir. If 
    source_path is None or does 
    not exist, this is a no-op. 
    Prefer a symlink; fall back 
    to copy if symlink fails. 
    """ if source_path is None:
        return
    # Resolve absolute path if 
relative (relative to current 
working directory / repo root)
    if not 
source_path.is_absolute():
        source_path = 
(Path.cwd() / 
source_path).resolve()
    if not source_path.exists():
        # Nothing we can do; 
skip quietly
        return
    _ensure_dir(dest_dir) 
    dest_file = dest_dir / 
    source_path.name if 
    dest_file.exists():
        return
    try:
        
dest_file.symlink_to(source_path)
    except OSError:
        
shutil.copy2(source_path, 
dest_file) def 
_sid_sequence_pattern(cid_sequence: 
Optional[List[str]]) -> str:
    """ Encode the ordered CID 
    list into a deterministic 
    folder name. """ if not 
    cid_sequence:
        return "CID-seq_unknown"
    safe_parts = [str(c) for c 
in cid_sequence]
    return "CID-seq_" + 
"_".join(safe_parts) def 
rebuild_index(artifacts_root: 
Path, registry_db: Path) -> 
None:
    """ Rebuild the Artifacts/ 
    index views from the 
    registry. Inputs:
      artifacts_root: Path to 
the Artifacts/ directory.
      registry_db: Path to 
modules/registry/registry.sqlite.
    This function:
      1) Loads all current 
artifacts from scan_events.
      2) For each artifact, 
computes its target view 
path(s).
      3) Creates the necessary 
folders under Artifacts/.
      4) Places (symlinks or 
copies) the artifact file into 
those folders.
    """ artifacts_root = 
    artifacts_root.resolve() 
    registry_db = 
    registry_db.resolve() 
    records = 
    load_identities_from_registry(registry_db) 
    for rec in records:
        env = rec.use_env_last 
or "unknown"
        if rec.id_type == "PYN":
            # PY view sid_bucket 
            = 
            f"SID-count_{rec.sid_count:03d}" 
            dest_dir = 
            artifacts_root / 
            "PY" / env / 
            sid_bucket / 
            rec.id_value 
            _place_artifact_file(rec.source_path, 
            dest_dir)
        elif rec.id_type == 
"SID":
            # SID view 
            cid_bucket = 
            f"CID-count_{rec.cid_count:03d}" 
            seq_pattern = 
            _sid_sequence_pattern(rec.cid_sequence) 
            dest_dir = (
                artifacts_root / 
                "SID" / env / 
                cid_bucket / 
                seq_pattern / 
                rec.id_value
            ) 
            _place_artifact_file(rec.source_path, 
            dest_dir)
        elif rec.id_type == 
"CID":
            # CID view cid_key = 
            rec.id_value if 
            rec.capability:
                cap_folder = 
f"{cid_key}__cap_{rec.capability}"
            else:
                cap_folder = 
cid_key
            dest_dir = 
artifacts_root / "CID" / cid_key 
/ cap_folder
            
_place_artifact_file(rec.source_path, 
dest_dir)
        else:
            # Unknown type; 
ignore
            continue def main() 
-> None:
    """ CLI entry point. 
    Defaults:
      artifacts_root = 
<repo_root>/Artifacts
      registry_db = 
<repo_root>/modules/registry/registry.sqlite
    You can override via 
environment variables:
      CPW_ARTIFACTS_ROOT 
      CPW_REGISTRY_DB
    """ repo_root = 
    Path(__file__).resolve().parents[2] 
    artifacts_root = Path(
        
os.environ.get("CPW_ARTIFACTS_ROOT", 
str(repo_root / "Artifacts"))
    ) registry_db = Path(
        os.environ.get(
            "CPW_REGISTRY_DB", 
            str(repo_root / 
            "modules" / 
            "registry" / 
            "registry.sqlite"),
        )
    ) 
    rebuild_index(artifacts_root, 
    registry_db)
if __name__ == "__main__":
    main()
