

from __future__ import unicode_literals

import sys
import argparse
import pickledb
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML, ANSI

style = Style.from_dict({
    # Default style.
    '': '#ff0066',

    # Prompt.
    'username': '#884444 italic',
    'at': '#00aa00',
    'colon': '#00aa00',
    'pound': '#00aa00',
    'host': '#000088 bg:#aaaaff',
    'path': '#884444 underline',

    # Make a selection reverse/underlined.
    # (Use Control-Space to select.)
    'selected-text': 'reverse underline',
})


def create_ssh_connection(name, auth):

    prompt_fragments = [('class:username', 'username '), ]
    username = prompt(prompt_fragments, style=style)
    print('username: %s' % username)

    prompt_fragments = [('class:password', 'password '), ]
    password = prompt(prompt_fragments, style=style)
    print('password: %s' % password)

    db = pickledb.load('drt.db', True)
    db.set(f"connection.ssh.{auth}.{name}.username", username)
    db.set(f"connection.ssh.{auth}.{name}.password", password)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=sys.argv[0])
    parser.add_argument('name', help='connection name')
    parser.add_argument('auth', choices=['password', 'publickey'])

    args = parser.parse_args()

    create_ssh_connection(args.name, args.auth)
