from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from producer.kafka_producer import send_to_kafka
from consumer.kafka_consumer import run_consumer
import threading

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Danh sách 10 feature numeric mà model dùng
TOP5_FEATURES = [
    'int_rate', 'fico_range_low', 'funded_amnt', 'dti',
    'annual_inc', 'pub_rec', 'open_acc', 'total_acc',
    'delinq_2yrs', 'acc_now_delinq'
]

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit")
def submit_form(
    int_rate: float = Form(...),
    fico_range_low: int = Form(...),
    funded_amnt: float = Form(...),
    dti: float = Form(...),
    annual_inc: float = Form(...),
    pub_rec: int = Form(...),
    open_acc: int = Form(...),
    total_acc: int = Form(...),
    delinq_2yrs: int = Form(...),
    acc_now_delinq: int = Form(...)
):
    # Gộp dữ liệu từ form vào dict theo TOP5_FEATURES
    data = {
        "int_rate": int_rate,
        "fico_range_low": fico_range_low,
        "funded_amnt": funded_amnt,
        "dti": dti,
        "annual_inc": annual_inc,
        "pub_rec": pub_rec,
        "open_acc": open_acc,
        "total_acc": total_acc,
        "delinq_2yrs": delinq_2yrs,
        "acc_now_delinq": acc_now_delinq
    }

    # Gửi dữ liệu vào Kafka
    send_to_kafka(data)
    return {"message": "Dữ liệu đã được gửi vào Kafka!", "data": data}

@app.on_event("startup")
def startup_event():
    # Khởi chạy consumer chạy nền
    thread = threading.Thread(target=run_consumer, daemon=True)
    thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
