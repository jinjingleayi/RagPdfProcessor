"""
RAG System - Complete Workflow with Detailed Progress
"""
import gradio as gr
from rag_pipeline import RAGPipeline
from indexing import index_pdf, index_directory
from es_functions import get_index_stats, create_elastic_index, delete_elastic_index
import os
import time

# Global state
current_index = None
pipeline = None
is_ready = False

def step1_create_index(index_name):
    """STEP 1: Create or Select Index"""
    global current_index, is_ready, pipeline
    
    if not index_name or not index_name.strip():
        return "❌ Please enter an index name", ""
    
    index_name = index_name.strip().lower().replace(" ", "_")
    
    status = f"📊 STEP 1: Creating/Selecting Index\n"
    status += f"{'='*60}\n\n"
    status += f"🔄 Checking index: {index_name}...\n"
    
    try:
        created = create_elastic_index(index_name)
        
        if created:
            status += f"✅ New index '{index_name}' created successfully!\n"
        else:
            stats = get_index_stats(index_name)
            status += f"✅ Using existing index '{index_name}'\n"
            status += f"📈 Current documents: {stats}\n"
        
        current_index = index_name
        is_ready = False
        pipeline = None
        
        status += f"\n{'='*60}\n"
        status += f"✅ Index ready: {index_name}\n"
        status += f"➡️ Next: Go to STEP 2 to upload PDFs"
        
        return status, f"✅ Index: {index_name}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}", "❌ Failed"

def step2_ingest_pdfs(files, extract_images, extract_tables):
    """STEP 2: Ingest PDFs with detailed extraction display"""
    global current_index, is_ready
    
    if not current_index:
        return "❌ Please create/select an index first (STEP 1)"
    
    if not files or len(files) == 0:
        return "❌ Please upload at least one PDF file"
    
    output = []
    output.append(f"📥 STEP 2: Ingesting PDF Documents")
    output.append(f"{'='*60}\n")
    output.append(f"📂 Index: {current_index}")
    output.append(f"📄 Files to process: {len(files)}")
    output.append(f"🖼️  Extract images: {'Yes' if extract_images else 'No'}")
    output.append(f"📊 Extract tables: {'Yes' if extract_tables else 'No'}")
    output.append(f"{'='*60}\n")
    
    try:
        total_docs = 0
        
        for i, file in enumerate(files):
            pdf_name = os.path.basename(file.name)
            
            output.append(f"\n{'─'*60}")
            output.append(f"[{i+1}/{len(files)}] 🔄 Processing: {pdf_name}")
            output.append(f"{'─'*60}")
            
            # Process PDF with detailed output
            result, docs = index_pdf(file.name, current_index, extract_images, extract_tables)
            output.append(result)
            total_docs += len(docs)
            
            yield "\n".join(output)
        
        # Final summary
        stats = get_index_stats(current_index)
        is_ready = True
        
        output.append(f"\n{'='*60}")
        output.append(f"✅ INGESTION COMPLETE!")
        output.append(f"{'='*60}")
        output.append(f"📊 Summary:")
        output.append(f"   • Processed: {len(files)} PDF(s)")
        output.append(f"   • Total chunks in index: {stats}")
        output.append(f"   • Index ready for queries")
        output.append(f"{'='*60}\n")
        output.append(f"➡️ Next: Go to STEP 3 to query your documents!")
        
        yield "\n".join(output)
        
    except Exception as e:
        output.append(f"\n❌ Error: {str(e)}")
        yield "\n".join(output)

def step2_ingest_folder():
    """Quick: Ingest test folder with detailed progress"""
    global current_index, is_ready
    
    if not current_index:
        return "❌ Please create/select an index first (STEP 1)"
    
    folder_path = "../data/pdfs/test_pdf"
    
    if not os.path.exists(folder_path):
        return "❌ Test folder not found"
    
    output = []
    output.append(f"📥 STEP 2: Ingesting Test PDFs")
    output.append(f"{'='*60}\n")
    output.append(f"📂 Index: {current_index}")
    output.append(f"📁 Folder: test_pdf/")
    
    try:
        # Use detailed directory indexing
        result = index_directory(
            folder_path,
            current_index,
            extract_images=True,  # Enable to show extraction
            extract_tables=True
        )
        
        output.append(result)
        is_ready = True
        
        output.append(f"\n➡️ Next: Go to STEP 3 to query!")
        
        return "\n".join(output)
        
    except Exception as e:
        output.append(f"\n❌ Error: {str(e)}")
        return "\n".join(output)

