# Databricks notebook source
# DBTITLE 1,Install Dependencies
# MAGIC %pip install mlflow==2.10.1 langchain==0.1.5 databricks-vectorsearch==0.22 databricks-sdk==0.18.0 mlflow[databricks]
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Set needed parameters
import os

host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")
os.environ['DATABRICKS_TOKEN'] = "dapi314ca2214d8fcc*******"

index_name="health.default.asclepius_notes_en"
host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")

VECTOR_SEARCH_ENDPOINT_NAME="dbdemos_vs_endpoint"

# COMMAND ----------

# DBTITLE 1,Build Retriever
from databricks.vector_search.client import VectorSearchClient
from langchain_community.vectorstores import DatabricksVectorSearch
from langchain_community.embeddings import DatabricksEmbeddings

embedding_model = DatabricksEmbeddings(endpoint="text-embedding-3-large")

def get_retriever(persist_dir: str = None):
    os.environ["DATABRICKS_HOST"] = host
    #Get the vector search index
    vsc = VectorSearchClient(workspace_url=host, personal_access_token=os.environ["DATABRICKS_TOKEN"])
    vs_index = vsc.get_index(
        endpoint_name=VECTOR_SEARCH_ENDPOINT_NAME,
        index_name=index_name
    )

    # Create the retriever
    vectorstore = DatabricksVectorSearch(
        vs_index, text_column="note", embedding=embedding_model
    )
    return vectorstore.as_retriever()

# COMMAND ----------

# DBTITLE 1,test vector endpoint
# Get the retriever
retriever = get_retriever()

# Perform a search (example)
query = "What is the expanded form of the abbreviation 'CSF'?"
results = retriever.get_relevant_documents(query)

# Print the results
for result in results:
    print(result)

# COMMAND ----------

# DBTITLE 1,Create the RAG Langchain
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatDatabricks

chat_model = ChatDatabricks(endpoint="llama_3_70b_instruct", max_tokens = 200)

TEMPLATE = """You are a healthcare assistant responsible for answering health-related questions. Use the provided pieces of retrieved context to formulate your response. Only include information from the context that is directly relevant to the question. Ignore any irrelevant details. \n\n Context: {context}
Question: {question}
Answer:
"""
prompt = PromptTemplate(template=TEMPLATE, input_variables=["context", "question"])

chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    chain_type="stuff",
    retriever=get_retriever(),
    chain_type_kwargs={"prompt": prompt}
)

# COMMAND ----------

# DBTITLE 1,Test Langchain
question = {"query": "What are the key findings and diagnosis of the patient with cutaneous T-cell lymphoma/mycosis fungoides, type II diabetes mellitus, atrial flutter, sick sinus syndrome, and metastatic Merkel cell carcinoma?"}
answer = chain.run(question) # chain.invoke(question)
print(answer)

# COMMAND ----------

# DBTITLE 1,Register our Chain as a model to Unity Catalog
from mlflow.models import infer_signature
import mlflow
import langchain

mlflow.set_registry_uri("databricks-uc")
model_name = "health.default.health_chatbot_model"

with mlflow.start_run(run_name="health_chatbot_run") as run:
    signature = infer_signature(question, answer)
    model_info = mlflow.langchain.log_model(
        chain,
        loader_fn=get_retriever,  # Load the retriever with DATABRICKS_TOKEN env as secret (for authentication).
        artifact_path="chain",
        registered_model_name=model_name,
        pip_requirements=[
            "mlflow==" + mlflow.__version__,
            "langchain==" + langchain.__version__,
            "databricks-vectorsearch",
        ],
        input_example=question,
        signature=signature
    )

# COMMAND ----------

#{
#  "dataframe_split": {
#    "columns": [ "query" ],
#    "data": [[ "Hi, how are you?" ]]
#  }
#}

# COMMAND ----------

# MAGIC %environment
# MAGIC "client": "1"
# MAGIC "base_environment": ""
