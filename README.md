# Competitive Programming Tools
My tools, templates, and structures for programming competitions.

```bash
> cpt --help
```
```
Usage: cpt [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  flush   Clears temporary data stored by copetitive programming tools.
  get     Given a the name of a snippet, print the content it to stdout.
  listen  Listen for information about problems from the "Competitive...
  mk      Create a file containing snippets/main
  mke     Create a file containing snippets/main and open it in $EDITOR
  run     Executes a program from source.
```

## Example usage
![example-usage](./doc/example_usage.gif)

## Platform support
No.

I only tested this on my own computer running linux.

## Installation

- Install python3, pip, and g++.
- Clone this repository
- `cd` into it

- run this (maybe `pip3` instead of `pip` depending on platform)
```bash
> pip install . -e
```
- Figure out where pip put the scripts and add that folder to $PATH.
In my case that would be adding this to my `.bashrc`:
```bash
export PATH=$PATH:~/.local/bin/
```

## Tips and Tricks

### Getting snippets with a shortcut

The command
```bash
cpt get -
```
reads the name of the snippet you wanna get from `stdin`, and
```bash
cpt get --list
```
lists all available snippets.
This can be combined into something that
asks to pick a snippet name and then prints it:
```bash
cpt get --list | dmenu | cpt get -
```
Then adding for example this:
```vim
nnoremap <M-s> <ESC>:read !cpt get --list \| dmenu \| cpt get - 2>/dev/null<enter><enter>
```
to `init.vim` lets you press a short cut (`alt`+`s` here) that opens a menu asking to select a snippet,
and then pastes the snippet in at cursor position.

## Future plans
- Add more useful snippets
- Maybe make it work on windows
