#!/usr/bin/env python
from __future__ import print_function
from collections import Mapping
from collections import namedtuple
from collections import OrderedDict
from collections import Set
from itertools import islice
from os import path
from random import choice
from random import random
from random import randrange
from threading import Lock
from sys import argv

from yaml import load


Character = namedtuple('Character', ['name', 'tags'])
Template = namedtuple('Template', ['text', 'weight'])


weight_main = 3
characters = None
template_table = None
with open(path.join(path.dirname(__file__), 'static/config.yml')) as f:
    config = load(f)
    weight_main = config.get('weight_main', weight_main)
    characters = [Character(**c) for c in config.get('characters', [])]
    templates = []
    for t in config.get('templates', []):
        if isinstance(t, Mapping):
            templates.append(Template(**t))
        else:
            templates.append(Template(str(t), 1))
    total = sum((t.weight for t in templates))
    template_table = []
    position = 0.0
    for t in templates:
        position += t.weight
        template_table.append((position / total, t.text))


def get_template():
    try:
        position = random()
        return (v for k, v in template_table if position < k).next()
    except StopIteration:
        return '%()s kills %()s'


class CharacterSelector(Mapping):
    lock = Lock()
    chosen = []

    def get(self, tags, main=False):
        matching = None
        if tags:
            if not isinstance(tags, Set):
                tags = set(tags.split(','))
            if main:
                tags.add('main')
            matching = [c.name for c in characters if c.name not in self.chosen
                        and tags.issubset(c.tags)]
            return matching and choice(matching)
        elif main:
            matching = [c.name for c in characters if c.name not in self.chosen
                        and 'main' in c.tags]
        else:
            matching = [c.name for c in characters if
                        c.name not in self.chosen]
        return matching and choice(matching)

    def __getitem__(self, key):
        name = None
        if randrange(weight_main):
            name = self.get(key, True)
        name = name or self.get(key, False) or 'George R. R. Martin'
        self.chosen.append(name)
        return name

    def __len__(self):
        return len(characters)

    def __iter__(self):
        for character in characters:
            yield character.name

    def keys(self):
        return list(reduce(lambda x, y: x.union(y.tags), characters,
                           frozenset()))

    def items(self):
        for tag in self.keys():
            yield (tag, [c.name for c in characters if tag in c.tags])

    def values(self):
        return list(self)

    def populate(self, template):
        try:
            self.lock.acquire()
            self.chosen = []
            s = template % self
            return s[0].upper() + s[1:]
        finally:
            self.lock.release()


def iterator():
    selector = CharacterSelector()
    while True:
        yield selector.populate(get_template())


if __name__ == '__main__':
    print('%d main characters' % len([c for c in characters 
          if 'main' in c.tags]))
    print('%d minor characters' % len([c for c in characters 
          if 'main' not in c.tags]))
    print('%d templates' % len(templates))
    count = 1
    try:
        count = int(argv[1])
    except:
        pass
    for s in islice(iterator(), count):
        print(s)
