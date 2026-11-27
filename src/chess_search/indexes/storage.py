import lmdb

MAP_SIZE = 2**40
MAX_DBS = 8


def open_lmdb_env(path, readonly=False):
    return lmdb.open(path, map_size=MAP_SIZE, max_dbs=MAX_DBS, readonly=readonly)


def push_to_hub(path, repo_id):
    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
    api.upload_folder(folder_path=path, repo_id=repo_id, repo_type="dataset", ignore_patterns=["lock.mdb"])


def download_from_hub(repo_id):
    from huggingface_hub import snapshot_download

    return snapshot_download(repo_id=repo_id, repo_type="dataset")
