"""
Simple RAG System Interface - Easy to use!
"""
import gradio as gr
from rag_pipeline import RAGPipeline
from indexing import create_and_index, index_directory
from es_functions import get_index_stats, create_elastic_index
import os
import shutil

# Global variables
INDEX_NAME = "my_documents"
pipeline = None
documents_ready = False

def process_pdfs(files, extract_images, extract_tables):
    """
    Process uploaded PDF files - this is the INDEXING step
    (Indexing = Making PDFs searchable by the system)
    """
    global documents_ready
    
    if not files or len(files) == 0:
        return "❌ Please upload at least one PDF file"
    
    try:
        # Create index if it doesn't exist
        create_elastic_index(INDEX_NAME)
        
        results = []
        total_docs = 0
        
        # Process each uploaded PDF
        for i, file in enumerate(files):
            pdf_path = file.name
            pdf_name = os.path.basename(pdf_path)
            
            results.append(f"📄 Processing {i+1}/{len(files)}: {pdf_name}...")
            
            # Index the PDF (make it searchable)
            count = create_and_index(
                INDEX_NAME,
                pdf_path,
                extract_images=extract_images,
                extract_tables=extract_tables
            )
            total_docs += count
            results.append(f"   ✅ Added {count} searchable chunks from {pdf_name}\n")
        
        # Get total stats
        stats = get_index_stats(INDEX_NAME)
        documents_ready = True
        
        summary = "\n".join(results)
        summary += f"\n{'='*60}\n"
        summary += f"✅ SUCCESS!\n"
        summary += f"📊 Total searchable chunks: {stats}\n"
        summary += f"📚 Processed {len(files)} PDF(s)\n\n"
        summary += f"➡️ Now go to the 'Ask Questions' tab to search your documents!"
        
        return summary
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease check if Elasticsearch is running."

def process_folder():
    """Process all PDFs in the test folder"""
    global documents_ready
    
    folder_path = "../data/pdfs/test_pdf"
    
    if not os.path.exists(folder_path):
        return "❌ Test folder not found"
    
    try:
        # Create index
        create_elastic_index(INDEX_NAME)
        
        # Process all PDFs in folder
        count = index_directory(
            folder_path,
            INDEX_NAME,
            extract_images=False,  # Faster without images
            extract_tables=True
        )
        
        stats = get_index_stats(INDEX_NAME)
        documents_ready = True
        
        return f"""✅ SUCCESS!
        
📊 Processed all PDFs from test folder
📈 Total searchable chunks: {stats}

➡️ Now go to 'Ask Questions' tab to search!"""
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def ask_question(question):
    """Ask a question about your documents"""
    global pipeline, documents_ready
    
    if not question.strip():
        return "❌ Please enter a question", ""
    
    if not documents_ready:
        return "⚠️ Please upload and process PDFs first (go to 'Upload PDFs' tab)", ""
    
    try:
        # Initialize pipeline if needed
        if pipeline is None:
            pipeline = RAGPipeline(
                index_name=INDEX_NAME,
                use_multi_query=False,
                use_query_decomposition=False
            )
        
        # Get answer
        result = pipeline.simple_query(question)
        
        answer = result['answer']
        
        # Format sources
        sources = f"\n📚 Found {result['num_sources']} relevant document(s):\n\n"
        for i, source in enumerate(result['sources'], 1):
            sources += f"[{i}] {source['text_preview']}\n"
            sources += f"    (Page {source['metadata'].get('page', '?')}, "
            sources += f"Relevance: {source['rerank_score']:.2%})\n\n"
        
        return answer, sources
    
    except Exception as e:
        return f"❌ Error: {str(e)}", ""

