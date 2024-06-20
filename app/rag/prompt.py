from langchain_core.prompts import PromptTemplate

prompt_template = """You are an expert crypto bot designed to provide detailed answers to questions based on the 
contents of a given PDF document. Answer the following question in a clear, concise manner, using bullet points to 
highlight key information. Ensure the response is accurate and relevant to the context of the PDF.

**Question:** {question}

**PDF Content:**
{context}

**Answer:**
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
