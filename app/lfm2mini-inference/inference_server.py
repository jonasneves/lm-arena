import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uvicorn
from shared.llama_server_wrapper import LlamaServerConfig, create_llama_server_app

config = LlamaServerConfig(
    model_id="lfm2-350m",
    display_name="LFM2 350M",
    owned_by="liquidai",
    default_repo="unsloth/LFM2-350M-GGUF",
    default_file="LFM2-350M-Q4_K_M.gguf",
    default_port=8110,
    n_ctx=8192,
    max_concurrent=6,
)

app = create_llama_server_app(config)

if __name__ == "__main__":
    port = int(os.getenv("PORT", str(config.default_port)))
    uvicorn.run(app, host="0.0.0.0", port=port)
