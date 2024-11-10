# %% [markdown]
# ## Weaviate quickstart guide (as a notebook!)
# 
# This notebook will guide you through the basics of Weaviate. You can find the full documentation [on our site here](https://weaviate.io/developers/weaviate/quickstart).
# 
# <a target="_blank" href="https://colab.research.google.com/github/weaviate-tutorials/quickstart/blob/main/quickstart_end_to_end.ipynb">
#   <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
# </a>

# %% [markdown]
# You will need the Weaviate Python client. If you don't yet have it installed - you can do so with:

# %%
# !pip install -U weaviate-client

# %% [markdown]
# ### Weaviate instance
# 
# For this, you will need a working instance of Weaviate somewhere. We recommend either:
# - Creating a free sandbox instance on Weaviate Cloud Services (https://console.weaviate.cloud/), or
# - Using [Embedded Weaviate](https://weaviate.io/developers/weaviate/installation/embedded).
# 
# Instantiate the client using **one** of the following code examples:

# %% [markdown]
# #### For using WCS
# 
# NOTE: Before you do this, you need to create the instance in WCS and get the credentials. Please refer to the [WCS Quickstart guide](https://weaviate.io/developers/wcs/quickstart).

# %%
# # For using WCS
import weaviate
import json
import os
import dotenv

dotenv.load_dotenv()
client = weaviate.Client(
    url = "https://9xpe4nykqgq5v7zrfdji4q.c0.us-west3.gcp.weaviate.cloud",  # Replace with your endpoint
    auth_client_secret=weaviate.AuthApiKey(api_key=os.environ["WEAVIATE-API-KEY"]),  # Replace w/ your Weaviate instance API key
    additional_headers = {
        "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]  # Replace with your inference API key
    }
)

# %% [markdown]
# ### Create a class

# %%
if client.schema.exists("Question"):
    client.schema.delete_class("Question")

# %%
class_obj = {
    "class": "Question",
    "vectorizer": "text2vec-openai",  # If set to "none" you must always provide vectors yourself. Could be any other "text2vec-*" also.
    "moduleConfig": {
        "text2vec-openai": {},
        "generative-openai": {}  # Ensure the `generative-openai` module is used for generative queries
    }
}

client.schema.create_class(class_obj)

# %% [markdown]
# ### Add objects
# 
# We'll add objects to our Weaviate instance using a batch import process.
# 
# We shows you two options, where you can either:
# - Have Weaviate create vectors, or
# - Specify custom vectors.

# %% [markdown]
# #### Have Weaviate create vectors (with `text2vec-openai`)

# %%
# Load data
import requests
url = 'https://raw.githubusercontent.com/weaviate-tutorials/quickstart/main/data/jeopardy_tiny.json'
resp = requests.get(url)
data = json.loads(resp.text)

# Configure a batch process
with client.batch(
    batch_size=100
) as batch:
    # Batch import all Questions
    for i, d in enumerate(data):
        print(f"importing question: {i+1}")

        properties = {
            "answer": d["Answer"],
            "question": d["Question"],
            "category": d["Category"],
        }

        client.batch.add_data_object(
            properties,
            "Question",
        )

# %% [markdown]
# #### Specify "custom" vectors (i.e. generated outside of Weaviate)

# %%
# # Load data
# import requests
# fname = "jeopardy_tiny_with_vectors_all-OpenAI-ada-002.json"  # This file includes pre-generated vectors
# url = f'https://raw.githubusercontent.com/weaviate-tutorials/quickstart/main/data/{fname}'
# resp = requests.get(url)
# data = json.loads(resp.text)

# # Configure a batch process
# with client.batch(
#     batch_size=100
# ) as batch:
#     # Batch import all Questions
#     for i, d in enumerate(data):
#         print(f"importing question: {i+1}")

#         properties = {
#             "answer": d["Answer"],
#             "question": d["Question"],
#             "category": d["Category"],
#         }

#         custom_vector = d["vector"]
#         client.batch.add_data_object(
#             properties,
#             "Question",
#             vector=custom_vector  # Add custom vector
#         )

# %% [markdown]
# ### Queries

# %% [markdown]
# #### Semantic search
# 
# Let's try a similarity search. We'll use nearText search to look for quiz objects most similar to biology.

# %%
nearText = {"concepts": ["biology"]}

response = (
    client.query
    .get("Question", ["question", "answer", "category"])
    .with_near_text(nearText)
    .with_limit(2)
    .do()
)

print(json.dumps(response, indent=4))

