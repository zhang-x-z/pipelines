from kfp import dsl, components, kubernetes, compiler

# Load Fluid components
# TODO: need to change the location of these component yaml files.
create_s3_dataset = components.load_component_from_file('./component-yaml/create-s3-dataset.yaml')
create_alluxioruntime = components.load_component_from_file('./component-yaml/create-alluxioruntime.yaml')
preheat_dataset = components.load_component_from_file('./component-yaml/preheat-dataset.yaml')
delete_dataset = components.load_component_from_file('./component-yaml/cleanup-dataset-and-alluxioruntime.yaml')
delete_alluxioruntime = components.load_component_from_file('./component-yaml/cleanup-dataset-and-alluxioruntime.yaml')

# The component to train a simple CNN with FashionMNIST
# In production environment, you'd better not to use packages_to_install,
# since the KFP SDK will install these dependencies at task runtime.
# More details in https://www.kubeflow.org/docs/components/pipelines/v2/components/containerized-python-components/
@dsl.component(
    base_image='bitnami/pytorch:2.1.2',
    packages_to_install=['pandas']
)
def train_and_test_cnn(dataset_name: str, data_root_path: str, batch_size: int, epochs: int, learning_rate: float):
    import logging

    logging.info("Training a simple CNN...")

    import os
    import pandas as pd
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.init as init
    from torchvision import transforms
    from torch.utils.data import DataLoader, Dataset, random_split   

    dataset_path = os.path.join(data_root_path, dataset_name)
    logging.info("Dataset file location: " + dataset_path)

    # Check Dataset Path
    logging.info("Check dataset")
    for dirname, _, filenames in os.walk(dataset_path):
        for filename in filenames:
            logging.info(os.path.join(dirname, filename))
    
    # Prepare Data
    logging.info("Start load dataset...")
    train_data=pd.read_csv(f"{dataset_path}/fashion-mnist_train.csv")
    test_data=pd.read_csv(f"{dataset_path}/fashion-mnist_test.csv")
    logging.info("Load dataset successfully!")

    class CustomDataset(Dataset):

        def __init__(self,dataframe,transform=None):
            self.dataframe=dataframe
            self.transform=transform


        def __len__(self):

            return len(self.dataframe)
    
        def __getitem__(self,idx):
            label = self.dataframe.iloc[idx, 0]
            image_data = self.dataframe.iloc[idx, 1:].values.astype('uint8').reshape((28, 28, 1))

            if(self.transform):
                image=self.transform(image_data)

            return image,label
    
    transform = transforms.Compose([transforms.ToTensor()])

    train_dataset=CustomDataset(train_data,transform=transform)
    test_dataset=CustomDataset(test_data, transform=transform)
    
    train_size=int(0.8*len(train_dataset))
    valid_size=len(train_dataset)-train_size

    train_dataset,valid_dataset=random_split(train_dataset,[train_size,valid_size])
    train_loader=DataLoader(train_dataset,batch_size=batch_size,shuffle=True)
    valid_loader=DataLoader(valid_dataset,batch_size=batch_size)
    test_loader=DataLoader(test_dataset,batch_size=batch_size)
    
    # Build a simple CNN
    class CNN(nn.Module):

        def __init__(self,num_classes):
            super(CNN, self).__init__()
            self.feature = nn.Sequential(
                nn.Conv2d(1,24,kernel_size=3,padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2),
                nn.Conv2d(24,128,kernel_size=3,padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2)
            )
            self.classifier = nn.Sequential(
                nn.Linear(128*7*7,48),
                nn.ReLU(inplace=True),
                nn.Linear(48,num_classes)
            )

        def forward(self,x):
            x = self.feature(x)
            x = x.view(x.size(0),-1)
            x = self.classifier(x)
            return x 
    
    # Train this CNN
    def train(model,train_loader,optimizer,criterion, device):
        model.train()
        train_loss=0
        correct=0
        total=0

        for images,labels in train_loader:
            images,labels =images.to(device),labels.to(device)

            optimizer.zero_grad()
            outputs=model(images)
            loss=criterion(outputs,labels)
            loss.backward()
            optimizer.step()

            train_loss+=loss.item()
            _,predicted=outputs.max(1)
            total+=labels.size(0)
            correct+=predicted.eq(labels).sum().item()

        train_accuracy=100*correct/total
        train_loss/=len(train_loader)
        return train_loss,train_accuracy
    
    def validate(model,valid_loader,criterion,device):
        model.eval()
        val_loss=0
        correct=0
        total=0

        with torch.no_grad():
            for images,labels in valid_loader:
                images,labels=images.to(device),labels.to(device)

                outputs=model(images)
                loss=criterion(outputs,labels)

                val_loss+=loss.item()
                _,predicted=outputs.max(1)
                total+=labels.size(0)
                correct+=predicted.eq(labels).sum().item()

            val_accuracy = 100.0 * correct / total
            val_loss /= len(valid_loader)
        return val_loss, val_accuracy

    def test(model, test_loader, device):
        model.eval()
        correct=0
        total=0
        
        with torch.no_grad():
            for images,labels in test_loader:
                images,labels=images.to(device),labels.to(device)
                
                outputs=model(images)
                _,predicted=outputs.max(1)
                total+=labels.size(0)
                correct+=predicted.eq(labels).sum().item()

            test_accuracy = 100.0 * correct / total
        
        return test_accuracy
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cnn = CNN(10).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(cnn.parameters(),lr=learning_rate)

    train_accuracy=[]
    validation_accuracy=[]
    train_losses=[]
    validation_losses=[]

    logging.info("Begin training...")
    for epoch in range(epochs):
        train_loss, train_acc = train(cnn, train_loader, optimizer, criterion, device)
        val_loss, val_acc = validate(cnn, valid_loader, criterion, device)

        train_accuracy.append(train_acc)
        validation_accuracy.append(val_acc)
        train_losses.append(train_loss)
        validation_losses.append(val_loss)


        logging.info(f"Epoch {epoch+1}/{epochs}: Train Loss: {train_loss:.4f}, Validation Loss: {val_loss:.4f} Train Accuracy: {train_acc:.2f}%, Validation Accuracy: {val_acc:.2f}%")
    
    logging.info("Test the CNN...")
    test_acc = test(cnn, test_loader, device)
    logging.info(f"Final Test Accuracy: {test_acc:.2f}%")

