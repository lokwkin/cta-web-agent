# LowCostWebAgent
**cta-web-agent** is an experimental project desgined to build a **fast and cost-effective** autonomous web agentic bot. It pre-masks and preserves only Call-To-Action elements and **uses only text-to-text models** for processing. By doing this, it aims be largely-scalable with a relatively low cost and be **deployable in a private or local environment**.

## Background
Many of the automated web bots on the market require users to predefine the XPath or CSS Selectors of the page elements they want to extract. While this approach may be straightforward and accurate, it cannot handle website layout updates, cannot deal with previously unseen websites, and most importantly, requires human effort to set up.

Since the rise of LLMs, and especially with the advances in vision understanding, some solutions have been developed to combine computer vision with LLM to simulate how humans see, digest, and interact with browsers. However, these solutions often require heavy token usage costs and take a relatively long time to process. And more importantly, difficult to be deployed locally.

Therefore, this project aims to reduce both cost and processing time. Instead of feeding in the screenshots and HTML into LLMs, it uses only texts and pre-masks unnecessary information when processing. *It extracts only the Call-To-Action elements from the webpage, converting HTML to markdown while preserving necessary information, then followed by prompting LLM agents for agentic reasoning and actions. This approach uses purely text-to-text models and avoids image-understanding models, and processes only the necessary texts, thereby reducing cost and processing time.* 

## Limitations
Due to the nature that it uses only text-to-text models, it is expected that it can at best cover most agentic web tasks that doesn't involve images or other non-text information processing. The overall capability may not be comparable with those uses vision models, but as a contrast it can maintain lower token costs.

## Usage
```sh
pip install -r requirements.txt

export OPENAI_API_KEY=<OPENAI_API_KEY>
python src/main.py 'https://github.com' 'Check the price per month for a team plan'
```

## Env Vars
```sh
USE_MODEL_PROVIDER=ollama # "ollama" / "openai" / "groq"

# If you use OpenAI
OPENAI_API_KEY=<Your own API key>
OPENAI_MODEL='gpt-3.5-turbo'
OPENAI_PROXY_URL='http://123.234.345.456:8888' # Proxy URL to connect OpenAI> # e.g.  Leave bank if not needed

# If using Ollama
OLLAMA_API_URL='http://localhost:11434/api/generate'
OLLAMA_MODEL=llama3

# If using Groq
GROQ_API_KEY=<Your own API key>
GROQ_MODEL='llama3-8b-8192'
```

## TODOssss 
- **Welcome any comments, suggestions or even contributions** 😀
- Keep developing and fine-tuning until it succesfully run all the basic flow task targets I have on hand :D
- Models & Prompting
    - Preprocess
        - Split into smaller chunks of HTMLs
        - Masking out too detailed text
        - Logic to better preserve and representation of necessary elements in HTML to markdown
    - Prompting improve
        - Separate understanding of page and decision making
        - Apply Tree of Thought
- Browser interaction
    - Support more input types (dropdown / checkbox / radio button)
    - Support hovering
    - Inspect specific element to get more detail
    - Allow specific URL navigation as an action
    - Explicitly handle google search as an action
    - Captcha handling
- Engineering
    - Dockerize for easy deployment
    - Simple API to control
    - Basic Frontend display for Demo & Evaluation
- Testing
    - Apply evalautions sets like "WebArena" / "AutoWebBench"
