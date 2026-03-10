"""
LFM2.5 1.2B Thinking Inference Server

Uses llama-server wrapper due to llama-cpp-python binding incompatibilities.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uvicorn
from shared.llama_server_wrapper import LlamaServerConfig, create_llama_server_app

config = LlamaServerConfig(
    model_id="lfm2.5-1.2b-thinking",
    display_name="LFM2.5 1.2B Thinking",
    owned_by="liquidai",
    default_repo="LiquidAI/LFM2.5-1.2B-Thinking-GGUF",
    default_file="LFM2.5-1.2B-Thinking-Q4_K_M.gguf",
    default_port=8108,
    n_ctx=4096,
    max_concurrent=6,
    # LFM2.5 uses short convolution + GQA blocks (no SSM); LiquidAI's design
    # explicitly excludes flash attention. Both flash_attn and kv_cache_quant
    # cause llama_decode -1 on this architecture. See docs/models/lfm2thinking.md
    flash_attn=False,
    kv_cache_quant=False,
)

app = create_llama_server_app(config)

if __name__ == "__main__":
    port = int(os.getenv("PORT", str(config.default_port)))
    uvicorn.run(app, host="0.0.0.0", port=port)
