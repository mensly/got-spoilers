from pyramid.view import view_config
from spoilers import iterator
from random import choice

music = [('goats', 'X6tKZ-cg4RI'),
         ('wiener', 'XifUlSyQ2CI')
         ]

spoiler_iter = iterator()


@view_config(route_name='home', renderer='templates/index.pt')
def my_view(request):
    spoiler = spoiler_iter.next()
    if 'Tyrion' in spoiler:
        music_file = 'dinklage'
        music_src = 'DHlzIgSvnYc'
    else:
        music_file, music_src = choice(music)
    return dict(spoiler=spoiler,
                music_file=music_file,
                music_src=music_src)


@view_config(route_name='spoiler', renderer='templates/simple.pt')
def spoiler(request):
    return dict(spoiler=spoiler_iter.next())
