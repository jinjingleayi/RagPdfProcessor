"""
PDF Processing - Extracts text, images, and tables with progress display
"""
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP
import tiktoken
import fitz
import os

def num_tokens_from_string(string):
    """Calculate tokens in string"""
    encoding = tiktoken.get_encoding('cl100k_base')
    return len(encoding.encode(string))

def extract_text_chunks(pdf_path, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """Extract and chunk text from PDF"""
    print(f"   [Text] Extracting text from PDF...")
    
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=num_tokens_from_string
    )
    
    chunks = text_splitter.split_documents(pages)
    
    result = []
    for i, chunk in enumerate(chunks):
        result.append({
            'text': chunk.page_content,
            'metadata': {
                'page': chunk.metadata.get('page', 0),
                'source': chunk.metadata.get('source', pdf_path),
                'chunk_id': i
            },
            'content_type': 'text'
        })
    
    print(f"   ✅ Extracted {len(result)} text chunks from {len(pages)} pages")
    return result

def extract_images_from_pdf(pdf_path, output_dir='../data/images'):
    """Extract images from PDF (basic extraction)"""
    print(f"   [Images] Scanning PDF for images...")
    
    pdf_document = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    processed_xrefs = set()
    total_images_found = 0
    
    for page_num in range(pdf_document.page_count):
        try:
            page = pdf_document.load_page(page_num)
            page_width = page.rect.width
            page_text = page.get_text("text")
            
            page_images = pdf_document.get_page_images(page_num)
            
            for img_index, item in enumerate(page_images):
                try:
                    xref = item[0]
                    if xref in processed_xrefs:
                        continue
                    processed_xrefs.add(xref)
                    total_images_found += 1
                    
                    image_width = item[2]
                    image_height = item[3]
                    
                    # Skip small images
                    if image_width < page_width / 3 or image_width < 200 or image_height < 100:
                        continue
                    
                    # Extract image
                    pix = fitz.Pixmap(pdf_document, xref)
                    if pix.colorspace and pix.colorspace.name == 'DeviceCMYK':
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    
                    image_filename = f'img_p{page_num + 1}_i{img_index + 1}.png'
                    image_save_path = os.path.join(output_dir, image_filename)
                    pix.save(image_save_path)
                    del pix
                    
                    # Create description from context
                    description = f"Image on page {page_num + 1} - Context: {page_text[:200]}..."
                    
                    results.append({
                        'text': description,
                        'metadata': {
                            'page': page_num,
                            'source': pdf_path,
                            'image_path': image_save_path
                        },
                        'content_type': 'image'
                    })
                    print(f"   ✅ Extracted image from page {page_num + 1}")
                
                except Exception as e:
                    print(f"   ⚠️ Could not process image {img_index + 1} on page {page_num + 1}")
                    continue
        
        except Exception as e:
            continue
    
    pdf_document.close()
    print(f"   📸 Total images found: {total_images_found}, extracted: {len(results)}")
    return results

def extract_tables_from_pdf(pdf_path):
    """Extract tables from PDF"""
    print(f"   [Tables] Scanning PDF for tables...")
    
    pdf_document = fitz.open(pdf_path)
    results = []
    
    for page_num in range(pdf_document.page_count):
        try:
            page = pdf_document.load_page(page_num)
            page_text = page.get_text("text")
            page_tables = page.find_tables()
            
            for table_index, table in enumerate(page_tables):
                try:
                    md = table.to_markdown()
                    
                    # Create description
                    description = f"Table on page {page_num + 1}:\n{md}"
                    
                    results.append({
                        'text': description,
                        'metadata': {
                            'page': page_num,
                            'source': pdf_path,
                            'table_index': table_index
                        },
                        'content_type': 'table',
                        'table_markdown': md
                    })
                    print(f"   ✅ Extracted table from page {page_num + 1}")
                except Exception as e:
                    continue
        
        except Exception as e:
            continue
    
    pdf_document.close()
    print(f"   📊 Total tables extracted: {len(results)}")
    return results

def process_pdf_complete(pdf_path, extract_images=True, extract_tables=True):
    """
    Complete PDF processing with detailed progress
    """
    print(f"\n📄 Processing: {os.path.basename(pdf_path)}")
    print(f"{'─'*60}")
    
    # Extract text
    text_chunks = extract_text_chunks(pdf_path)
    
    # Extract images
    image_descriptions = []
    if extract_images:
        try:
            image_descriptions = extract_images_from_pdf(pdf_path)
        except Exception as e:
            print(f"   ⚠️ Image extraction skipped: {e}")
    else:
        print(f"   ⏭️ Image extraction disabled")
    
    # Extract tables
    table_descriptions = []
    if extract_tables:
        try:
            table_descriptions = extract_tables_from_pdf(pdf_path)
        except Exception as e:
            print(f"   ⚠️ Table extraction skipped: {e}")
    else:
        print(f"   ⏭️ Table extraction disabled")
    
    # Combine
    all_content = text_chunks + image_descriptions + table_descriptions
    
    print(f"\n   📊 Extraction Summary:")
    print(f"      • Text chunks: {len(text_chunks)}")
    print(f"      • Images: {len(image_descriptions)}")
    print(f"      • Tables: {len(table_descriptions)}")
    print(f"      • Total: {len(all_content)} items")
    
    return {
        'text_chunks': text_chunks,
        'images': image_descriptions,
        'tables': table_descriptions,
        'all_content': all_content
    }
