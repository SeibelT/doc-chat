from Backend.create_vectorDB import create_vectorstore_from_pdfs


#create_vectorstore_from_pdfs(pdf_dir, index_dir, chunk_size=1000, chunk_overlap=200)
path_prompts = "meta_data/prompts.yaml"
import os 
if not os.path.exists(path_prompts):
        print(f"Prompts file not found at {path_prompts}. Please ensure it exists.")    
else:
    with open(path_prompts, 'r') as file:
        prompts = file.read()
    print("Prompts loaded successfully.",prompts)

prompts["average"]