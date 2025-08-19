FROM python:3.12.11

WORKDIR /opt/ic_responses

COPY requirements.txt ./

RUN apt update && apt -y install vim locales locales-all
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV LC_ALL=nl_NL.UTF-8
ENV LANG=nl_NL.UTF-8
ENV LANGUAGE=nl_NL.UTF-8

CMD ["tail", "-f", "requirements.txt"]