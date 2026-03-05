import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uvicorn
from shared.llama_server_wrapper import LlamaServerConfig, create_llama_server_app

config = LlamaServerConfig(
    model_id="falcon-h1r-7b",
    display_name="Falcon H1R 7B",
    owned_by="tii",
    default_repo="unsloth/Falcon-H1R-7B-GGUF",
    default_file="Falcon-H1R-7B-Q4_K_M.gguf",
    default_port=8202,
    n_ctx=4096,
    max_concurrent=2,
)

app = create_llama_server_app(config)

if __name__ == "__main__":
    port = int(os.getenv("PORT", str(config.default_port)))
    uvicorn.run(app, host="0.0.0.0", port=port)
