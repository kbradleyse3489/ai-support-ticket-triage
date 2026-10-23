"""Package the reviewable source, licensed data, model and measured deliverables."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'AI_Support_Ticket_Triage_Quality_Review_Keisha_Walker.zip'
EXCLUDE_DIRS={'__pycache__','.pytest_cache','.ipynb_checkpoints','.venv','venv','qa_render','rendered','_render','render_qa','qa','qa_v2','qa_v3','qa_v4'}
EXCLUDE_NAMES={'demo_capture.log','demo_server.log','clean_install.log','package_check.txt','MANIFEST.sha256'}
files=[]
for p in ROOT.rglob('*'):
    relative=p.relative_to(ROOT)
    if p.is_file() and not any(part in EXCLUDE_DIRS or part.startswith('qa_') for part in relative.parts) and p.name not in EXCLUDE_NAMES and p.suffix not in {'.pyc','.zip'}:
        files.append(p)
files=sorted(files)
manifest=ROOT/'MANIFEST.sha256'
manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files))
files.append(manifest)
with ZipFile(OUT,'w',ZIP_DEFLATED,compresslevel=8) as z:
    for p in files:z.write(p,Path('AI_Support_Ticket_Triage_Quality_Review')/p.relative_to(ROOT))
with ZipFile(OUT) as z:
    assert z.testzip() is None
print(OUT)
print('Files:',len(files),'Bytes:',OUT.stat().st_size,'SHA256:',hashlib.sha256(OUT.read_bytes()).hexdigest())
