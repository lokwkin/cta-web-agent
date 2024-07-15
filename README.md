# cta-web-agent
**cta-web-agent** is an experimental project aiming to build an automated web agent bot that performs user tasks in a fast and cost-effectively manner, by extracting critical Call-To-Action elements and pre-masking unnecessary information before prompting LLMs.

## Background
Many of the automated web bots on the market require users to predefine the XPath or CSS Selectors of the page elements they want to extract. While this approach may be straightforward and accurate, it cannot handle website layout updates, cannot deal with previously unseen websites, and most importantly, requires human effort to set up.

Since the rise of LLMs, and especially with the advances in vision understanding, some solutions have been developed to combine computer vision with LLM to simulate how humans see, digest, and interact with browsers. However, these solutions often require heavy token usage costs and take a relatively long time to process. 

Therefore, this project aims to reduce both cost and processing time. Instead of feeding in the entire screen and HTML into LLMs, it pre-masks unnecessary information before prompting. *It extracts only the Call-To-Action elements from the webpage, converting HTML to markdown while preserving critical information, then followed by prompting LLM for planning and actions. This approach avoids using computer vision and highlights only the necessary data, thereby reducing cost and processing time.*

## Usage
```
export OPENAI_API_KEY=<OPENAI_API_KEY>
python src/main.py https://github.com 'Search for most starred AI agent repository'
```