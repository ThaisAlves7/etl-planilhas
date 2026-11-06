import hashlib

from etl.extract.arquivo import calcular_hash


def test_hash_depende_do_conteudo_e_nao_do_nome(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_bytes(b"x;y\n1;2\n")
    b.write_bytes(b"x;y\n1;2\n")

    assert calcular_hash(str(a)) == calcular_hash(str(b))

    b.write_bytes(b"x;y\n1;3\n")
    assert calcular_hash(str(a)) != calcular_hash(str(b))


def test_hash_confere_com_o_sha256_conhecido(tmp_path):
    arquivo = tmp_path / "abc.txt"
    arquivo.write_bytes(b"abc")

    assert calcular_hash(str(arquivo)) == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_hash_de_arquivo_maior_que_um_bloco(tmp_path):
    dados = b"x" * (3 * 1024 * 1024 + 17)
    arquivo = tmp_path / "grande.bin"
    arquivo.write_bytes(dados)

    assert calcular_hash(str(arquivo)) == hashlib.sha256(dados).hexdigest()
