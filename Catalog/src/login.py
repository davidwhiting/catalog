### Move the below to the right place

#@app('/login')
#async def login(q: Q):
#    if 'token' not in q.client:
#        q.page['form'] = ui.form_card(box='1 1 4 4', items=[
#            ui.text_l('Please login'),
#            ui.button(name='login', label='Login', primary=True)
#        ])
#    else:
#        q.page['form'] = ui.form_card(box='1 1 4 4', items=[
#            ui.text_l(f'Hello, {q.client.user["preferred_username"]}'),
#            ui.button(name='logout', label='Logout', primary=True)
#        ])
#    await q.page.save()
#
#@app('/callback')
#async def callback(q: Q):
#    code = q.args['code']
#    result = msal_app.acquire_token_by_authorization_code(
#        code,
#        scopes=SCOPE,
#        redirect_uri=REDIRECT_URI
#    )
#    if 'access_token' in result:
#        q.client.token = result['access_token']
#        userinfo_endpoint = os.getenv('REQUESTS_GET_ADDRESS')
#        q.client.user = requests.get(
#            userinfo_endpoint,
#            headers={'Authorization': f'Bearer {q.client.token}'}
#        ).json()
#        await serve(q)
#    else:
#        q.page['form'] = ui.form_card(box='1 1 4 4', items=[
#            ui.text_l('Login failed. Please try again.')
#        ])
#        await q.page.save()
#
#@app('/')
#async def serve(q: Q):
#    if q.args.login:
#        auth_url = msal_app.get_authorization_request_url(
#            SCOPE, redirect_uri=REDIRECT_URI
#        )
#        q.page['redirect'] = ui.redirect(auth_url)
#    elif q.args.logout:
#        q.client.token = None
#        q.client.user = None
#        await login(q)
#    else:
#        await login(q)
