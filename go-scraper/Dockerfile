# Build stage
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o scraper ./cmd/scraper

# Run stage
FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/scraper /app/scraper

# Create config and data directories
RUN mkdir -p /app/config /app/data

ENTRYPOINT ["/app/scraper"]