# Create simple interface
with gr.Blocks(title="Simple RAG System", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📚 Simple RAG System - Search Your PDFs!
    
    ## How to use (2 simple steps):
    1. **Upload PDFs** → Click "Process PDFs" (this makes them searchable)
    2. **Ask Questions** → Type your question and get answers!
    
    ---
    """)
    
    with gr.Tabs():
        # Tab 1: Upload PDFs
        with gr.Tab("📤 STEP 1: Upload PDFs"):
            gr.Markdown("""
            ### Upload Your PDF Documents
            **What is "Processing"?** It means the system reads your PDFs and makes them searchable.
            You only need to do this once per document.
            """)
            
            with gr.Row():
                with gr.Column():
                    pdf_files = gr.File(
                        label="📁 Select PDF Files (you can select multiple!)",
                        file_types=[".pdf"],
                        file_count="multiple"
                    )
                    
                    with gr.Row():
                        extract_images = gr.Checkbox(
                            label="Extract Images (slower but more complete)",
                            value=False
                        )
                        extract_tables = gr.Checkbox(
                            label="Extract Tables",
                            value=True
                        )
                    
                    process_btn = gr.Button("🚀 Process PDFs", variant="primary", size="lg")
                    
                    gr.Markdown("---\n### Or use test PDFs:")
                    test_folder_btn = gr.Button("📂 Process Test PDFs (3 files)", variant="secondary")
                
                with gr.Column():
                    upload_output = gr.Textbox(
                        label="Processing Status",
                        lines=20,
                        placeholder="Upload PDFs and click 'Process PDFs' to start..."
                    )
            
            process_btn.click(
                process_pdfs,
                inputs=[pdf_files, extract_images, extract_tables],
                outputs=upload_output
            )
            
            test_folder_btn.click(
                process_folder,
                outputs=upload_output
            )
        
        # Tab 2: Ask Questions
        with gr.Tab("💬 STEP 2: Ask Questions"):
            gr.Markdown("""
            ### Search Your Documents
            Ask any question about the PDFs you uploaded!
            """)
            
            with gr.Row():
                with gr.Column():
                    question_box = gr.Textbox(
                        label="Your Question",
                        placeholder="Example: What is this document about?",
                        lines=3
                    )
                    ask_btn = gr.Button("🔍 Get Answer", variant="primary", size="lg")
                    
                    gr.Examples(
                        examples=[
                            "What is the main topic of these documents?",
                            "Summarize the key points",
                            "What information is provided about [topic]?"
                        ],
                        inputs=question_box
                    )
            
            with gr.Row():
                with gr.Column():
                    answer_box = gr.Textbox(
                        label="📝 Answer",
                        lines=10,
                        placeholder="Your answer will appear here..."
                    )
                with gr.Column():
                    sources_box = gr.Textbox(
                        label="📚 Source Documents",
                        lines=10,
                        placeholder="Related document excerpts..."
                    )
            
            ask_btn.click(
                ask_question,
                inputs=question_box,
                outputs=[answer_box, sources_box]
            )
        
        # Tab 3: Help
        with gr.Tab("❓ Help"):
            gr.Markdown("""
            ## 📖 How This System Works
            
            ### Simple Explanation:
            
            1. **Upload PDFs** 
               - You give the system your PDF files
               
            2. **Processing (Indexing)**
               - The system reads the PDFs
               - Breaks them into small, searchable pieces
               - Stores them in a database (Elasticsearch)
               - This makes searching FAST!
               
            3. **Ask Questions**
               - You type a question
               - System finds relevant parts from your PDFs
               - AI generates an answer based on what it found
               
            ### Tips:
            - ✅ Upload all your PDFs at once (select multiple files)
            - ✅ Processing takes time - be patient!
            - ✅ You can upload more PDFs later - they'll be added to your collection
            - ✅ Ask specific questions for better answers
            
            ### Troubleshooting:
            - If processing fails, make sure Elasticsearch is running
            - If answers are poor, try uploading PDFs with images/tables enabled
            - Clear and specific questions get better answers!
            """)

if __name__ == "__main__":
    print("🚀 Starting Simple RAG System...")
    print("📍 Elasticsearch should be at http://localhost:9200")
    print("🌐 Opening web interface at http://localhost:7860")
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
