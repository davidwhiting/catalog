from h2o_wave import main, app, Q, ui


@app('/')
async def serve(q: Q):
    q.page['hello'] = ui.markdown_card(
        box='1 1 4 4',
        title='HF Spaces tutorial',
        content='Hello World!'
    )
    await q.page.save()
