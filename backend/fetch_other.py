"""Fetch a balanced 'other' (not-a-medicine) class for the CNN.

Downloads diverse real photographs from Lorem Picsum (picsum.photos) into
dataset/train/other and dataset/test/other so the classifier can learn to
reject images that are not medicine boxes.

Counts are matched to one medicine class (~27 train / 6 test) so the new
class does not dominate training. We pull a few extra for diversity.
"""
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATASET = os.path.join(ROOT, "dataset")

TRAIN_DIR = os.path.join(DATASET, "train", "other")
TEST_DIR = os.path.join(DATASET, "test", "other")

N_TRAIN = 40
N_TEST = 10
SIZE = 400  # download at 400x400 real photos; the model resizes to 224 later.


def download(seed, dest):
    url = f"https://picsum.photos/seed/{seed}/{SIZE}/{SIZE}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    with open(dest, "wb") as fh:
        fh.write(data)
    return len(data)


def fetch_into(folder, count, seed_prefix):
    os.makedirs(folder, exist_ok=True)
    ok = 0
    seed = 0
    while ok < count:
        seed += 1
        name = f"other_{seed_prefix}_{seed:03d}.jpg"
        dest = os.path.join(folder, name)
        try:
            size = download(f"{seed_prefix}{seed}", dest)
            if size < 1000:  # too small -> likely an error placeholder, skip
                os.remove(dest)
                continue
            ok += 1
            print(f"  [{ok}/{count}] {name} ({size} bytes)")
        except Exception as e:
            print(f"  skip seed {seed}: {e}")
        time.sleep(0.2)  # be polite to the server
    return ok


if __name__ == "__main__":
    print(f"Downloading {N_TRAIN} train images -> {TRAIN_DIR}")
    fetch_into(TRAIN_DIR, N_TRAIN, "tr")
    print(f"\nDownloading {N_TEST} test images -> {TEST_DIR}")
    fetch_into(TEST_DIR, N_TEST, "te")
    print("\nDone. 'other' class is ready. Now retrain with: py train.py")
