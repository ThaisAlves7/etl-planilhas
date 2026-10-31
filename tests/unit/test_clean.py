import pandas as pd
from etl.transform.clean import vazio_para_nulo


def test_vazio_e_espacos_viram_nulo():
    df = pd.DataFrame({"nome": ["Ana", "", " "]})
    out = vazio_para_nulo(df, ["nome"])
    assert out["nome"].isna().tolist() == [False, True, True]
