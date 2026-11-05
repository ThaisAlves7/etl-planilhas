from pathlib import Path

import pytest
from pydantic import ValidationError

from etl.config import carregar_config

CONFIG = Path(__file__).parents[2] / "config" / "vendas.yaml"


def test_carrega_a_configuracao_da_fonte():
    cfg = carregar_config(str(CONFIG))

    assert cfg.encoding == "latin-1"
    assert cfg.delimitador == ";"
    assert "%d/%m/%Y" in cfg.formatos_data


def test_lista_de_formatos_de_data_nao_pode_ser_vazia(tmp_path):
    arquivo = tmp_path / "x.yaml"
    arquivo.write_text("formatos_data: []\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        carregar_config(str(arquivo))


def test_chave_desconhecida_na_configuracao_e_recusada(tmp_path):
    arquivo = tmp_path / "x.yaml"
    arquivo.write_text(
        "encodng: utf-8\nformatos_data: ['%Y-%m-%d']\n", encoding="utf-8"
    )

    with pytest.raises(ValidationError):
        carregar_config(str(arquivo))
