# bbcli


Browse BBC News from the comand line. (Based on pyhackernews)

![demo2](https://github.com/user-attachments/assets/71ceb6e8-1345-451e-8523-d792b68804c6)


# Installation & Usage:

```
python3 -m venv .venv

source .venv/bin/activate

pip3 install .
```
`bbcli`

# Configuration:

Custom keybindings can be defined in either:

`$HOME/.bbcli`

Or:

`$HOME/.config/bbcli`

Like so:

    [Keys]
    quit = q
    open = w
    tabopen = O
    refresh = r
    latest = l
    scroll_up = k
    scroll_down = j
    bottom = G

    [Commands]
    ; %URL is a placeholder for where the actual URL will be inserted.
    ; Remove these if unused.

    open = dwbremote :open %URL
    tabopen = dwbremote :tabopen %URL
