import os
import pandas as pd

from .commons import get_part
from .part_string import analyse_string
from .part_datetime import analyse_datetime
from .part_numeral import analyse_numeral
from .part_default import analyse_default

def analyze_dataframe(df: pd.DataFrame, output_dir: str = "analyzer", output_name: str = "index"):
    """Génère une page HTML avec quelques analyses rudimentaires sur un dataframe

    :param pd.DataFrame df: Dataframe à analyser
    :param str, optional output_dir: Nom du dossier d'output, defaults to "analyzer"
    :param str, optional output_name: Nom du fichier d'output, defaults to "index"
    """
    str_output = ""
    arr_cols = df.columns
    dct_types = df.dtypes
    for str_col in arr_cols:
        str_type_name = str(dct_types[str_col]).lower()

        if str_type_name == "string":
            str_output += analyse_string(df[str_col])
        elif (
            str_type_name.startswith("datetime") or
            str_type_name.startswith("timestamp")
        ):
            str_output += analyse_datetime(df[str_col], str(dct_types[str_col]))
        elif (
            str_type_name.startswith("int") or
            str_type_name.startswith("float")
        ):
            str_output += analyse_numeral(df[str_col], str(dct_types[str_col]))
        else:
            str_output += analyse_default(df[str_col], str(dct_types[str_col]))

        str_output += "<hr>"
    

    df_desc = pd.concat([
        pd.DataFrame(df.columns, columns=["Colonnes"]),
        df.count().reset_index().rename(columns={0: "Nb Non-Null"})["Nb Non-Null"],
        df.dtypes.reset_index().rename(columns={0: "dtype"})["dtype"]
    ], axis=1)
        

    if os.path.exists(os.path.join(output_dir, f"{output_name}.html")):
        os.remove(os.path.join(output_dir, f"{output_name}.html"))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(os.path.join(output_dir, f"{output_name}.html"), mode="w", encoding="utf-8") as f:
        f.write(
            get_part(
                "main",
                {
                    "TITLE": output_name,
                    "DESCRIBE": df_desc.to_html(index=False, border=0, justify="inherit", classes="table table-sm table-hover"),
                    "ROW_COUNT": df.shape[0],
                    "COL_COUNT": df.shape[1],
                    "CONTENT": str_output
                }
            )
        )
