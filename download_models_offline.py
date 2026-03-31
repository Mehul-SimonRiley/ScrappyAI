import os
from huggingface_hub import snapshot_download

qwen_model = "Qwen/Qwen2.5-1.5B-Instruct"
bge_model = "BAAI/bge-large-en-v1.5"

print("="*50)
print(f"[System] Initiating deep offline cloning for {qwen_model}...")
print("="*50)
qwen_dir = snapshot_download(
    repo_id=qwen_model, 
    local_dir="offline_models/qwen",
    local_dir_use_symlinks=False,
    ignore_patterns=["*.msgpack", "*.h5", "*.ot", "*onnx*"]  # Download SafeTensors uniquely to shrink footprint mathematically
)
print(f"\\n-> Qwen Successfully cloned definitively to {qwen_dir}\\n")

print("="*50)
print(f"[System] Initiating deep offline cloning for {bge_model}...")
print("="*50)
bge_dir = snapshot_download(
    repo_id=bge_model, 
    local_dir="offline_models/bge",
    local_dir_use_symlinks=False,
    ignore_patterns=["*.msgpack", "*.h5", "*.ot", "*onnx*"] 
)
print(f"\\n-> BGE Successfully cloned definitively to {bge_dir}\\n")

print("-> ALL OFF-GRID DEPENDENCIES DOWNLOADED SUCCESSFULLY!")
