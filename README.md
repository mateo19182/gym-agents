# IreneAgent

docker build -t gym-api .
docker run -p 8000:8000 --env-file .env gym-api

## TODO
  - make fast!
  - openTelemetry: <https://huggingface.co/docs/smolagents/tutorials/inspect_runs>
  - speech2text
  - español adapt

- available tools:
  - web search
  - python
  - txt2sql
  - rag w/ chroma

- figure out schedules
  - store as csv / json or SQL?
  - pass current datetime as context