def step3_query(query, top_k_retrieval, top_k_rerank):
    """STEP 3: Query with detailed process"""
    global current_index, pipeline, is_ready
    
    if not current_index:
        return "❌ Please complete STEP 1 first", ""
    
    if not is_ready:
        return "⚠️ Please complete STEP 2 first (ingest PDFs)", ""
    
    if not query.strip():
        return "❌ Please enter a query", ""
    
    output = []
    output.append(f"🔍 STEP 3: Query System")
    output.append(f"{'='*60}\n")
    output.append(f"📂 Index: {current_index}")
    output.append(f"❓ Query: {query}")
    output.append(f"{'='*60}\n")
    
    try:
        # Initialize pipeline
        if pipeline is None or pipeline.index_name != current_index:
            output.append(f"🔄 Initializing RAG pipeline...")
            pipeline = RAGPipeline(
                index_name=current_index,
                use_multi_query=False,
                use_query_decomposition=False
            )
            output.append(f"✅ Pipeline ready\n")
        
        output.append(f"🔍 Searching your PDFs...")
        output.append(f"   📊 Retrieving top {top_k_retrieval} documents...")
        output.append(f"   🎯 Reranking to top {top_k_rerank}...")
        output.append(f"   🤖 Generating answer from YOUR documents...\n")
        
        # Get answer
        result = pipeline.simple_query(query, top_k_retrieval, top_k_rerank)
        
        output.append(f"{'='*60}")
        output.append(f"✅ Query Complete!")
        output.append(f"{'='*60}\n")
        output.append(f"📝 ANSWER:\n")
        output.append(result['answer'])
        
        # Format sources
        sources = []
        sources.append(f"📚 SOURCE DOCUMENTS FROM YOUR PDFs")
        sources.append(f"{'='*60}\n")
        sources.append(f"Found {result['num_sources']} relevant passages:\n")
        
        for i, source in enumerate(result['sources'], 1):
            sources.append(f"[{i}] Type: {source['content_type']} | Page {source['metadata'].get('page', '?')} | Relevance: {source['rerank_score']:.1%}")
            sources.append(f"Preview: {source['text_preview']}")
            sources.append(f"{'-'*60}\n")
        
        return "\n".join(output), "\n".join(sources)
        
    except Exception as e:
        output.append(f"\n❌ Error: {str(e)}")
        return "\n".join(output), ""

def step4_settings():
    """STEP 4: Settings"""
    global current_index
    
    if not current_index:
        return "Please create an index first (STEP 1)"
    
    try:
        stats = get_index_stats(current_index)
        
        info = []
        info.append(f"⚙️ STEP 4: Settings & Optimization")
        info.append(f"{'='*60}\n")
        info.append(f"📂 Current Index: {current_index}")
        info.append(f"📊 Total Documents: {stats}\n")
        info.append(f"🔧 Current Settings:")
        info.append(f"   • Chunk Size: 1024 tokens")
        info.append(f"   • Chunk Overlap: 100 tokens")
        info.append(f"   • Embedding Dimension: 1024")
        info.append(f"   • Using: Ollama (llama3.2) - FREE!")
        info.append(f"\n💡 Tips:")
        info.append(f"   ✓ Images & tables are extracted for complete understanding")
        info.append(f"   ✓ Increase retrieval count for broader search")
        info.append(f"   ✓ Lower temperature = more factual answers")
        
        return "\n".join(info)
    except Exception as e:
        return f"❌ Error: {str(e)}"

def step5_delete_index(index_to_delete):
    """Delete index"""
    if not index_to_delete:
        return "❌ Enter index name"
    
    try:
        success = delete_elastic_index(index_to_delete.strip())
        return f"✅ Deleted: {index_to_delete}" if success else f"⚠️ Not found: {index_to_delete}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Create interface
