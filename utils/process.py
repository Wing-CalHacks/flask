import json
import openai
from openai.embeddings_utils import cosine_similarity
import matplotlib
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(
    openai_api_key="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")
openai.api_key = "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"


def getCSV(filename):
    with open(filename, 'r') as f:
        return f.read()

def getJSON(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        return data


def getEmbeddedProducts(products, format):
    embeds = {}
    for p in products:
        embeds[p] = embeddings.embed_query(p)
    # export embeddings to a file
    with open('data/embeddings.json', 'w') as outfile:
        json.dump(embeds, outfile)
    return embeds


# turns each string into a product object and converts to json
def process_products(inputs):
    products = []
    for item in inputs:
        product = create_product_object(item[0])
        product_json = json.dumps(product, cls=ProductEncoder)
        product_dict = json.loads(product_json)
        products.append(product_dict)

    return products

def product_template(products):
    res = []
    for p in products:
        res.append(
            {
                'name': p['title'],
                'desc': p['desc']
            }
        )
    return str(res)

