import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

defaults = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

with open(Path(__file__).parent / "config.development.yaml") as f:
    yaml_config = yaml.safe_load(f) or {}

load_dotenv(override=False)

env_config = {}
for key, value in os.environ.items():
    if key.startswith("APP_"):
        env_config[key[4:].lower()] = value

if "NUM_WORKERS" in os.environ:
    env_config["workers"] = os.environ["NUM_WORKERS"]

config = {}
config.update(defaults)
config.update(yaml_config)
config.update(env_config)


def coerce(key, value):
    if key in {"port", "workers"}:
        return int(value)
    if key == "debug":
        return str(value).strip().lower() in {"true", "1", "yes", "on"}
    return str(value)


for key in list(config):
    config[key] = coerce(key, config[key])


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    result = dict(config)

    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            key = key.strip()
            if key:
                result[key] = coerce(key, value)

    result["api_key"] = "****"
    return result
