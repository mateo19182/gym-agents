from smolagents import Tool
from langchain_chroma import Chroma

class RetrieverTool(Tool):
    name = "buscador"
    description = (
        "Utiliza búsqueda semántica para recuperar partes de la documentación que podrían ser las más relevantes. "
        "Contiene documentos relacionados con las políticas, normas, membresías y servicios del gimnasio."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": (
                "La consulta a realizar. Proporcione información enunciativa en lugar de plantearla como pregunta."
            ),
        }
    }
    output_type = "string"

    def __init__(self, vector_store: Chroma, **kwargs):
        super().__init__(**kwargs)
        self.vector_store = vector_store

    def forward(self, query: str) -> str:
        docs = self.vector_store.similarity_search(query, k=3)
        return "\nDocumentos recuperados:\n" + "".join(
            [f"\n\n===== Documento {i} =====\n{doc.page_content}" for i, doc in enumerate(docs)]
        ) 