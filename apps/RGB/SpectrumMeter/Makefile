CC      := gcc
CFLAGS  := -Wall -Wextra -O2 `pkg-config --cflags libpulse-simple`
LDFLAGS := -pthread -lm `pkg-config --libs libpulse-simple`
PROGS   := vu-bar

all: clean $(PROGS)

.PHONY: clean
clean:
	rm -f *.o $(PROGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $^

vu-bar: gui.o vu.o
	$(CC) $(CFLAGS) $^ $(LDFLAGS) -o $@
