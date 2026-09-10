# Track 2 — application template

Starter skeleton for the Track 2 export control advisor. Read the scenario, the data description, the full I/O contract and the submission rules on the website:
<https://hackathon-armasuisse.github.io/tracks/track-2/>

We note that usage of this template is **optional**. You can start from scratch or use your own framework, as long as you meet the requirements.

## What's here

- `app/main.py` — the `/advise` endpoint skeleton; implement your advisor here.
- `inference.env.example` — the inference endpoint variables we pass at deploy.
- `Dockerfile` — builds and runs the app on port 8080.

The legal sources and the party lists are distributed separately as an encrypted zip, please see the website.

## Deploying on your team VM

Your VM already has a TLS certificate and a public hostname,
`llmhack-team-N.hackathon.intlab.ch`. `compose.yaml` in this repository runs two
containers: **Caddy**, which terminates TLS on that hostname, and **your app**,
which Caddy reaches at `app:8080` on the internal network.

```bash
cp inference.env.example inference.env     # then fill in the key and model
nano Caddyfile                             # replace N with your team number
mkdir -p data && unzip <track2_data.zip> -d data
docker compose up -d --build
```

Check it from another machine:

```bash
curl https://llmhack-team-N.hackathon.intlab.ch/health
```

