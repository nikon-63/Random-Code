# ANSI Escape Hidden Message

Example demonstrating how ANSI escape codes to hide messages on a webpage—nearly invisible in a browser but revealed when fetched with curl in a terminal.

## Build and Run
```
make build
make run
```

## Usage

Then visit `http://localhost:8080` in a browser to see the all the random characters. Then run `curl http://localhost:8080` in a terminal to reveal the hidden message.

## Cleanup
```
make remove
```