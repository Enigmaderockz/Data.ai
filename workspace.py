#prompt

I have built a tool using python which reads the automation reports, fetch the failures, analyses those failures, categories them, come up with theoretical and technical solution. Now consider api is abc and I am calling this api and using prompt to come up with data in these columns analyses those failures, categories them, come up with theoretical and technical solution. Problem is Open AI api is giving me very vague technical everytime as it is not aware of framework which is throwing error. so I amlooking for a function which takes workspace or automation folder as an input system argument and we cna use open ai api either as a workspace to understand the code, and when giving technical solution, it should gie based on the framework so that it would be easy for a person to solve the issues. can you come up with such function?

############################

import os
import openai
import pandas as pd
import faiss
import numpy as np
from openai import OpenAI

client = OpenAI()

# ---------- STEP 1: Embed Workspace ----------
def embed_text(text, model="text-embedding-3-small"):
    resp = client.embeddings.create(
        model=model,
        input=text
    )
    return np.array(resp.data[0].embedding, dtype="float32")

def build_workspace_index(workspace_path: str):
    docs, embeddings = [], []
    
    for root, _, files in os.walk(workspace_path):
        for file in files:
            if file.endswith((".py", ".yaml", ".json")):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        # Chunk large files
                        for i in range(0, len(content), 1500):
                            chunk = content[i:i+1500]
                            docs.append((file, chunk))
                            embeddings.append(embed_text(chunk))
                except Exception as e:
                    print(f"Could not read {file}: {e}")

    embeddings = np.vstack(embeddings)
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return docs, index

# ---------- STEP 2: Search Relevant Code ----------
def search_context(query, docs, index, top_k=3):
    q_emb = embed_text(query)
    distances, idxs = index.search(np.array([q_emb]), top_k)
    return [docs[i] for i in idxs[0]]

# ---------- STEP 3: Analyze Failures ----------
def analyze_failures_excel(excel_path, workspace_path, model="gpt-4o-mini"):
    df = pd.read_excel(excel_path)
    docs, index = build_workspace_index(workspace_path)

    solutions = []
    for reason in df["failure reasons"]:
        context_snippets = search_context(reason, docs, index)
        context_text = "\n\n".join([f"File: {c[0]}\n{c[1]}" for c in context_snippets])

        system_prompt = f"""
        You are an expert QA automation engineer.
        Use the provided framework context to give framework-specific solutions.
        """

        user_prompt = f"""
        Failure reason:
        {reason}

        Framework context:
        {context_text}

        1. Categorize the failure (infra, locator, assertion, network, etc).
        2. Give theoretical root cause.
        3. Suggest a TECHNICAL fix based on the code/framework style.
        """

        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        solutions.append(resp.choices[0].message.content.strip())
    
    df["AI Solutions"] = solutions
    return df
