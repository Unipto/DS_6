from typing import TypedDict
from plotly.graph_objects import Figure
import os

class ColumnInformations(TypedDict):
    """Objet retourné par les fonctions d'analyse de colonne

    :cvar str html: Code HTML correspondant à la colonne
    :cvar dict[str, Figure] plots: Dictionnaire ayant comme clé le chemin vers un
      fichier image, et en valeur le plot correspondant à l'image
    """
    html: str
    plots: dict[str, Figure]

def get_part(part_name: str, parameters: dict = {}) -> str:
    """Récupère le code HTML

    :param str part_name: Nom du fichier
    :param dict parameters: Dictionnaire avec en clé le mot-clé dans l'HTML et
        en valeur la valeur à insérer dans l'HTML
    :return str: Le bout de code HTML avec les mot-clés remplacés par leurs valeurs
    """
    str_part_code: str = ""
    str_part_path = os.path.join(os.path.dirname(__file__), "html_parts", f"{part_name}.html")
    with open(str_part_path, mode="r", encoding="utf-8") as f:
        str_part_code = f.read()
    
    for k,v in parameters.items():
        str_part_code = str_part_code.replace(f"%%{k}%%", str(v))

    return str_part_code

