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

### Expanding local includes

The command
```bash
cpt expand file.cpp
```
prints the content of `file.cpp` with local includes
(from the directory `include` in competitive programming tools)
replaced with their contents recursively.
This allows you to put data structures and algorithms in their
own files and include instead of copy pasting.

Here is how i use it:
```vim
nnoremap <F9> :w<enter>:!echo %:p \| cpt expand - --tmp-file \| wl-copy<enter><enter>
nnoremap <F10> :w<enter>:!echo %:p \| cpt expand - \| wl-copy<enter><enter>
```
Putting these lines in the vim configuration lets you
hit F9 to put the expanded source code in a temporary file,
and copies the path of the temporary file to the clipboard.
Hitting F10 puts the expanded source code directly in the clipboard.
I use both because it differs between online judges wether
submitting by pasting or by uploading a file is easier.