# %% [markdown]
# The response includes a list of top 2 (due to the limit set) objects whose vectors are most similar to the word biology.
# 
# Notice that even though the word biology does not appear anywhere, Weaviate returns biology-related entries.
# 
# This example shows why vector searches are powerful. Vectorized data objects allow for searches based on degrees of similarity, as shown here.

# %% [markdown]
# #### Semantic search with a filter
# You can add a Boolean filter to your example. For example, let's run the same search, but only look in objects that have a "category" value of "ANIMALS".

# %%
nearText = {"concepts": ["biology"]}

response = (
    client.query
    .get("Question", ["question", "answer", "category"])
    .with_near_text(nearText)
    .with_where({
        "path": ["category"],
        "operator": "Equal",
        "valueText": "ANIMALS"
    })
    .with_limit(2)
    .do()
)

print(json.dumps(response, indent=4))

# %% [markdown]
# The response includes a list of top 2 (due to the limit set) objects whose vectors are most similar to the word biology - but only from the "ANIMALS" category.
# 
# Using a Boolean filter allows you to combine the flexibility of vector search with the precision of where filters.

# %% [markdown]
# #### Generative search (single prompt)
# 
# Next, let's try a generative search, where search results are processed with a large language model (LLM).
# 
# Here, we use a `single prompt` query, and the model to explain each answer in plain terms.

# %%
nearText = {"concepts": ["biology"]}

response = (
    client.query
    .get("Question", ["question", "answer", "category"])
    .with_near_text(nearText)
    .with_generate(single_prompt="Explain {answer} as you might to a five-year-old.")
    .with_limit(2)
    .do()
)

print(json.dumps(response, indent=4))

# %% [markdown]
# We see that Weaviate has retrieved the same results as before. But now it includes an additional, generated text with a plain-language explanation of each answer.

# %% [markdown]
# #### Generative search (grouped task)
# 
# In the next example, we will use a grouped task prompt instead to combine all search results and send them to the LLM with a prompt. We ask the LLM to write a tweet about all of these search results.

# %%
response = (
    client.query
    .get("Question", ["question", "answer", "category"])
    .with_near_text({"concepts": ["biology"]})
    .with_generate(grouped_task="Write a tweet with emojis about these facts.")
    .with_limit(2)
    .do()
)

print(response["data"]["Get"]["Question"][0]["_additional"]["generate"]["groupedResult"])

# %% [markdown]
# Generative search sends retrieved data from Weaviate to a large language model, or LLM. This allows you to go beyond simple data retrieval, but transform the data into a more useful form, without ever leaving Weaviate.

# %% [markdown]
# Well done! In just a few short minutes, you have:
# 
# - Created your own cloud-based vector database with Weaviate,
# - Populated it with data objects,
#     - Using an inference API, or
#     - Using custom vectors,
# - Performed searches, including:
#     - Semantic search,
#     - Sementic search with a filter and
#     - Generative search.

# %% [markdown]
# ## Next
# 
# You can do much more with Weaviate. We suggest trying:
# 
# - Examples from our [search how-to](https://weaviate.io/developers/weaviate/search) guides for [keyword](https://weaviate.io/developers/weaviate/search/bm25), [similarity](https://weaviate.io/developers/weaviate/search/similarity), [hybrid](https://weaviate.io/developers/weaviate/search/hybrid), [generative](https://weaviate.io/developers/weaviate/search/generative) searches and [filters](https://weaviate.io/developers/weaviate/search/filters) or
# - Learning [how to manage data](https://weaviate.io/developers/weaviate/manage-data), like [reading](https://weaviate.io/developers/weaviate/manage-data/read), [batch importing](https://weaviate.io/developers/weaviate/manage-data/import), [updating](https://weaviate.io/developers/weaviate/manage-data/update), [deleting](https://weaviate.io/developers/weaviate/manage-data/delete) objects or [bulk exporting](https://weaviate.io/developers/weaviate/manage-data/read-all-objects) data.
# 
# For more holistic learning, try <i class="fa-solid fa-graduation-cap"></i> [Weaviate Academy](https://weaviate.io/developers/academy). We have built free courses for you to learn about Weaviate and the world of vector search.
# 
# You can also try a larger, [1,000 row](https://raw.githubusercontent.com/databyjp/wv_demo_uploader/main/weaviate_datasets/data/jeopardy_1k.json) version of the Jeopardy! dataset, or [this tiny set of 50 wine reviews](https://raw.githubusercontent.com/databyjp/wv_demo_uploader/main/weaviate_datasets/data/winemag_tiny.csv).

# %% [markdown]
# 


