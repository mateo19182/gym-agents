from smolagents import Tool
from langchain_chroma import Chroma

class RetrieverTool(Tool):
    name = "retriever"
    description = (
        "Uses semantic search to retrieve parts of documentation that could be most relevant. "
        "It contains documents related to gym policies, rules, membership, and amenities information."
        "You should query this tool in English!"
    )
    inputs = {
        "query": {
            "type": "string",
            "description": (
                "The query to perform. Provide information aligned with your target documents. "
                "Use the affirmative form rather than a question."
            ),
        }
    }
    output_type = "string"

    def __init__(self, vector_store: Chroma, **kwargs):
        super().__init__(**kwargs)
        self.vector_store = vector_store

    def forward(self, query: str) -> str:
        docs = self.vector_store.similarity_search(query, k=3)
        return "\nRetrieved documents:\n" + "".join(
            [f"\n\n===== Document {i} =====\n{doc.page_content}" for i, doc in enumerate(docs)]
        ) 