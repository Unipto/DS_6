import pandas as pd
import numpy as np

def bool_to_text(val: any) -> str | None:
    """Transforme une valeur boolish en texte (`"Oui"`/`"Non"`/`None`)

    :param any val: Une valeur boolish, c'est-à-dire pouvant être interprétée comme un bool
    
    :return str | None: Retourne `None` si la valeur passée est None
        sinon si la valeur est trueish alors `"Oui"`
        sinon `"Non"`

    """
    if val is None:
        return None
    elif val:
        return "Oui"
    else:
        return "Non"


def bytes_to_giga_bytes(val: None | int | float) -> float | None:
    """Convertit un bomre de bytes (octets) en GigaBytes (Giga-octets)
    en divisant par 1 milliard (`1000 * 1000 * 1000`)

    :param None | int | float val: Une valeur numérique ou `None`

    :return float | None: Retourne `None` si la valeur passée est `None`
        sinon retourne la valeur divisée par 1 milliard
    """
    if val is None:
        return None
    else:
        return val / (1000 * 1000 * 1000)


def bytes_to_mega_bytes(val: None | int | float) -> float | None:
    """Convertit un bomre de bytes (octets) en MegaBytes (Mega-octets)
    en divisant par 1 million (`1000 * 1000`)

    :param None | int | float val: Une valeur numérique ou `None`
    
    :return float | None: Retourne `None` si la valeur passée est None
        sinon retourne la valeur divisée par 1 million
    """
    if val is None:
        return None
    else:
        return val / (1000 * 1000)


def str_to_datetime64(str_input: str) -> np.datetime64:
    """Convertit un string en datetime

    :param str str_input: Datetime sous la forme d'un string
    :return np.datetime64: Le string sous forme de datetime
    """
    return pd.Timestamp(str_input).to_datetime64()