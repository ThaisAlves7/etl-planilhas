from hashlib import sha256


def calcular_hash(caminho: str) -> str:
    digest = sha256()
    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()
