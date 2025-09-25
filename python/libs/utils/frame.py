from typing import Callable
import pandas as pd
import ast


def transform_column_names(df: pd.DataFrame, fn: Callable[[str], str]) -> pd.DataFrame:
    """Transforme les noms de colonnes d'un DataFrame en les passants dans une \
        fonction
    
    :param pd.DataFrame df: DataFrame à transformer
    :param Callable fn: Fonction prenant un string en paramètres et en retournant un
    :return pd.DataFrame: Le dataframe transformé
    """
    return df.rename(columns={str_col: fn(str_col) for str_col in df.columns})


def apply_to_col(df: pd.DataFrame, fn: Callable, arr_cols: list[str] = None) -> pd.DataFrame:
    """Applique une fonction à une liste de colonne d'un dataframe

    :param pd.DataFrame df: Le dataframe sur lequel appliqué la fonction
    :param Callable fn: Fonction à appliquer
    :param Optional[list[str]] arr_cols: Liste des colonnes auxquelles appliquer la fonction.
        Si la liste est vide, la fonction sera appliquée à toutes les colonnes
    
    :return pd.Dataframe: Le dataframe transformé
    """
    if arr_cols is None:
        arr_cols = df.columns()

    if len(arr_cols) == 0:
        arr_cols = df.columns()

    for str_col in arr_cols:
        df[str_col] = df[str_col].apply(fn)

    return df


def expand_dict(df: pd.DataFrame, arr_cols: list[str], renamer: dict | str = "") -> pd.DataFrame:
    """Étend une colonne de dictionnaire en rajoutant un préfixe à chaque colonne \
        ou en n'extrayant que certaines colonnes

    :param pd.DataFrame df: Dataframe à transporter
    :param list[str] arr_cols: Liste des colonnes à développer
    :param Optional[dict | str] renamer: Préfixe à ajouter à chaque colonne ou
        dictionnaire mappant un nom de propriété à celui d'une colonne, defaults to `""`
    
    :return pd.DataFrame: Le dataframe transformé
    """
    def get_value(dct_input: dict | None, str_key: str) -> any:
        """Récupère la valeur d'un dictionnaire pour une clé donnée. Si le dictionnaire \
        est `None` ou si la clé n'est pas dans le dictionnaire, retourne `None`

        :param dict | None dct_input: Dictionnaire à parcourir
        :param str str_key: Clé à chercher
        :return any: Valeur dans le dictionnaire pour la clé donnée
        """
        if pd.isna(dct_input):
            return None

        if dct_input is None:
            return None

        if str_key not in dct_input:
            print(f"WARNING: {str_key} not in {dct_input}")
            return None

        return dct_input[str_key]

    for str_col in arr_cols:
        if isinstance(renamer, str):
            df = pd.concat(
                [
                    df,
                    df[str_col].apply(lambda x: pd.Series(x).add_prefix(renamer))
                ],
                axis=1
            )
        else:
            for str_src_col, str_dst_col in renamer.items():
                df[str_dst_col] = df[str_col].apply(lambda x: get_value(x, str_src_col))

    df = df.drop(columns=arr_cols)
    return df


def expand_class_instance(df: pd.DataFrame, arr_cols: list[str], renamer: dict | str = "") -> pd.DataFrame:
    """Wrapper de expand_dict. Étend une colonne contenant un string décrivant une instance de classe avec des paramètres en \
    rajoutant un préfixe à chaque colonne ou en n'extrayant que certaines colonnes

    :param pd.DataFrame df: Dataframe à transporter
    :param list[str] arr_cols: Liste des colonnes à développer
    :param Optional[dict | str] renamer: Préfixe à ajouter à chaque colonne ou
        dictionnaire mappant un nom de propriété à celui d'une colonne, defaults to `""`
    
    :return pd.DataFrame: Le dataframe transformé
    """
    def convert_to_dict(str_input: str | None) -> dict:
        """Convertit un string contenant une instance de classe avec de paramètres en un dictionnaire. Si le string \
        est `None` ou si la clé n'est pas dans le dictionnaire, retourne `None`
        Exemple: "DeviceType(family='iPod', brand='Apple', model='iPod')" -> {'family':'iPod', 'brand':'Apple', 'model':'iPod'}

        :param str | None str_input: String à traiter
        :return dict: Ensemble des paramètre de l'instance convertie en dictionnaire
        """
        if pd.isna(str_input):
            return None

        if str_input is None:
            return None
        
        int_start = str_input.find('(')
        int_end = str_input.rfind(')')
        if int_start > int_end:
            return None
        
        ast_expr = ast.parse(str_input, mode='eval').body
        if not isinstance(ast_expr, ast.Call):
            raise ValueError("Not a call expression")

        dict_params = {kw.arg: ast.literal_eval(kw.value) for kw in ast_expr.keywords}

        return dict_params
    
    for str_col in arr_cols:
        df[str_col] = df[str_col].map(convert_to_dict)

    return expand_dict(df=df, arr_cols=arr_cols, renamer=renamer)