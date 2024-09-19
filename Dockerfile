FROM python:3.10-alpine

WORKDIR /home/bringauto

COPY requirements.txt /home/bringauto/
RUN pip install --no-cache-dir -r requirements.txt

COPY log /home/bringauto/log
COPY config /home/bringauto/config
COPY fleet_management_api /home/bringauto/fleet_management_api

EXPOSE 8080

ENTRYPOINT ["python"]
CMD ["-m", "fleet_management_api", "config/config.json"]
