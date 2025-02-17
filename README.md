# Gym-Agents

docker build -t gym-api .
docker run -p 8000:8000 --env-file .env gym-api

 python -m tests.test_retriever

## TODO
  - make fast!
  - openTelemetry: <https://huggingface.co/docs/smolagents/tutorials/inspect_runs>
  - speech2text
  - español adapt
    - embeddings! (https://jina.ai/news/aqui-se-habla-espanol-top-quality-spanish-english-embeddings-and-8k-context/)
    - https://medium.com/contact-research/how-to-deal-with-different-language-questions-in-your-rag-application-714eb3ccb772
      - seems like translation everything to engliush is the best option for now
- available tools:
  - web search
  - python
  - txt2sql
  - rag w/ chroma

- figure out schedules
  - store as csv / json or SQL?
  - pass current datetime as context