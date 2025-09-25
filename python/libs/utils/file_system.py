import os
import glob

def get_files(str_glob: str) -> list[str]:
    """Retourne une liste de fichier correspondants à un glob en encapsulant
    `os.path.normpath` et `glob.glob`

    :param str str_glob: Glob à récupérer
    :return list[str]: Liste de fichiers correspondants au Glob donné
    """
    return [os.path.normpath(str_file_path) for str_file_path in glob.glob(str_glob)]
