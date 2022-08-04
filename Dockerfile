FROM python:3.8
LABEL maintainer="Dzung Do"

EXPOSE 3111

COPY ./techtrends /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python init_db.py

CMD ["python", "app.py"]