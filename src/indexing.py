"""
Indexing Module with Detailed Progress Display
"""
from pdf_processor import process_pdf_complete
from embedding import batch_embedding
from es_functions import create_elastic_index, bulk_index_documents, get_index_stats
import os

def index_pdf(pdf_path, index_name, extract_images=True, extract_tables=True):
    """
    Process and index a single PDF with detailed progress
    """
    output = []
    
    if not os.path.exists(pdf_path):
        return f"❌ PDF not found: {pdf_path}", output
    
    pdf_name = os.path.basename(pdf_path)
    
    output.append(f"\n{'='*60}")
    output.append(f"📄 Processing: {pdf_name}")
    output.append(f"{'='*60}\n")
    
    try:
        # Step 1: Extract content with details
        output.append("🔄 Step 1: Extracting content from PDF...")
        output.append(f"   📝 Extracting text chunks...")
        
        pdf_content = process_pdf_complete(pdf_path, extract_images, extract_tables)
        all_content = pdf_content['all_content']
        
        # Show extraction details
        output.append(f"   ✅ Extracted {len(pdf_content['text_chunks'])} text chunks")
        
        if extract_images:
            output.append(f"   📸 Extracted {len(pdf_content['images'])} images")
            for i, img in enumerate(pdf_content['images'][:3], 1):  # Show first 3
                output.append(f"      • Image {i}: {img['text'][:80]}...")
        
        if extract_tables:
            output.append(f"   📊 Extracted {len(pdf_content['tables'])} tables")
            for i, tbl in enumerate(pdf_content['tables'][:3], 1):  # Show first 3
                output.append(f"      • Table {i}: {tbl['text'][:80]}...")
        
        output.append(f"\n   📦 Total content items: {len(all_content)}")
        
        if not all_content:
            output.append("❌ No content extracted from PDF")
            return "\n".join(output), []
        
        # Step 2: Generate embeddings
        output.append(f"\n🔄 Step 2: Generating embeddings (vectorization)...")
        texts = [item['text'] for item in all_content]
        embeddings = batch_embedding(texts, batch_size=25)
        output.append(f"   ✅ Generated {len(embeddings)} vectors")
        
        # Step 3: Prepare documents
        output.append(f"\n🔄 Step 3: Preparing documents for indexing...")
        documents = []
        file_name = os.path.basename(pdf_path)
        
        for i, (content, embedding) in enumerate(zip(all_content, embeddings)):
            doc = {
                'text': content['text'],
                'vector': embedding,
                'content_type': content.get('content_type', 'text'),
                'file_name': file_name,
                'page': content.get('metadata', {}).get('page', 0),
                'chunk_id': f"{file_name}_{i}",
                'metadata': content.get('metadata', {})
            }
            
            if 'image_path' in content.get('metadata', {}):
                doc['image_path'] = content['metadata']['image_path']
            
            if 'table_markdown' in content:
                doc['table_markdown'] = content['table_markdown']
            
            documents.append(doc)
        
        output.append(f"   ✅ Prepared {len(documents)} documents")
        
        # Step 4: Index to Elasticsearch
        output.append(f"\n🔄 Step 4: Indexing to Elasticsearch...")
        success, failed = bulk_index_documents(index_name, documents)
        
        output.append(f"   ✅ Successfully indexed: {success} documents")
        if failed > 0:
            output.append(f"   ⚠️ Failed: {failed} documents")
        
        output.append(f"\n{'='*60}")
        output.append(f"✅ {pdf_name} processing complete!")
        output.append(f"{'='*60}\n")
        
        return "\n".join(output), documents
        
    except Exception as e:
        output.append(f"\n❌ Error processing {pdf_name}: {str(e)}")
        return "\n".join(output), []

def index_directory(directory_path, index_name, extract_images=True, extract_tables=True):
    """Index all PDFs in a directory with progress"""
    output = []
    
    if not os.path.exists(directory_path):
        return f"❌ Directory not found: {directory_path}"
    
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        return f"❌ No PDF files found in {directory_path}"
    
    output.append(f"\n{'='*60}")
    output.append(f"📂 Processing Directory: {directory_path}")
    output.append(f"📄 Found {len(pdf_files)} PDF file(s)")
    output.append(f"{'='*60}\n")
    
    total_success = 0
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(directory_path, pdf_file)
        output.append(f"\n[{i}/{len(pdf_files)}] 📄 {pdf_file}")
        output.append(f"{'-'*60}")
        
        try:
            result, docs = index_pdf(pdf_path, index_name, extract_images, extract_tables)
            output.append(result)
            total_success += len(docs)
        except Exception as e:
            output.append(f"❌ Error: {str(e)}\n")
    
    # Final summary
    stats = get_index_stats(index_name)
    output.append(f"\n{'='*60}")
    output.append(f"📊 FINAL SUMMARY")
    output.append(f"{'='*60}")
    output.append(f"✅ Total documents in index: {stats}")
    output.append(f"📚 Ready for queries!")
    output.append(f"{'='*60}\n")
    
    return "\n".join(output)

def create_and_index(index_name, pdf_path_or_directory, extract_images=True, extract_tables=True):
    """Create index and index PDFs"""
    output = []
    
    output.append(f"🎯 Creating/Using Index: {index_name}")
    create_elastic_index(index_name)
    output.append(f"✅ Index ready\n")
    
    if os.path.isfile(pdf_path_or_directory):
        result, docs = index_pdf(pdf_path_or_directory, index_name, extract_images, extract_tables)
        output.append(result)
        return len(docs)
    elif os.path.isdir(pdf_path_or_directory):
        result = index_directory(pdf_path_or_directory, index_name, extract_images, extract_tables)
        output.append(result)
        return get_index_stats(index_name)
    else:
        return 0

if __name__ == '__main__':
    test_index = 'test_index'
    test_pdf = '../data/pdfs/test_pdf'
    if os.path.exists(test_pdf):
        create_and_index(test_index, test_pdf, extract_images=True, extract_tables=True)
