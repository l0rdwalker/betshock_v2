FROM alpine:edge

EXPOSE 8080
EXPOSE 8081

RUN apk add --no-cache gettext
RUN apk --update add privoxy openvpn runit

COPY app /app

RUN find /app -name run | xargs chmod u+x

ENV OPENVPN_FILENAME=au-bne.prod.surfshark.comsurfshark_openvpn_tcp \
    LOCAL_NETWORK=10.16.5.111/21 \
    ONLINECHECK_DELAY=900

CMD ["runsvdir", "/app"]