with gr.Blocks(title="RAG System", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📚 RAG PDF Processing System
    ### Complete Workflow: Index → Ingest → Query → Optimize
    """)
    
    with gr.Tabs():
        with gr.Tab("1️⃣ Create/Select Index"):
            gr.Markdown("### Step 1: Create or select an index name for your documents")
            
            with gr.Row():
                with gr.Column():
                    index_input = gr.Textbox(
                        label="Index Name",
                        placeholder="my_documents",
                        value="my_documents"
                    )
                    create_btn = gr.Button("🎯 Create/Select Index", variant="primary", size="lg")
                with gr.Column():
                    index_status = gr.Textbox(label="Status", value="⏳ Waiting...", lines=1)
            
            step1_output = gr.Textbox(label="Details", lines=10)
            create_btn.click(step1_create_index, inputs=index_input, outputs=[step1_output, index_status])
        
        with gr.Tab("2️⃣ Ingest PDF Documents"):
            gr.Markdown("### Step 2: Upload and process PDFs (with text, images, tables extraction)")
            
            with gr.Row():
                with gr.Column():
                    pdf_upload = gr.File(
                        label="📁 Upload PDF Files (multiple allowed)",
                        file_types=[".pdf"],
                        file_count="multiple"
                    )
                    
                    gr.Markdown("**Extraction Options:**")
                    with gr.Row():
                        extract_imgs = gr.Checkbox(label="📸 Extract Images", value=True, info="Process images in PDFs")
                        extract_tbls = gr.Checkbox(label="📊 Extract Tables", value=True, info="Process tables in PDFs")
                    
                    ingest_btn = gr.Button("📥 Start Ingestion (shows detailed progress)", variant="primary", size="lg")
                    
                    gr.Markdown("---\n**Quick Test:**")
                    test_btn = gr.Button("📂 Ingest Test PDFs (3 files with images/tables)", variant="secondary")
                
                with gr.Column():
                    ingest_output = gr.Textbox(
                        label="Extraction Progress (shows text, images, tables)",
                        lines=30,
                        placeholder="Detailed progress will appear here..."
                    )
            
            ingest_btn.click(step2_ingest_pdfs, inputs=[pdf_upload, extract_imgs, extract_tbls], outputs=ingest_output)
            test_btn.click(step2_ingest_folder, outputs=ingest_output)
        
        with gr.Tab("3️⃣ Query System"):
            gr.Markdown("### Step 3: Ask questions - AI answers using ONLY your uploaded PDFs")
            
            with gr.Row():
                with gr.Column():
                    query_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Ask about content in your PDFs...",
                        lines=3
                    )
                    
                    with gr.Row():
                        k_retrieval = gr.Slider(1, 20, value=10, step=1, label="Retrieve")
                        k_rerank = gr.Slider(1, 10, value=5, step=1, label="Rerank to")
                    
                    query_btn = gr.Button("🔍 Search & Answer", variant="primary", size="lg")
                    
                    gr.Examples(
                        examples=[
                            "What is the main topic of these documents?",
                            "Summarize the key points",
                            "What information about criminal procedure?"
                        ],
                        inputs=query_input
                    )
            
            with gr.Row():
                with gr.Column():
                    answer_output = gr.Textbox(label="📝 AI Answer (from YOUR PDFs only)", lines=20)
                with gr.Column():
                    sources_output = gr.Textbox(label="📚 Source Documents", lines=20)
            
            query_btn.click(step3_query, inputs=[query_input, k_retrieval, k_rerank], 
                          outputs=[answer_output, sources_output])
        
        with gr.Tab("4️⃣ Settings & Optimization"):
            gr.Markdown("### Step 4: View settings and manage indexes")
            
            refresh_btn = gr.Button("🔄 View Current Settings", variant="primary")
            settings_output = gr.Textbox(label="Settings", lines=15)
            refresh_btn.click(step4_settings, outputs=settings_output)
            
            gr.Markdown("---\n### Delete Index")
            with gr.Row():
                delete_input = gr.Textbox(label="Index Name", placeholder="index_to_delete")
                delete_btn = gr.Button("🗑️ Delete", variant="stop")
            delete_output = gr.Textbox(label="Result")
            delete_btn.click(step5_delete_index, inputs=delete_input, outputs=delete_output)

if __name__ == "__main__":
    print("🚀 Starting RAG System...")
    print("📍 Elasticsearch: http://localhost:9200")
    print("🦙 Ollama: FREE local AI")
    print("🌐 Interface: http://localhost:7860")
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
