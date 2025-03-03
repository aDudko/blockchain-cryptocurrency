FROM node:alpine AS frontend
LABEL author="Anatol Dudko"
LABEL email="anatoly_dudko@icloud.com"
WORKDIR /app
COPY templates/package* ./
RUN npm install
COPY ./templates/ ./
RUN npm run build

FROM python:3.12-alpine
LABEL author="Anatol Dudko"
LABEL email="anatoly_dudko@icloud.com"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /static
COPY --from=frontend /app/dist /app/static
RUN rm -r templates
EXPOSE 5000
CMD ["python", "app.py"]