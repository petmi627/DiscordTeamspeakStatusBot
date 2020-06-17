FROM python:3

MAINTAINER Mike Peters "mike@skylake.me"

COPY ./requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

COPY ./discord_teampeak_status-bot.py /discord_teampeak_status-bot.py
WORKDIR /

CMD ["python", "discord_teampeak_status-bot.py"]