# Gym-Agents

docker build -t gym-agent .
docker run -p 8000:8000 --env-file .env gym-agent

sudo docker build -t registry.innplay.site/gym-agent:0.1 .
docker push registry.innplay.site/gym-agent:0.1

## TODO
  - make fast!
  - openTelemetry: <https://huggingface.co/docs/smolagents/tutorials/inspect_runs>
  - speech2text
  - español adapt
    - traducir todo and use embeddings in english lol

  - se caga con el conversation history a vecess...

- available tools:
  - web search
  - python
  - txt2sql
  - rag w/ chroma

- figure out schedules
  - store as csv / json or SQL?
  - pass current datetime as context