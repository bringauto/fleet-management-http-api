FROM bringauto/python-environment:latest

WORKDIR /home/bringauto

COPY ./requirements.txt /home/bringauto
RUN "$PYTHON_ENVIRONMENT_PYTHON3" -m pip install --no-cache-dir -r requirements.txt

COPY config /home/bringauto/config
COPY fleet_management_api /home/bringauto/fleet_management_api

EXPOSE 8080

USER 5000:5000
RUN mkdir /home/bringauto/log

ENTRYPOINT ["bash", "-c", "$PYTHON_ENVIRONMENT_PYTHON3 -m fleet_management_api $0 $@"]
CMD ["config/config.json"]
