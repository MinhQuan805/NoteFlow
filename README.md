## 📂 Cấu trúc thư mục

````
# 🚀 Cách chạy dự án

## 🔹 Backend (FastAPI)

1. **Cài thư viện cần thiết**

   ```bash
   pip install -r requirements.txt
````

2. **Chạy server**

   ```bash
   uvicorn main:app --reload
   ```

   > Server sẽ chạy tại: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔹 Frontend (Next.js)

> ⚠️ Yêu cầu: Cài đặt **Node.js >= v22.19.0**

1. **Cài thư viện cần thiết**

   ```bash
   npm install
   ```

2.1 **Chạy ứng dụng phía developer**

Chạy dự án

```bash
npm run dev
```

> Ứng dụng sẽ chạy tại: [http://localhost:3000](http://localhost:3000)

2.2 **Chạy ứng dụng phía client**

Build Project

```bash
npm run build
```

Chạy dự án

```bash
npm run build
```

> Ứng dụng sẽ chạy tại: [http://localhost:3000](http://localhost:3000)

---

## Notes

Links sent from the frontend that are invalid or cause errors will not be ingested, so they must be checked first
