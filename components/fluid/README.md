# Fluid Pipline Components

Organization: Fluid

Organization Description: Fluid is an open source Kubernetes-native Distributed Dataset Orchestrator and Accelerator for data-intensive applications, such as big data and AI applications.

Version information: Fluid Pipline Components v0.0.1, used Fluid Client Python SDK 1.0.0

Test status: Currently manual tests

Owners information:

## Usage

Fluid pipline components provide various component to interact with Fluid. Currently we provide the following components:
- Create Dataset
- Bind Dataset to Runtime
- Delete Dataset
- Delete Runtime
- Migrate Dataset
- Preload Dataset

Users can load the component like:
```python
from kfp import components

create_dataset_comp = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/master/components/fluid/src/component_metadata/create_dataset.yaml')
```

You can find all of the compiled IR YAML files from [here](https://github.com/kubeflow/pipelines/tree/master/components/fluid/src/component_metadata).

### Create Dataset
Component to create a Dataset.
#### Arguments
- `dataset_name` _str_ - Name of the Dataset.
- `namespace` _str_ - Namespace of the Dataset.
- `mount_point` _str_ - Mount point of the source. E.g. use `s3://your-bucket` to mount a S3 bucket.
- `options` _dict_ - Options which can be used in cache runtime. Defaults to None.
  
  E.g. you can set Alluxio configurations in this field if you will bind this Dataset to AlluxioRuntime:
  ```python
  options = {
      "alluxio.underfs.s3.endpoint": "https://your-s3-endpoint",
      "alluxio.underfs.s3.endpoint.region": "your-s3-region"
  }
  ``` 
- `cred_secret_name` _str, optional_ - Name of the secret which is used to access external storage (e.g. S3). Defaults to None.
- `cred_secret_options` _dict, optional_ - Contents in secret `<cred_secret_name>`. Defaults to None.
  
  E.g. If you create a secret to access S3 with AlluxioRuntime like:
  ```yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: s3-secret
  stringData:
    s3-accessKeyId: <your-access-key-id>
    s3-secretKey: <your-secret-key>
  ```
  You should set `cred_secret_name` and `cred_secret_options` to:
  ```python
  cred_secret_name = "s3-secret"
  cred_secret_options = {
      "s3a.accessKeyId": "s3-accessKeyId",
      "s3a.secretKey": "s3-secretKey"
  }
  ```
  Note that you should set `cred_secret_name` and `cred_secret_options` together.
- `mount_path` _str, optional_ - Path to mount in cache runtime. When this field is None, the mount path will be set to `/<mount_name>`. Defaults to None.
- `mount_name` _str, optional_ - Name of this mount. When this field is None, it will be set to `dataset_name`. Defaults to None.
- `mode` _str, optional_ - Mode of this Dataset. Must be one of ["ReadOnly", "ReadWrite"]. Defaults to "ReadOnly".

### Bind Dataset to Runtime
Component to bind a Dataset to a cache runtime. The given Dataset must be created before.
#### Arguments
- `dataset_name` _str_ - Name of the Dataset which need to bind to a cache runtime.
- `namespace` _str_ - Namespace of the Dataset which need to bind to a cache runtime.
- `cache_capacity` _float_ - Cache capacity (GiB) of one cache runtime worker.
- `runtime_type` _str, optional_ - Type of the cache runtime.
  Must be one of ["alluxio", "jindo", "juicefs", "efc", "vineyard"]. Defaults to "alluxio".
- `cache_medium` _str, optional_ - Cache medium type used in cache runtime workers.
  Must be one of ["MEM", "SSD", "HDD"]. Defaults to "MEM".
- `replicas` _int, optional_ - Number of cache runtime workers. Defaults to 1.

### Delete Dataset
Component to delete a Dataset.
#### Arguments
- `dataset_name` _str_ - Name of the Dataset.
- `namespace` _str_ - Namespace of the Dataset.

### Delete Runtime
Component to delete a cache runtime.
#### Arguments
- `runtime_name` _str_ - Name of the cache runtime.
- `namespace` _str_ - Namespace of the cache runtime.
- `runtime_type` _str, optional_ - Type of the cache runtime. Must be one of ["alluxio", "jindo", "juicefs", "efc", "vineyard"]. Defaults to "alluxio".

### Migrate Dataset
Component to migrate a Dataset.
#### Arguments
- `dataset_name` _str_ - Name of the Dataset.
- `namespace` _str_ - Namespace of the Dataset.
- `migrate_path` _str_ - Path to be migrated.
- `migrate_direction` _str_ - The direction of migration. Must be either "from" or "to". "from" means migrate from external storage to the Dataset. "to" means migrate from the Dataset to external storage.
- `external_storage_uri` _str_ - External storage uri used for migration.
- `external_storage_encrypt_options` _dict_ - Encrypt options used to access the external storage. Defaults to None.

### Preload Dataset
Component to preload the Dataset.
#### Arguments
- `dataset_name` _str_ - Name of the Dataset.
- `namespace` _str_ - Namespace of the Dataset.
- `target_path` _str, optional_ - Path which needs to preload data, both directory and file path are supported. Defaults to "/".
  Note that the path is relative to the Dataset's mount path.
  For example, when mounting `s3://bucket/path` to the Dataset's root path (`/`), you preloads `s3://bucket/path/dir` by set this field to `/dir`.
- `load_metadata` _bool, optional_ - Whether to load metadata. Defaults to False.
