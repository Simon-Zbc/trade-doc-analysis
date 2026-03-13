# Deployment Guide for Trade Document Analysis App

## Azure Setup

### 1. Azure Portal Setup

#### Create Document Intelligence Resource
1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Document Intelligence"
4. Click Create and configure:
   - **Subscription**: Select your subscription
   - **Resource group**: Create new or select existing
   - **Region**: Choose appropriate region (e.g., East US)
   - **Name**: e.g., `doc-intelligence-trade`
   - **Pricing tier**: Select Standard for production

5. After creation, go to "Keys and Endpoint"
6. Copy:
   - **Endpoint**: `https://<region>.api.cognitive.microsoft.com/`
   - **Key 1 or Key 2**: Save for .env file

#### Create or Configure Azure AI Foundry

Option 1: Using Azure AI Foundry (Recommended)
1. Go to [Azure AI Foundry](https://ai.azure.com)
2. Create a new project or select existing
3. Go to "Deployments"
4. Deploy a GPT-4 mini model:
   - Model: gpt-4-mini
   - Deployment name: gpt-4-mini
   - Version: Latest

5. Go to "Credentials & Keys"
6. Copy:
   - **API Key**: For .env file
   - **API Endpoint**: For .env file

Option 2: Using Azure OpenAI Service
1. Go to Azure Portal
2. Search for "OpenAI"
3. Create Azure OpenAI resource
4. Go to "Keys and Endpoint"
5. Deploy GPT-4 mini model in "Model deployments"
6. Copy endpoint and key

### 2. Local Environment Setup

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd trade-doc-analysis
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables
   ```bash
   cp .env.example .env
   ```

6. Edit `.env` with your Azure credentials:
   ```
   DOCUMENT_INTELLIGENCE_ENDPOINT=https://<region>.api.cognitive.microsoft.com/
   DOCUMENT_INTELLIGENCE_KEY=<your-api-key>
   
   AZURE_AI_FOUNDRY_ENDPOINT=https://<region>.openai.azure.com/
   AZURE_AI_FOUNDRY_API_KEY=<your-api-key>
   AZURE_AI_FOUNDRY_MODEL=gpt-4-mini
   ```

### 3. Local Testing

1. Run the startup check
   ```bash
   python setup.py
   ```

2. Run unit tests
   ```bash
   python -m unittest tests.py
   ```

3. Run the Streamlit application
   ```bash
   streamlit run src/app.py
   ```

The application should open at `http://localhost:8501`

## Cloud Deployment Options

### Option 1: Azure App Service

1. Create App Service Plan
   ```bash
   az appservice plan create \
     --name trade-doc-plan \
     --resource-group <resource-group> \
     --sku B1 \
     --is-linux
   ```

2. Create Web App
   ```bash
   az webapp create \
     --resource-group <resource-group> \
     --plan trade-doc-plan \
     --name trade-doc-app \
     --runtime "python|3.9"
   ```

3. Deploy application
   ```bash
   az webapp deployment source config-zip \
     --resource-group <resource-group> \
     --name trade-doc-app \
     --src <zip-file>
   ```

4. Configure environment variables
   ```bash
   az webapp config appsettings set \
     --resource-group <resource-group> \
     --name trade-doc-app \
     --settings DOCUMENT_INTELLIGENCE_KEY="<key>" \
     DOCUMENT_INTELLIGENCE_ENDPOINT="<endpoint>" \
     AZURE_AI_FOUNDRY_API_KEY="<key>" \
     AZURE_AI_FOUNDRY_ENDPOINT="<endpoint>"
   ```

### Option 2: Azure Container Instances

1. Create Dockerfile
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["streamlit", "run", "src/app.py", "--server.port=80"]
   ```

2. Build and push to Azure Container Registry
   ```bash
   az acr build \
     --registry <registry-name> \
     --image trade-doc-app:latest .
   ```

3. Deploy to ACI
   ```bash
   az container create \
     --resource-group <resource-group> \
     --name trade-doc-app \
     --image <registry>.azurecr.io/trade-doc-app:latest \
     --environment-variables DOCUMENT_INTELLIGENCE_KEY="<key>" \
     --ports 80
   ```

### Option 3: Azure Static Web Apps with Backend

For a more scalable solution:

1. Deploy backend as Azure Function
2. Deploy Streamlit frontend to Static Web Apps
3. Use Azure API Management for routing

## Performance Optimization

### For Production Use

1. **Enable caching** in Document Intelligence
2. **Implement rate limiting** to prevent API quota exceeded
3. **Add logging** to track usage patterns
4. **Use async processing** for multiple documents
5. **Set up monitoring** with Application Insights

### Scaling Considerations

- Document Intelligence: Auto-scale based on requests
- AI Foundry: Monitor token usage and costs
- App Service: Use Premium tier for high traffic
- Implement request queuing for batch processing

## Cost Optimization

1. **Use Standard pricing** for Document Intelligence (S0 tier)
2. **Monitor API usage** in Azure Portal
3. **Implement document caching** to reduce re-processing
4. **Use Azure Spot Instances** for non-critical tasks
5. **Set up budget alerts** in Azure Cost Management

## Monitoring and Logging

### Application Insights Integration

1. Create Application Insights resource
   ```bash
   az monitor app-insights component create \
     --app trade-doc-app \
     --location <region> \
     --resource-group <resource-group>
   ```

2. Add instrumentation to Python app
   ```python
   from opencensus.ext.flask.flask_middleware import FlaskMiddleware
   from opencensus.trace.samplers import ProbabilitySampler
   ```

3. Monitor in Azure Portal

### Logging Best Practices

- Log all API calls with request/response
- Track document processing time
- Monitor error rates and types
- Set up alerts for failures

## Troubleshooting Production Issues

### Common Issues

1. **API Quota Exceeded**
   - Implement request throttling
   - Increase API tier

2. **Slow Document Processing**
   - Check document file size
   - Optimize GPT prompts
   - Consider async processing

3. **Authentication Failures**
   - Verify Azure credentials
   - Check endpoint format
   - Ensure API key hasn't expired

## Security Considerations

1. **Use Managed Identities** instead of keys where possible
2. **Store secrets in Azure Key Vault**
3. **Enable HTTPS** for all connections
4. **Implement IP whitelisting** if applicable
5. **Audit access logs** regularly
6. **Encrypt data in transit and at rest**

## Maintenance

1. **Regular backups** of configuration
2. **Update dependencies** monthly
3. **Monitor Azure SDK versions**
4. **Test updates** in staging environment
5. **Keep documentation** updated
