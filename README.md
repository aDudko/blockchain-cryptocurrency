# Blockchain Cryptocurrency

**A basic implementation of a blockchain and cryptocurrency application**

## Technologies

- `Python` - version 3.12
- `pycryptodomex` - crypto
- `requests` - connection between network nodes
- `Flask` for API
- `Vue3`: SPA frontend on `Vite`
- `Docker` - containerization
- `Docker-Compose` - infrastructure for network
- `Blockchain` - core blockchain and transaction logic

## Project structure

```
blockchain-cryptocurrency/
│   app.py                 # Flask API
│   compose.yml            # Docker Compose
│   Dockerfile             # Docker config
│   .gitignore             # Git ignore rules
│   .dockerignore          # Docker ignore rules
│
├── src/                   # Blockchain logic
|   ├── utils              # Helpers
│   ├── block.py
│   ├── blockchain.py
│   ├── transaction.py
│   ├── wallet.py
│   └── __init__.py
│
├── templates/             # Vue frontend
│   ├── src/
│   │   ├── components/
│   │   ├── assets/
│   │   ├── main.js
│   │   ├── App.vue
│   │   └── style.css
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── .env
```

## Run in Docker

```sh
docker-compose up --build
```

Open in browser:

```
http://localhost:5001
http://localhost:5002
http://localhost:5003
```

### Author:

Anatoly Dudko

