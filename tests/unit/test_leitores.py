import pandas as pd

from etl.extract.leitores import ler_excel


def test_ler_excel_pula_titulos_e_calcula_linha_de_origem(tmp_path):
    caminho = tmp_path / "x.xlsx"
    with pd.ExcelWriter(caminho) as xl:
        pd.DataFrame(
            [
                ["Relatório de vendas", None],
                ["gerado hoje", None],
                ["a", "b"],
                ["1", "2"],
                ["3", "4"],
            ]
        ).to_excel(xl, sheet_name="Vendas", header=False, index=False)

    df = ler_excel(str(caminho), nome_aba="Vendas", linhas_antes_do_cabecalho=2)

    assert list(df.columns[:2]) == ["a", "b"]
    assert list(df["linha_origem"]) == [4, 5]  # 2 títulos + cabeçalho na linha 3
