"""Download only the verified public fictional dataset; preserve existing raw bytes."""
import hashlib
from pathlib import Path
import tempfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://vincentarelbundock.github.io/Rdatasets/csv/gt/pizzaplace.csv'
SHA256 = '243425c7184d31b35b09ae72c468154b1fb3434ec5d4f5cd32c8beb89d1b8801'
TARGET = ROOT / 'data/raw/pizzaplace.csv'

def verify(path):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != SHA256:
        raise ValueError(f'Data checksum mismatch for {path.name}; expected {SHA256}, got {actual}. No source file replaced.')

def main():
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        verify(TARGET)
        print('Verified existing fictional dataset; no download or overwrite needed.')
        return
    temp = None
    try:
        with urlopen(URL, timeout=60) as response:
            with tempfile.NamedTemporaryFile(dir=TARGET.parent, suffix='.download', delete=False) as output:
                temp = Path(output.name)
                total = 0
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > 10 * 1024 * 1024:
                        raise ValueError('Download exceeded expected size limit')
                    output.write(chunk)
        verify(temp)
        temp.replace(TARGET)
        print('Downloaded and checksum-verified fictional pizza data. See data/PROVENANCE.md.')
    finally:
        if temp is not None and temp.exists():
            temp.unlink()

if __name__ == '__main__':
    main()