@dsl.pipeline(name='train-and-test-cnn-for-fashion-mnist')
def train_and_test_cnn_for_fashion_mnist_pipeline(dataset_name: str, namespace: str, s3_endpoint: str, s3_region: str, mount_point: str, batch_size: int, epochs: int, learning_rate: float):
    # dataset's mount path when training
    mount_path = '/datasets'
    # prepare dataset
    create_dataset_op = create_s3_dataset(dataset_name=dataset_name, namespace=namespace, mount_point=mount_point, mount_s3_endpoint=s3_endpoint, mount_s3_region=s3_region)
    create_alluxioruntime_op = create_alluxioruntime(dataset_name=dataset_name, namespace=namespace)
    preheat_dataset_op = preheat_dataset(dataset_name=dataset_name, namespace=namespace)
    # disable caching
    create_dataset_op.set_caching_options(False)
    create_alluxioruntime_op.set_caching_options(False)
    preheat_dataset_op.set_caching_options(False)
    # train cnn
    train_and_test_cnn_op = train_and_test_cnn(dataset_name=dataset_name, data_root_path=mount_path, batch_size=batch_size, epochs=epochs, learning_rate=learning_rate)
    train_and_test_cnn_op.set_caching_options(False)
    # mount dataset pvc to training component
    kubernetes.mount_pvc(task=train_and_test_cnn_op, pvc_name=dataset_name, mount_path=mount_path)
    # define components' dependence
    create_alluxioruntime_op.after(create_dataset_op)
    preheat_dataset_op.after(create_alluxioruntime_op)
    train_and_test_cnn_op.after(preheat_dataset_op)
    # delete dataset and alluxio runtime
    delete_alluxioruntime_op = delete_alluxioruntime(dataset_name=dataset_name, namespace=namespace)
    delete_alluxioruntime_op.set_caching_options(False)
    delete_alluxioruntime_op.after(train_and_test_cnn_op)
    delete_alluxioruntime_op.ignore_upstream_failure()
    delete_dataset_op = delete_dataset(dataset_name=dataset_name, namespace=namespace)
    delete_dataset_op.set_caching_options(False)
    delete_dataset_op.after(delete_alluxioruntime_op)

if __name__ == '__main__':
    # Compile into IR YAML
    compiler.Compiler().compile(
        train_and_test_cnn_for_fashion_mnist_pipeline, 
        'train-and-test-cnn-for-fashion-mnist-pipline.yaml')