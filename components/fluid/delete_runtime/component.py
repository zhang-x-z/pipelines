from kfp import dsl, compiler

# Delete the AlluxioRuntime
# TODO: How to delete runtime in new SDK?
@dsl.component(packages_to_install=['git+https://github.com/fluid-cloudnative/fluid-client-python.git'])
def delete_runtime(
    runtime_type: str,
    runtime_name: str,
    namespace: str
):
    import logging
    from fluid import FluidClient, ClientConfig
    
    fluid_client = FluidClient(ClientConfig())
    fluid_client.delete_runtime(name=runtime_name, namespace=namespace, runtime_type="alluxio", wait_until_cleaned_up=True)

    logging.info(f"Cleanup the AlluxioRuntime \"{namespace}/{runtime_name}\" successfully!")

if __name__ == '__main__':
    compiler.Compiler().compile(delete_runtime, "./component.yaml")