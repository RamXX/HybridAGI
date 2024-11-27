from typing import Literal, Tuple
from hybridagi.readers import DocumentReader
from hybridagi.core.datatypes import Document, DocumentList
from docling_core.types.doc.document import DoclingDocument
from docling.document_converter import DocumentConverter
import json

class DoclingReader(DocumentReader):
    """A document reader implementation that uses Docling to process and convert documents.
    
    This class extends the DocumentReader HybridAGI base class to provide functionality for reading
    and converting documents using the Docling library. It supports multiple output formats
    including text, markdown, and JSON.

    Inherits From:
        DocumentReader: Base class for document reading operations
    """
    def read(self, filepath: str, format: Literal['text', 'markdown', 'json'] = 'text') -> Tuple[DocumentList, DoclingDocument]:
        """Reads and converts a document file using Docling.

        This method takes a file path and converts the document using Docling's DocumentConverter.
        The converted document can be exported in different formats (text, markdown, or JSON).
        
        Args:
            filepath (str): Path to the input document file
            format (Literal['text', 'markdown', 'json'], optional): Output format for the converted document. 
                Defaults to 'text'.

        Returns:
            Tuple[DocumentList, DoclingDocument]: A tuple containing:
                - DocumentList: A DocumentList object containing a single HybridAGI Document with the converted text and metadata
                - DoclingDocument: The raw Docling document object for further processing if needed
            NOTE: ALL other readers in HybridAGI return a DocumentList. However, since the workflow typically involves
                  chunking the document after it's obtained, it is much easier to return the DoclingDocument instance
                  which we can use to that effect via DoclingHierarchicalChunker.

        Example:
            ```python
            reader = DoclingReader()
            hybridagi_doc_list, docling_doc = reader.read("path/to/file.txt", format="markdown")
            singledoc = hybridagi_doc_list.docs[0]

            embeddings = OllamaEmbeddings()
            document_pipeline = Pipeline()
            document_pipeline.add("chunk_documents", DoclingHierarchicalChunker(doclingdoc=docling_doc))
            document_pipeline.add("embed_chunks", DocumentEmbedder(embeddings=embeddings))

            presentation_chunks = document_pipeline(presentation_doc)
            presentation_memory = LocalDocumentMemory(index_name="company_presentation")
            presentation_memory.update(presentation_doc)
            presentation_memory.update(presentation_chunks)
            ```
        """
        converter = DocumentConverter()
        result = converter.convert(filepath)
        doclingdoc = result.document

        match format:
            case "text": 
                text = doclingdoc.export_to_text()
            case "markdown":
                text = doclingdoc.export_to_markdown()
            case "json":
                text = json.dumps(doclingdoc.export_to_dict())
        
        dl = DocumentList()
        dl.docs.append( # type: ignore
            Document(
                text=text,
                metadata={"filepath": filepath, "format": format, "converter": "docling"},
            )
        )
        return dl, doclingdoc