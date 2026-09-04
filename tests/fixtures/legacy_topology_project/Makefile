CC = gcc
CFLAGS = -Wall -O2

all: engine

engine: src/core_engine.c
	$(CC) $(CFLAGS) -o bin/engine src/core_engine.c

test:
	./scripts/test.sh

clean:
	rm -rf bin/engine
