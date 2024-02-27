from kfp import dsl, compiler

# Preheat the dataset with specific dataset name and namespace
@dsl.component(packages_to_install=['git+https://github.com/fluid-cloudnative/fluid-client-python.git'])
def preheat_dataset(dataset_name: str, namespace: str):
    import logging
    from fluid import DataLoad, DataLoadSpec, FluidClient
    from kubernetes import client as k8s_client
    
    fluid_client = FluidClient()

    FLUID_GROUP = "data.fluid.io"
    FLUID_VERSION = "v1alpha1"

    dataload = DataLoad(
        api_version="%s/%s" % (FLUID_GROUP, FLUID_VERSION),
        kind="DataLoad",
        metadata=k8s_client.V1ObjectMeta(
            name="%s-loader" % dataset_name,
            namespace=namespace
        ),
        spec=DataLoadSpec(
            dataset={
                "name": dataset_name,
                "namespace": namespace
            }
        )
    )
    
    fluid_client.create_data_operation(data_op=dataload, wait=True)
    fluid_client.delete_data_operation(name="%s-loader" % dataset_name, data_op_type="dataload", namespace=namespace)
    logging.info(f"Load Dataset \"{namespace}/{dataset_name}\"  successfully!")

if __name__ == '__main__':
    compiler.Compiler().compile(preheat_dataset, "./component.yaml")