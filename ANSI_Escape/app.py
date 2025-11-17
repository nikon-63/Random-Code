from flask import Flask, Response
import random, string

app = Flask(__name__)

def hide_flag(message, total_lines = 50, line_length = 100):
    message = message.replace(" ", "_")  # Remove spaces as look odd in grid
    noise_chars = string.ascii_uppercase
    message = message.upper()
    # Different shades of gray in 256-color ANSI so they blend well but also when looking from browser they all have colour code marking so the hidden flah dose not stand out as being the only one without a colour code.
    noise_colors = [
    "38;5;232", "38;5;233", "38;5;234",
    "38;5;235", "38;5;236", "38;5;237",
    "38;5;238", "38;5;239"
    ]
    # Makes the flag characters red on yellow background to stand out.
    flag_style = "1;31;103"

    # Basic checks
    total_cells = total_lines * line_length
    if len(message) > total_cells:
        raise ValueError("Message longer than total grid cells.")

    flag_positions = sorted(random.sample(range(total_cells), len(message)))
    pos_iter = iter(flag_positions)
    next_flag_pos = next(pos_iter, None)

    msg_iter = iter(message)
    lines = []
    cell_index = 0

    # Randomly fill the grid with noise and flag characters
    for _ in range(total_lines):
        parts = []
        for _ in range(line_length):
            if next_flag_pos is not None and cell_index == next_flag_pos:
                ch = next(msg_iter)
                parts.append(f"\033[{flag_style}m{ch}\033[0m")
                next_flag_pos = next(pos_iter, None)
            else:
                noise_ch = random.choice(noise_chars)
                color = random.choice(noise_colors)
                parts.append(f"\033[{color}m{noise_ch}\033[0m")

            cell_index += 1
        lines.append("".join(parts))

    return "\n".join(lines) + "\n"

@app.route("/")
def home():
    # Hidden message here
    body = hide_flag("Top Secret Message")
    return Response(body, mimetype="text/plain; charset=utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)