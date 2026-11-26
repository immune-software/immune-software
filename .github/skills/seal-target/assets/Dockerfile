FROM python:3.13-alpine
RUN apk add --no-cache age && pip -q install bit==0.8.0
COPY seal.sh /bounty/
RUN sh /bounty/seal.sh
CMD ["cat", "/bounty/bounty.age"]
