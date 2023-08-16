FROM python:3.11

WORKDIR /bot

COPY requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY .. .

CMD ["python", "main.py"]