# Containerized Python API Template repository

Learn how to create a container and package it with GitHub Actions. This repository template gives you a good starting point for a Dockerfile, GitHub Actions workflow, and Python code.


## Learn objectives

* Containerize a Python application that uses FastAPI
* Use automation to deploy it to the cloud
* Setup GitHub Action to authenticate to Azure
* Automatically push new changes
* Debug cloud deployment 


## Deploy your API to the Azure Cloud

This deployment can be done at no cost, using free resources with an Azure subscription. Use one of these to deploy it:

- [Sign in to your account]()
- [Create a (no Credit Card required) Azure For Students account]()
- [Create a new Azure account]()


## Create an Azure App Service

1. Open an [Azure Cloud Shell](https://shell.azure.com/?WT.mc_id=academic-0000-alfredodeza) to use the `az` cli
1. Create a *Resource Group*:
```
az group create --name demo-fastapi --location "East US"
```
1. Create the **FREE** App Service Plan:
```
az appservice plan create --name "demo-fastapi" --resource-group demo-fastapi --is-linux --sku FREE
```
1. Create a random identifier for a unique webapp name:
```
let "randomIdentifier=$RANDOM*$RANDOM"
```
1. Create the web app with a placeholder container using the `randomIdentifier` from before
```
az webapp create --name "demo-fastapi-$randomIdentifier" --resource-group demo-fastapi --plan demo-fastapi --deployment-container-image mcr.microsoft.com/appsvc/staticsite:latest
```
1. Head to the [App Service](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites) and confirm that your service is up and running


## Create a Deployment profile

Run the following command with the `az` cli:

```
az webapp deployment list-publishing-profiles --resource-group demo-fastapi --name demo-fastapi --xml
```

Capture the output and add it as a [repository secret](/../../settings/secrets/actions/new) with the name `AZURE_WEBAPP_PUBLISH_PROFILE`


## Create an Azure Service Principal

You'll need the following:

1. An Azure subscription ID [find it here](https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBlade) or [follow this guide](https://docs.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id)
1. A Service Principal with the following details the AppID, password, and tenant information. Create one with: `az ad sp create-for-rbac -n "REST API Service Principal"` and assign the IAM role for the subscription. Alternatively set the proper role access using the following command (use a real subscription id and replace it):

```
az ad sp create-for-rbac --name "CICD" --role contributor --scopes /subscriptions/$AZURE_SUBSCRIPTION_ID --sdk-auth
``` 

Capture the output and add it as a [repository secret](/../../settings/secrets/actions/new) with the name `AZURE_CREDENTIALS`

## Generate a PAT

The access token will need to be added as an Action secret. [Create one](https://github.com/settings/tokens/new?description=Azure+Container+Apps+access&scopes=write:packages) with enough permissions to write to packages. If you follow the link, it should have everything pre-selected.

Capture the output and add it as a [repository secret](/../../settings/secrets/actions/new) with the name `PAT`

## Update workflow file

Now that you have everything created, you need to update the [.github/workflows/main.yml](/../../edit/main/.github/workflows/main.yml) file and add:

- `AZURE_WEBAPP_NAME`
- `AZURE_GROUP_NAME`

## Test locally

Make sure that everything runs locally. This repository is Codespaces-enabled that has already installed the `requirements.txt` file for you. To run the application, go to the `webapp/` directory and run:

```
uvicorn --host 0.0.0.0 main:app
```

You should see output like:

```
INFO:     Started server process [5579]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

The site will be available at the host's port 8000. Try out the API by going to `/docs`. 

If in a Codespace, you will get a notification in VSCode that the site is available. Otherwise look at the ports available for the application and click on port `8000`

## Deploy

Before continuing, check the following:

1. You have a PAT (Personal Access Token) saved as a [repository secret](/../../settings/secrets/)
1. You've created an Azure Service Principal and saved it as a [repository secret](/../../settings/secrets/) as `AZURE_CREDENTIALS`
1. You've saved the XML for the publish profile and saved it as a [repository secret](/../../settings/secrets/) as `AZURE_WEBAPP_PUBLISH_PROFILE`
1. You've created an [App Service](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites) with a valid name and the site is already available with the default static content

To deploy:

1. Go to [repository actions](/../../actions/workflows/main.yml) and click on _Run workflow_ and then the green button to run it.

**Deploying can take a couple of minutes**. Make sure you tail the logs in the Azure cloud shell to check the progress:

```
az webapp log tail --name $AZURE_WEBAPP_NAME --resource-group $AZURE_RESOURCE_GROUP
```

## Recommendations

When deploying, you might encounter errors or problems, either on the autonatiom part of it (GitHub Actions) or on the deployment destination (Azure WebApps). Here are a list of things to check for, and some suggestions on how to ensure that the deployment is correct.

* Not having enough RAM per container
* Not using authentication for accessing the remote registry (ghcr.io in this case). Authentication is always required
* Not using a PAT (Personal Access Token) or using a PAT that doesn't have write permissions for "packages".
* Different port than 8000 in the container. By default Azure Container Apps use 80 and the automation updates a config option to map it to 8000.

If running into trouble, check logs in the portal or use the following with the Azure CLI:

```
az webapp log tail --name $AZURE_WEBAPP_NAME --resource-group $AZURE_RESOURCE_GROUP
```

Update both variables to match your environment

## Resources 

Use the following links to useful and relevant resources that can help you deploy this API

- [Deploying containers to Azure](https://learning.oreilly.com/videos/deploying-containers-to/50135VIDEOPAIML/)
- [Azure in GitHub Actions](https://learning.oreilly.com/videos/azure-in-github/50140VIDEOPAIML/)
