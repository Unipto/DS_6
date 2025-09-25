import pandas as pd
import numpy as np
import plotly.express as px
from itertools import combinations
import joblib
from scipy.stats.contingency import association
import time
from typing import List, Tuple
import gc

MAX_CONTINGENCY_CELLS = int(20_000_000) # Taille maximale acceptée pour la table de contingence



def draw_correlation_heatmap(corr_matrix:pd.DataFrame, title:str=None, mask_top:bool=True, **plot_params):
    '''Affiche une heatmap correspondant à une matrice de corrélation donnée.

    :param pd.DataFrame corr_matrix: Matrice de corrélation visualiser.
    '''
    if mask_top:
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        corr_matrix = corr_matrix.mask(mask)
    fig = px.imshow(corr_matrix, title=title, **plot_params)
    fig.show()

################################################################################
#                                                                              #
#          MARK: Calcul de l'association de chaque paire de colonnes           #
#                                                                              #
################################################################################

def _assoc_from_codes_safe(codes_a, codes_b, col_a=None, col_b=None, verbose=False):
    """Calcule l'association entre deux colonnes. Cette fonction utilise des codes numériques pour représenter les modalités des colonnes
    afin d'optimiser les calculs. Elle gère les NaN (-1) et les tailles de tables de contingence maximales.

    :param codes_a np.ndarray: Tableau de codes pour la première colonne.
    :param codes_b np.ndarray: Tableau de codes pour la deuxième colonne.
    :param col_a str, optional: Nom de la première colonne. Defaults to None.
    :param col_b str, optional: Nom de la deuxième colonne. Defaults to None.

    :return float: L'association entre les deux colonnes, ou NaN si l'association n'est pas
               possible (taille de table de contingence trop petite, valeurs manquantes, etc.).
    """
    try:
        # Masquer les NaN (-1)
        mask = (codes_a != -1) & (codes_b != -1)
        if mask.sum() == 0:
            return np.nan

        a = codes_a[mask]
        b = codes_b[mask]

        # Remapper les modalités observées à 0..k-1 pour éviter lignes/colonnes vides
        uniq_a = np.unique(a)
        uniq_b = np.unique(b)
        na = int(uniq_a.size)
        nb = int(uniq_b.size)

        # Vérifier taille de la table de contingence
        n_cells = na * nb
        if n_cells <= 0 or n_cells > MAX_CONTINGENCY_CELLS:
            if verbose:
                print(f"INFO - Paire {col_a} - {col_b} ignorée car la taille de la table de contingence {n_cells} dépasse la taille maximale permise (na={na}, nb={nb})")
            return np.nan

        # Remapping vectorisé : searchsorted sur les uniques triés
        ia = np.searchsorted(uniq_a, a) # Evite les loops inneficaces
        ib = np.searchsorted(uniq_b, b)

        idx = ia * np.int64(nb) + ib
        if np.any(idx < 0):
            print(f"WARNING - Indices négatifs pour la paire {col_a}-{col_b}; skipping")
            return np.nan

        cont = np.bincount(idx, minlength=int(n_cells)).reshape((na, nb))

        # Si la table est dégénérée (pas au moins 2x2), on ne peut pas calculer l'association
        if cont.shape[0] < 2 or cont.shape[1] < 2:
            if verbose:
                print(f"INFO - Pas assez de catégories après filtrage pour la paire {col_a} - {col_b}: shape={cont.shape}")
            return np.nan

        # Calculer l'association en capturant les erreurs/scipy warnings
        try:
            val = float(association(cont))
        except Exception as e:
            print(f"WARNING - Erreur dans association() pour la paire {col_a}-{col_b} ayant une table de contingence de taille {cont.shape}: {e}")
            return np.nan

        if np.isnan(val) or np.isinf(val):
            return np.nan
        return val

    except OverflowError as e:
        print(f"ERROR - OverflowError lors du calcul de l'association pour {col_a} - {col_b}: {e}")
        return np.nan
    except ValueError as e:
        print(f"ERROR - ValueError lors du calcul de l'association pour {col_a} - {col_b}: {e}")
        return np.nan
    except MemoryError as e:
        print(f"ERROR - MemoryError lors du calcul de l'association pour {col_a} - {col_b}: {e}")
        return np.nan
    except Exception as e:
        print(f"ERROR - Erreur inattendue lors du calcul de l'association pour {col_a} - {col_b}: {e}")
        return np.nan


def _chunk_pairs(pairs: List[Tuple[str, str]], chunk_size: int) -> List[List[Tuple[str, str]]]:
    """Divise une liste de paires de colonnes en morceaux de taille fixe.

    :param List[Tuple[str, str]] pairs: Liste de paires de colonnes à diviser.
    :param int chunk_size: Taille de chaque morceau.

    returns: List[List[Tuple[str, str]]]: Liste de listes, où chaque sous-liste contient une portion des paires.
    """
    return [pairs[i:i + chunk_size] for i in range(0, len(pairs), chunk_size)]

