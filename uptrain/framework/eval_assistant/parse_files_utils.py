import typing as t
import docx
from loguru import logger    
from pypdf import PdfReader
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from uptrain.operators import QueryRewrite
from uptrain import Settings
import polars as pl
from openai import OpenAI
import fitz


def parse_file(
    file_list: t.Union[list]
):
    file_content = []
    for file in file_list:
        try:
            file_location = open(file, "rb")
            if file.split('.')[-1] == 'docx':
                content = parse_docx(file_location)
                file_content.append({
                    'content': content,
                    
                    'file_name':file})

            elif file.split('.')[-1] == 'pdf':
                content = parse_pdf(file_location)
                file_content.append({
                    'content': content,
                    'file_name':file})
                
        except Exception as e:
            logger.error(e)
    return file_content
    
def parse_docx(
    file
):
    doc = docx.Document(file)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    content = [item for item in fullText if item != ""]
    return content

def parse_pdf(
    file
):
    text = ""

    pdf_document = fitz.open(file)
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b["type"] == 0:  # 0 represents a text block
                lines = b["lines"]
                for line in lines:
                    text += line["spans"][0]["text"]  # Add the first span of each line
                text += "\n"  # Add a space instead of a newline character
    pdf_document.close()

    # Split the text into a list based on newline characters
    content = text.split("\n")
    return content



def vector_search(
    file_list: t.Union[list],
    conversation: list[dict],
    openai_api_key: str
):
    context_chunk =[]
    file_parsed = parse_file(file_list)
    for index in range(len(file_parsed)):
        for chunk in file_parsed[index]['content']:
            context_chunk.append([chunk,file_parsed[index]['file_name']])
    context_chunk_df = pd.DataFrame(context_chunk, columns = ['chunk', 'file'])
    text = context_chunk_df['chunk']
    text = [item for item in list(text) if item != ""]
    
    client = OpenAI(api_key=openai_api_key)
    vectors_embeddings = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    # return vectors_embeddings
    vectors = np.array([list(embedding_list.embedding) for embedding_list in vectors_embeddings.data]).astype(np.float32)
    vector_dimension = vectors.shape[1]
    vector_index = faiss.IndexFlatL2(vector_dimension)
    faiss.normalize_L2(vectors)
    vector_index.add(vectors)
    conversation_new = []
    for index in range(len(conversation)):
        conversation_list = conversation[index]['conversation']
        conversation_list_new = []
        conversation_history = []
        rewritten_query = None
        for i in range(len(conversation_list)):
            if conversation_list[i]['role'] == 'user':
                if i>0:
                    settings = Settings(
                        openai_api_key=openai_api_key
                    )
                    query_rewrite_input = [
                        {
                            'question': conversation_list[i]['content'],
                            'conversation': conversation_history
                        }
                    ]
                    rewritten_query = QueryRewrite().setup(settings).run(pl.DataFrame(query_rewrite_input))['output'].to_dicts()[0]['revised_question']
                if rewritten_query is not None:
                    search_text = rewritten_query
                else:
                    search_text = conversation_list[i]['content']
                
                search_vector = client.embeddings.create(
                                                input=search_text,
                                                model="text-embedding-3-small"
                                            )
                search_vector = [embedding.embedding for embedding in search_vector.data]
                search_vector = np.array([list(embedding_list) for embedding_list in search_vector]).astype(np.float32)
                # _vector = np.array([search_vector])
                faiss.normalize_L2(search_vector)
                k = vector_index.ntotal
                # return _vector, k
                distances, ann = vector_index.search(search_vector, k=k)
                results_context_df = pd.DataFrame({'distances': distances[0], 'ann': ann[0]})
                context_chunk_df_final = pd.merge(results_context_df, context_chunk_df, left_on='ann', right_index = True)
                scores = list(context_chunk_df_final['distances'].unique())
                threshold = 2
                mean = np.mean(scores)
                std_dev = np.std(scores)
                context_shortlisted = context_chunk_df_final[context_chunk_df_final['distances']< mean - threshold * std_dev]
                if len(context_shortlisted) > 0:
                    retrieved_context = context_shortlisted['chunk'].str.cat(sep=' ')
                    files_utilized = list(context_shortlisted['file'].unique())
                else:
                    try: 
                        context_shortlisted = context_chunk_df_final.sort_values(by = 'distances', ascending=True)[0:3]
                    except:
                        context_shortlisted = context_chunk_df_final.sort_values(by = 'distances', ascending=True)[0]
                    retrieved_context = context_shortlisted['chunk'].str.cat(sep=' ')
                    files_utilized = list(context_shortlisted['file'].unique())
                    
                message_dict = {
                    'role': conversation_list[i]['role'],
                    'content': conversation_list[i]['content'],
                    'retrieved_context':retrieved_context,
                    'files': files_utilized
                }
                if rewritten_query is not None:
                    message_dict['rewritten_query'] = rewritten_query
                conversation_list_new.append(message_dict)
            else:
                conversation_list_new.append(
                    conversation_list[i]
                )
            rewritten_query = None
            conversation_history.append(conversation_list[i])
        conversation_new.append(conversation[index])
        conversation_new[index]['conversation'] = conversation_list_new
    return conversation_new