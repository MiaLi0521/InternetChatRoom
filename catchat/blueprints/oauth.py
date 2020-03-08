import os
from urllib.parse import urljoin

import requests
from requests.exceptions import ConnectionError
from flask import Blueprint, flash, redirect, url_for, abort, current_app, request
from flask_login import login_user, current_user

from catchat.extensions import db
from catchat.model import User

oauth_bp = Blueprint('oauth', __name__)

github = dict(
    name='github',
    consumer_key='GITHUB_CLIENT_ID',
    consumer_secret='GITHUB_CLIENT_SECRET',
    request_token_params={'scope': 'user'},
    base_url='https://api.github.com/',
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
)

google = dict(
    name='google',
    consumer_key='GOOGLE_CLIENT_ID',
    consumer_secret='GOOGLE_CLIENT_SECRET',
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

providers = {
    'github': github,
    'google': google,
}

profile_endpoints = {
    'github': 'user',
    'google': 'userinfo',
}


def get_social_profile(provider, access_token_response):
    token_type = access_token_response.json().get('token_type')
    token = access_token_response.json().get('access_token')
    headers = {
        'Authorization': '{} {}'.format(token_type, token),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'keep-live': 'false',
    }
    try:
        response = requests.get(provider['base_url'] + provider['request_token_params'].get('scope'), headers=headers)
        print(response.text)
    except ConnectionError:
        return
    if response.status_code != 200:
        return

    if provider.get('name') == 'google':
        username = response.json().get('name')
        website = response.json().get('link')
        github = ''
        email = response.json().get('email')
        bio = ''
    else:
        username = response.json().get('name')
        website = response.json().get('blog')
        github = response.json().get('html_url')
        email = response.json().get('email')
        bio = response.json().get('bio')
    return username, website, github, email, bio


@oauth_bp.route('/login/<provider_name>')
def oauth_login(provider_name):
    if provider_name not in providers.keys():
        abort(404)

    if current_user.is_authenticated:
        return redirect(url_for('chat.home'))

    callback = url_for('.oauth_callback', provider_name=provider_name, _external=True)
    provider = providers[provider_name]
    client_id = current_app.config[provider['consumer_key']]
    query_str = '?client_id={}&scope={}&redirect_uri={}'.format(client_id, 'user:email', callback)
    authorize_url = urljoin(provider.get('authorize_url'), query_str)
    return redirect(authorize_url)


@oauth_bp.route('/callback/<provider_name>')
def oauth_callback(provider_name):
    if provider_name not in providers.keys():
        abort(404)

    provider = providers[provider_name]
    data = {
        'client_id': current_app.config[provider['consumer_key']],
        'client_secret': current_app.config[provider['consumer_secret']],
        'code': request.args.get('code')
    }
    headers = {
        'Accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'keep-live': 'false',
    }
    try:
        response = requests.post(provider['access_token_url'], data=data, headers=headers)
    except ConnectionError:
        flash('Connection Error, please try again.')
        return redirect(url_for('auth.login'))
    if response.status_code != 200 or response.json().get('access_token') is None:
        flash('Access denied, please try again.')
        return redirect(url_for('auth.login'))

    response = get_social_profile(provider, response)
    if response is None:
        flash('Get profile failed, please try again.')
        return redirect(url_for('auth.login'))

    # 使用access_token获取用户信息
    username, website, github, email, bio = response
    if email is None:
        flash('Please set a public email.Because we need to get your email.')
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email, nickname=username, website=website, github=github, bio=bio)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('chat.profile'))
    login_user(user, remember=True)
    return redirect(url_for('chat.home'))

