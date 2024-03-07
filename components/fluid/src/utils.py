from fluid import constants

legal_cache_medium = {"MEM", "SSD", "HDD"}

legal_runtime_type = {
    "alluxio": constants.ALLUXIO_RUNTIME_KIND,
    "jindo": constants.JINDO_RUNTIME_KIND,
    "juicefs": constants.JUICEFS_RUNTIME_KIND,
    "efc": constants.EFC_RUNTIME_KIND,
    # "vineyard": constants.VINEYARD_RUNTIME_KIND
}

def convert_runtime_type(runtime_type: str):
    return legal_runtime_type.get(runtime_type.lower())

def is_valid_cache_medium(cache_medium: str) -> bool:
    return cache_medium.upper() in legal_cache_medium