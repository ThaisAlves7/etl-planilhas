import yaml
from pydantic import BaseModel, ConfigDict, Field


class ConfigFonte(BaseModel):
    model_config = ConfigDict(extra="forbid")

    encoding: str = "latin-1"
    delimitador: str = ";"
    formatos_data: list[str] = Field(min_length=1)


def carregar_config(caminho: str) -> ConfigFonte:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = yaml.safe_load(arquivo)
    return ConfigFonte.model_validate(dados)
