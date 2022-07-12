import os
import click
import uvicorn
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'auction.settings'
django.setup()


from django.core import management

import act.app


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    '--collectstatic/--no-collectstatic',
    is_flag=True,
    default=True,
    help='Collect Django static',
)
@click.option(
    '--uvicorn-debug/--no-uvicorn-debug',
    is_flag=True,
    default=True,
    help='Enable/Disable debug and auto-reload',
)
def web(collectstatic: bool, uvicorn_debug: bool):

    app = act.app.app

    if uvicorn_debug:
        # Автоперезапуск при изменении кода: uvicorn.config.Config.should_reload
        # Удобно при локальной разработке
        app = 'act.app:app'

    if collectstatic:
        management.call_command('collectstatic', '--no-input', '--clear')

    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        debug=uvicorn_debug,
        access_log=False,
        log_config=None,
        lifespan='on',
        loop='uvloop',
    )


if __name__ == '__main__':
    cli()
