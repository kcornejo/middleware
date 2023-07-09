FROM python:3.10.9-alpine

ENV NAME_DB=<DB_NAME_SECRET>
ENV HOST_DB=<DB_HOST_SECRET>
ENV USER_DB=<DB_USER_SECRET>
ENV PW_DB=<DB_PASS_SECRET>
ENV PORT_DB=<DB_PORT_SECRET>
ENV HOST=<HOST>
ENV PORT=<PORT>

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD [ "python", "api.py" ]