def get_association_table(
    df: pd.DataFrame,
    max_workers: int = 100, # Nombre élevé pour forcer à utiliser tous les threads dispos
    unique_threshold_ratio: float = 0.95, # 1 = pas de filtrage par rapport au nombre de 
    batch_size: int = 500,
    verbose: bool = False
) -> pd.DataFrame:
    """Retourne une table d'association entre colonnes.

    :param int max_workers: nombre de threads (utiliser threading backend pour éviter copie mémoire)
    :param float unique_threshold_ratio: seuil pour filtrer colonnes à forte cardinalité (comme avant)   
    :param int batch_size: Nombre de paires traitées par lot (diminue la mémoire si petit)
    :param bool verbose: si True, affiche logs info/warning/temps d'exécution

    :returns pd.DataFrame: DataFrame d'association (index/colonnes = colonnes valides)
    """

    start_all = time.perf_counter()
    if verbose:
        print("INFO - Démarrage get_association_table")

    # Sélection des colonnes pertinentes
    object_columns = df.columns.tolist()

    # Filtrer les colonnes avec trop de modalités avant parallélisme
    valid_cols = []
    for c in object_columns:
        nunq = df[c].dropna().nunique()
        if nunq <= unique_threshold_ratio * df.shape[0]:
            valid_cols.append(c)
        else:
            if verbose:
                print(f"INFO - Colonne '{c}' ignorée (nuniques={nunq} > threshold={unique_threshold_ratio})")

    if len(valid_cols) < 2:
        if verbose:
            print("INFO - Pas assez de colonnes valides pour calculer des associations.")
        return pd.DataFrame(index=valid_cols, columns=valid_cols, dtype=float)

    # Convertir en category pour compresser et extraire codes
    codes = {}
    for c in valid_cols:
        # Faire une conversion inplace contrôlée
        ser_categories = df[c].astype('category')
        codes[c] = ser_categories.cat.codes.values  # conversion en valeur numérique, numpy array, -1 = NaN

    association_table = pd.DataFrame(index=valid_cols, columns=valid_cols, dtype=float)

    pairs = list(combinations(valid_cols, 2))
    if verbose:
        print(f"INFO - Nombre de colonnes valides: {len(valid_cols)}, nombre de paires: {len(pairs)}")

    # Découper en lots pour contrôler la charge mémoire et suivre le progrès
    chunks = _chunk_pairs(pairs, batch_size)
    total_pairs = len(pairs)
    processed_pairs = 0
    n_jobs = max(1, min(max_workers, joblib.cpu_count()))

    for idx, chunk in enumerate(chunks, 1):
        t0 = time.perf_counter()
        if verbose:
            print(f"INFO - Traitement lot {idx}/{len(chunks)} : {len(chunk)} paires (workers={n_jobs}).")
            
        # Lance le calcul en threading pour éviter la sérialisation du DataFrame
        results = joblib.Parallel(n_jobs=n_jobs, backend='threading')(
            joblib.delayed(_assoc_from_codes_safe)(codes[a], codes[b], a, b, verbose)
            for a, b in chunk
        )

        # Affectation des résultats
        for (a, b), val in zip(chunk, results):
            association_table.loc[a, b] = val
            association_table.loc[b, a] = val

        processed_pairs += len(chunk)
        t1 = time.perf_counter()
        if verbose:
            print(f"INFO - Lot {idx} terminé en {(t1 - t0):.2f}s. Paires traitées: {processed_pairs}/{total_pairs}.")

        # Nettoyage mémoire entre lots
        del results
        gc.collect()

    # Diagonale (1.0 pour association parfaite avec soi-même)
    np.fill_diagonal(association_table.values, 1.0)

    total_time = time.perf_counter() - start_all
    if verbose:
        print(f"INFO - Terminé. Temps total: {total_time:.2f}s.")

    return association_table


def check_col_format(df: pd.DataFrame, str_col: str, reg_pat:str) -> None|pd.DataFrame:
    """Vérifie qu'une colonne de dtype 'string' ou 'object' respecte un format donnée.

    :param pd.DataFrame df: DataFrame contenant la colonne à analyser.
    :param str str_col: Nom de la colonne à analyser
    :param str reg_pat: Pattern regex à respecter
    :return None|pd.DataFrame: Si tous les éléments de la colonne respecte le format, rien n'est retourné/
    Dans le cas contraire, les lignes du dataframe qui ne respectent pas le format sont retournées.
    """
    ser = df[str_col].copy()

    if ser.dtype not in ("string", "object", "category"):
        raise TypeError(f"La colonne '{str_col}' doit être de dtype 'string' ou 'object'.")
    
    ser_mask = df[str_col].str.match(reg_pat)
    n_matches = ser_mask.sum()
    if n_matches == df.shape[0]:
        print(f"Le format '{reg_pat}' est tout le temps respecté dans la colonne '{str_col}'.")
        return None
    
    print(f"Le format '{reg_pat}' n'est pas respecté {df.shape[0] - n_matches} fois dans la colonne '{str_col}'.")
    return df.loc[~ser_mask]