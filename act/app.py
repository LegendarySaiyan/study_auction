from fastapi_jsonrpc import *
from act.api.api import api_v1

from django.core.asgi import get_asgi_application
from starlette.responses import RedirectResponse

app = API(
    title='AUCTION')

app.bind_entrypoint(api_v1)


@app.get('/', include_in_schema=False)
async def redirect_to_docs():
    response = RedirectResponse(url='/docs')
    return response


app.mount('/app', app=get_asgi_application())
