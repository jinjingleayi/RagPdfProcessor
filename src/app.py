"""
Gradio Web Interface for RAG System
Provides an easy-to-use interface for document indexing and Q&A
"""
import gradio as gr
from rag_pipeline import RAGPipeline
from indexing import create_and_index
from es_functions import get_index_stats, delete_elastic_index
import os

# Global pipeline instance
pipeline = None
current_index = None

def initialize_pipeline(index_name, use_multi_query, use_decomposition):
    """Initialize RAG pipeline with specified settings"""
    global pipeline, current_index
    try:
        pipeline = RAGPipeline(
            index_name=index_name,
            use_multi_query=use_multi_query,
            use_query_decomposition=use_decomposition
        )
        current_index = index_name
        return f"✅ Pipeline initialized successfully with index: {index_name}"
    except Exception as e:
        return f"❌ Error initializing pipeline: {str(e)}"

def index_pdf_file(pdf_file, index_name, extract_images, extract_tables):
    """Index a PDF file into Elasticsearch"""
    if not pdf_file:
        return "❌ Please upload a PDF file"
    
    try:
        # Save uploaded file temporarily
        pdf_path = pdf_file.name
        
        # Create index and index the PDF
        count = create_and_index(
            index_name,
            pdf_path,
            extract_images=extract_images,
            extract_tables=extract_tables
        )
        
        stats = get_index_stats(index_name)
        return f"✅ Successfully indexed {count} documents\n📊 Total documents in index '{index_name}': {stats}"
    
    except Exception as e:
        return f"❌ Error indexing PDF: {str(e)}"

def query_rag(question, top_k_retrieval, top_k_rerank):
    """Query the RAG system"""
    global pipeline
    
    if pipeline is None:
        return "❌ Please initialize the pipeline first (see Query tab)", ""
    
    if not question.strip():
        return "❌ Please enter a question", ""
    
    try:
        result = pipeline.query(
            question,
            top_k_retrieval=top_k_retrieval,
            top_k_rerank=top_k_rerank
        )
        
        answer = result['answer']
        
        # Format sources
        sources_text = f"\n\n📚 **Reference Sources ({result['num_sources']} sources):**\n\n"
        for i, source in enumerate(result['sources'], 1):
            sources_text += f"**[{i}]** Type: {source['content_type']}\n"
            sources_text += f"   Preview: {source['text_preview']}\n"
            sources_text += f"   Relevance: {source['rerank_score']:.4f}\n"
            sources_text += f"   Metadata: Page {source['metadata'].get('page', 'N/A')}\n\n"
        
        return answer, sources_text
    
    except Exception as e:
        return f"❌ Error: {str(e)}", ""

def clear_chat_history():
    """Clear chat history"""
    global pipeline
    if pipeline:
        pipeline.clear_history()
        return "✅ Chat history cleared"
    return "⚠️ No active pipeline"

