from src.etl.extract.leitores import ler_csv


def test_ler_csv_adiciona_linha_origem(tmp_path):
    arquivo = tmp_path / "x.csv"
    arquivo.write_text("a;b\n1;2\n3;4\n", encoding="latin-1")

    df = ler_csv(str(arquivo))

    assert list(df["linha_origem"]) == [2, 3]
    assert df.loc[0, "a"] == "1"
