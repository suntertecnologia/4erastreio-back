from src.utils.normalize_scrap_data import (
    normalize_accert,
    normalize_jamef,
    normalize_braspress,
    normalize_viaverde,
)

NORMALIZERS = {
    "accert": normalize_accert,
    "jamef": normalize_jamef,
    "braspress": normalize_braspress,
    "viaverde": normalize_viaverde,
}


def get_normalizer(transportadora: str):
    """
    Returns the normalizer function for the given transportadora.
    """
    normalizer_func = NORMALIZERS.get(transportadora.lower())
    if not normalizer_func:
        raise ValueError(f"Transportadora '{transportadora}' not supported.")
    return normalizer_func
