# Blockchain Cryptocurrency

## Overview

This project is a basic implementation of a blockchain and cryptocurrency application. The project is implemented 
in `Python` (backend) and `Vue` (frontend) using `Docker` for containerization.

## Technologies
- **Python**: `Flask` for API
- **Vue.js**: SPA frontend on `Vite`
- **Docker**: Containerization
- **Blockchain**: Core blockchain and transaction logic

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
├── templates/             # Vue.js frontend
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

- Go to the root folder of the project:
```sh
cd blockchain-cryptocurrency
```

- Build Docker and run:
```sh
docker-compose up --build
```

- Open in browser:
```
http://localhost:5001
http://localhost:5002
http://localhost:5003
```

### Author: 
Anatoly Dudko

