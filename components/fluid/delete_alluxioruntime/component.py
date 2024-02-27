from kfp import dsl, compiler

# Delete the AlluxioRuntime
@dsl.component(packages_to_install=['git+https://github.com/fluid-cloudnative/fluid-client-python.git'])
def delete_alluxioruntime(dataset_name: str, namespace: str):
    import logging
    from fluid import FluidClient
    
    fluid_client = FluidClient()
    fluid_client.delete_runtime(name=dataset_name, namespace=namespace, runtime_type="alluxio", wait_until_cleaned_up=True)

    logging.info(f"Cleanup the AlluxioRuntime \"{namespace}/{dataset_name}\" successfully!")

if __name__ == '__main__':
    compiler.Compiler().compile(delete_alluxioruntime, "./component.yaml")