def delete_index(index_name):
    """Delete an Elasticsearch index"""
    try:
        success = delete_elastic_index(index_name)
        if success:
            return f"✅ Index '{index_name}' deleted successfully"
        else:
            return f"⚠️ Index '{index_name}' does not exist"
    except Exception as e:
        return f"❌ Error deleting index: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="RAG PDF Processing System", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 RAG PDF Processing System
    ### Intelligent Document Q&A System with Elasticsearch
    
    **Key Features:**
    - 📄 PDF Processing (text, images, tables)
    - 🔍 Hybrid Search (vector + keyword search)
    - 🎯 Intelligent Reranking
    - 🚀 Multi-Query Retrieval & Query Decomposition
    """)
    
    with gr.Tabs():
        # Tab 1: Document Indexing
        with gr.Tab("📁 Document Indexing"):
            gr.Markdown("### Upload and Index PDF Documents")
            
            with gr.Row():
                with gr.Column():
                    pdf_upload = gr.File(label="Upload PDF File", file_types=[".pdf"])
                    index_name_input = gr.Textbox(
                        label="Index Name",
                        placeholder="my_knowledge_base",
                        value="my_rag_index",
                        info="Use lowercase letters and underscores only"
                    )
                    
                    with gr.Row():
                        extract_images_checkbox = gr.Checkbox(label="Extract Images", value=True)
                        extract_tables_checkbox = gr.Checkbox(label="Extract Tables", value=True)
                    
                    index_button = gr.Button("🚀 Start Indexing", variant="primary")
                
                with gr.Column():
                    index_output = gr.Textbox(label="Indexing Results", lines=10)
            
            index_button.click(
                index_pdf_file,
                inputs=[pdf_upload, index_name_input, extract_images_checkbox, extract_tables_checkbox],
                outputs=index_output
            )
            
            gr.Markdown("---")
            gr.Markdown("### Delete Index")
            with gr.Row():
                delete_index_input = gr.Textbox(label="Index Name", placeholder="index_to_delete")
                delete_button = gr.Button("🗑️ Delete Index", variant="stop")
            delete_output = gr.Textbox(label="Delete Results")
            
            delete_button.click(
                delete_index,
                inputs=delete_index_input,
                outputs=delete_output
            )
        
        # Tab 2: Question Answering
        with gr.Tab("💬 Question & Answer"):
            gr.Markdown("### Initialize RAG System")
            
            with gr.Row():
                pipeline_index_input = gr.Textbox(
                    label="Index Name",
                    placeholder="my_rag_index",
                    value="my_rag_index",
                    info="Name of the index to query"
                )
                multi_query_checkbox = gr.Checkbox(
                    label="Enable Multi-Query Retrieval",
                    value=False,
                    info="Generate query variations for better coverage"
                )
                decomposition_checkbox = gr.Checkbox(
                    label="Enable Query Decomposition",
                    value=False,
                    info="Break complex questions into sub-questions"
                )
            
            init_button = gr.Button("🔧 Initialize System", variant="primary")
            init_output = gr.Textbox(label="Initialization Status")
            
            init_button.click(
                initialize_pipeline,
                inputs=[pipeline_index_input, multi_query_checkbox, decomposition_checkbox],
                outputs=init_output
            )
            
            gr.Markdown("---")
            gr.Markdown("### Ask Questions")
            
            with gr.Row():
                with gr.Column(scale=2):
                    question_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Enter your question here...",
                        lines=3
                    )
                    
                    with gr.Row():
                        top_k_retrieval_slider = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=10,
                            step=1,
                            label="Number of Documents to Retrieve"
                        )
                        top_k_rerank_slider = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=5,
                            step=1,
                            label="Number of Documents After Reranking"
                        )
                    
                    with gr.Row():
                        query_button = gr.Button("🔍 Ask Question", variant="primary")
                        clear_button = gr.Button("🗑️ Clear History")
            
            with gr.Row():
                with gr.Column():
                    answer_output = gr.Textbox(label="📝 Answer", lines=10)
                with gr.Column():
                    sources_output = gr.Textbox(label="📚 Reference Sources", lines=10)
            
            clear_output = gr.Textbox(label="Clear Results", visible=False)
            
            query_button.click(
                query_rag,
                inputs=[question_input, top_k_retrieval_slider, top_k_rerank_slider],
                outputs=[answer_output, sources_output]
            )
            
            clear_button.click(
                clear_chat_history,
                outputs=clear_output
            )
        
        # Tab 3: User Guide
        with gr.Tab("ℹ️ User Guide"):
            gr.Markdown("""
            ## 📖 How to Use This System
            
            ### 1. Index Documents
            - Go to the **"Document Indexing"** tab
            - Upload a PDF file
            - Set an index name (use lowercase and underscores, e.g., `my_docs`)
            - Choose whether to extract images and tables
            - Click **"Start Indexing"**
            
            ### 2. Initialize the System
            - Go to the **"Question & Answer"** tab
            - Enter the index name you created
            - Optionally enable advanced features:
              - **Multi-Query Retrieval**: Generates multiple query variations for better recall
              - **Query Decomposition**: Breaks complex questions into simpler sub-questions
            - Click **"Initialize System"**
            
            ### 3. Ask Questions
            - Enter your question in the text box
            - Adjust retrieval parameters if needed:
              - **Documents to Retrieve**: Initial number of documents (more = broader search)
              - **After Reranking**: Final number of documents used for answer (fewer = more focused)
            - Click **"Ask Question"**
            - View the answer and reference sources
            
            ### 4. System Features
            - ✅ **Hybrid Search**: Combines vector search and keyword search
            - ✅ **Intelligent Reranking**: Uses Reranker model to improve result quality
            - ✅ **Multimodal Processing**: Supports text, images, and tables
            - ✅ **Conversational Context**: Supports multi-turn conversations
            
            ### 5. Important Notes
            - Ensure Elasticsearch is running at `http://localhost:9200`
            - Image and table extraction takes longer (can be disabled for faster indexing)
            - Index names must be lowercase letters and underscores only
            - Test with small documents first
            
            ### 6. Technical Architecture
            ```
            PDF → Extract Content → Chunk → Vectorize → Index to Elasticsearch
                                                              ↓
            User Query → Process Query → Hybrid Search → Rerank → Generate Answer
            ```
            
            ### 7. Tips for Best Results
            - Use clear, specific questions
            - Enable multi-query for complex topics
            - Enable decomposition for multi-part questions
            - Adjust retrieval parameters based on your needs:
              - More documents = broader coverage, but slower
              - Fewer documents = faster, but may miss relevant info
            """)

if __name__ == "__main__":
    print("🚀 Starting RAG System Interface...")
    print("📍 Make sure Elasticsearch is running at http://localhost:9200")
    print("🌐 Interface will be available at: http://localhost:7860")
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
