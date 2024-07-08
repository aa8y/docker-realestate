FROM python:3.12

WORKDIR app/

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app.py ./
ENTRYPOINT ["python"]
CMD ["app.py"]
