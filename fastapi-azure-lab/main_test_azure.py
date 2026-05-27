from fastapi import FastAPI
import os

app = FastAPI(
    title="UMT Cloud Testing API",
    description="Hệ thống API kiểm thử triển khai trên hạ tầng Azure App Service",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "message": "Chuc mung! API cua em da song thuc te tren Internet thong qua Azure Cloud.",
        "server_location": "Southeast Asia Datacenter"
    }

@app.get("/student")
def get_student_info():
    # SINH VIÊN SỬA LẠI THÔNG TIN CÁ NHÂN ĐỂ GIẢNG VIÊN CHECKPOINT CHẤM ĐIỂM
    return {
        "class_code": "BIT312V1",
        "student_name": "Nguyen Van A",
        "student_id": "231080001",
        "project": "Lab 3 - Cloud Deployment"
    }