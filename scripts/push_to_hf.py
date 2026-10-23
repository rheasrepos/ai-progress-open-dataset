"""Upload data/ and the dataset card to Hugging Face. Run by CI on merge to main.
Needs: pip install huggingface_hub; env HF_TOKEN and HF_DATASET_REPO (e.g. "rheamad/ai-progress-open-dataset")."""
import os, shutil, tempfile
from pathlib import Path
from huggingface_hub import HfApi

root = Path(__file__).parent.parent
repo = os.environ["HF_DATASET_REPO"]
api = HfApi(token=os.environ["HF_TOKEN"])
api.create_repo(repo, repo_type="dataset", exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    shutil.copytree(root / "data", Path(tmp) / "data")
    shutil.copy(root / "hf" / "README.md", Path(tmp) / "README.md")
    api.upload_folder(folder_path=tmp, repo_id=repo, repo_type="dataset",
                      commit_message="Sync from GitHub")
print("pushed to", repo)
