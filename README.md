# FastAPI WebSocket Chat App

This project is a **FastAPI-based WebSocket Chat Application** that allows real-time communication between users. The app is designed with authentication, rate limiting, and message history. Additionally, **ngrok** is used to expose the WebSocket publicly for testing, and **Grafana + Prometheus** is set up to monitor the app's performance metrics.

---

## Features 🚀
- **FastAPI WebSocket communication** for real-time chat.
- **Token-based authentication** for security.
- **Rate limiting** to prevent message spam.
- **Message history** for better user experience.
- **Ngrok** for public testing without deploying.
- **Grafana + Prometheus** for real-time application monitoring.

---

## Prerequisites 📌
Make sure you have the following installed:

- **Docker & Docker Compose**
- **Python 3.8+**
- **Ngrok** (for public testing)
- **Prometheus & Grafana** (for monitoring)

---

## Installation 🛠
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-repo/fastapi-websocket-chat.git
cd fastapi-websocket-chat
```

### 2️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 3️⃣ Run the Application (Locally)
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000/`.

---

## Public Testing with Ngrok 🌍
To test the WebSocket publicly:

1. **Run ngrok to expose FastAPI**:
   ```sh
   ngrok http 8000
   ```
2. **Copy the ngrok URL** (e.g., `https://your-ngrok-url.ngrok-free.app`)
3. **Update the frontend WebSocket connection**:
   ```js
   let ws = new WebSocket("wss://your-ngrok-url.ngrok-free.app/ws?token=valid_token");
   ```

Now, users can connect to the chat from anywhere using the **ngrok URL**.

---

## Monitoring with Grafana 📊
We use **Prometheus + Grafana** to monitor CPU usage, WebSocket activity, and app performance.

### 1️⃣ Run Prometheus and Grafana with Docker Compose
```sh
docker-compose up -d
```

### 2️⃣ Access Prometheus UI
- Open `http://localhost:9090`
- Add a scrape target for FastAPI in `prometheus.yml`:
  ```yaml
  scrape_configs:
    - job_name: "fastapi"
      static_configs:
        - targets: ["fastapi:8000"]
  ```

### 3️⃣ Configure Grafana
- Open `http://localhost:3000`
- Default login: `admin / admin`
- **Add Prometheus as a Data Source** (`http://prometheus:9090`)
- **Create Dashboard** with panels:
  - **CPU Usage**:  
    ```promql
    rate(process_cpu_seconds_total{job="fastapi"}[1m])
    or
    100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
    ```
  - **WebSocket Requests**:
    ```promql
    sum(rate(http_requests_total[5m]))
    ```

Now, you can visualize your WebSocket app's performance! 🚀

---

## Running with Docker 🐳
To run everything in **Docker**, use:
```sh
docker-compose up --build
```
This will start FastAPI, Prometheus, Grafana, and Ngrok together.

---

## Conclusion 🎉
You now have a **real-time chat app** with **WebSockets**, **public access via Ngrok**, and **monitoring via Grafana**! 🛠🔥

Feel free to **contribute** and improve this project! 🚀

