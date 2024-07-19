**cta-web-agent** is an experimental project targetted to build an automated web agentic bot that performs user tasks in a fast and cost-effectively manner, by pre-masking and preserving only Call-To-Action elements and using purely text-to-text models. By doing this, it aims to be easily deployable in a local environment and be able to largely scale out with a relatively low cost.

## Background
Many of the automated web bots on the market require users to predefine the XPath or CSS Selectors of the page elements they want to extract. While this approach may be straightforward and accurate, it cannot handle website layout updates, cannot deal with previously unseen websites, and most importantly, requires human effort to set up.

Since the rise of LLMs, and especially with the advances in vision understanding, some solutions have been developed to combine computer vision with LLM to simulate how humans see, digest, and interact with browsers. However, these solutions often require heavy token usage costs and take a relatively long time to process. And more importantly, difficult to be deployed locally.

Therefore, this project aims to reduce both cost and processing time. Instead of feeding in the screenshots and HTML into LLMs, it pre-masks unnecessary information before prompting. *It extracts only the Call-To-Action elements from the webpage, converting HTML to markdown while preserving critical information, then followed by prompting LLM agents for agentic reasoning and actions. This approach uses purely text-to-text models and avoids image-understanding models, and processes only the necessary data, thereby reducing cost and processing time.* 

## Limitations
Due to the nature that it uses only text-to-text models, it is expected that it can at best cover most agentic web tasks that doesn't involve images or other non-text information processing.

## Usage
```sh
pip install -r requirements.txt

export OPENAI_API_KEY=<OPENAI_API_KEY>
python src/main.py 'https://github.com' 'Check the price per month for a team plan'
```

## Env Vars
```sh
USE_MODEL_PROVIDER=ollama # "ollama" / "openai"
OPENAI_API_KEY=<Your own API key>
OPENAI_MODEL='gpt-3.5-turbo'
OPENAI_PROXY_URL='http://123.234.345.456:8888' # Proxy URL to connect OpenAI> # e.g.  Leave bank if not needed
OLLAMA_API_URL='http://localhost:11434/api/generate'
OLLAMA_MODEL=llama3
```

## TODOssss 
**(welcome any comments, suggestions or even contributions😀)**
- Keep developing and fine-tuning until it succesfully run all the basic flow task targets I have on hand :D
- Models & Prompting
    - Preprocess
        - Masking out too detailed text for smaller prompt input
        - Re-construct of HTML to markdown
    - Models adaption
        - Groq client
        - Other smaller size models
    - Prompting improve
        - Separate understanding of page and decision making
        - Auto fixing json
        - Apply Tree of Thought
- Browser interaction
    - Support more input types (dropdown / checkbox / radio button)
    - Support hovering
    - Allow specific URL navigation as an action
    - Explicitly handle google search as an action
    - Inspect specific element to get more detail
    - Captcha handling
- Engineering
    - Dockerize for easy deployment
    - Simple API to control
    - Basic Frontend display
- Testing
    - Apply evalautions like "WebArena" / "AutoWebBench"
