from kfp import dsl
import utils
import common


# Delete the runtime with given name, type (default type is alluxio) and namespace
@dsl.component(
    base_image=common.base_image,
    packages_to_install=[common.fluid_pysdk],
    target_image=common.target_image
)
def delete_runtime(
    runtime_name: str,
    namespace: str,
    runtime_type: str = "alluxio"
):
    """Component to delete a cache runtime.

    Args:
        runtime_name (str): Name of the cache runtime.
        namespace (str): Namespace of the cache runtime.
        runtime_type (str, optional): Type of the cache runtime. Must be one of ["alluxio", "jindo", "juicefs", "efc", "vineyard"]. Defaults to "alluxio".
    """
    import logging
    
    runtime_type = utils.convert_runtime_type(runtime_type)
    if runtime_type == None:
        logging.error(f"Failed to delete runtime \"{namespace}/{runtime_name}\" because argument runtime_type must be one of [\"alluxio\", \"jindo\", \"juicefs\", \"efc\", \"vineyard\"]")
        return
    
    from fluid import FluidK8sClient
    
    fluid_client = FluidK8sClient(namespace=namespace)
    fluid_client.delete_runtime(name=runtime_name, runtime_type=runtime_type, namespace=namespace, wait_until_cleaned_up=True)

    logging.info(f"Delete the runtime \"{namespace}/{runtime_name}\" successfully")
