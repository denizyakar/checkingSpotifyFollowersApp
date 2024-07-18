from flask import Flask, request, redirect, make_response
import requests

app = Flask(__name__)

CLIENT_ID = 'CLIENT ID BURAYA'  # Spotify Developer Dashboard'dan aldığın Client ID
CLIENT_SECRET = 'CLIENT SECRET BURAYA'  # Spotify Developer Dashboard'dan aldığın Client Secret
REDIRECT_URI = 'http://localhost:8888/callback'  # Spotify Developer Dashboard'da belirlediğin Redirect URI
SCOPE = 'user-follow-read'

@app.route('/user_input')
def user_input():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>User Input</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #28a745; /* Yeşil arka plan */
                color: #fff; /* Beyaz yazı rengi */
            }
            .container {
                margin-top: 50px;
            }
            .btn-primary {
                background-color: #007bff; /* Mavi buton rengi */
                border-color: #007bff;
            }
            .btn-primary:hover {
                background-color: #0056b3; /* Koyu mavi hover efekti */
                border-color: #004085;
            }
            .form-control {
                margin-bottom: 10px;
            }
            h1 {
                color: #fff; /* Beyaz başlık rengi */
                margin-top: 50px;
            }
            .result {
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center">Login</h1>
            <form action="/check_following" method="post">
                <div class="form-group">
                    <label for="user_id">ID of the authorized user:</label>
                    <input type="text" class="form-control" id="user_id" name="user_id" required>
                </div>
                <div class="form-group">
                    <label for="target_user_id">ID of the user that will be checked if is being followed:</label>
                    <input type="text" class="form-control" id="target_user_id" name="target_user_id" required>
                </div>
                <button type="submit" class="btn btn-primary btn-block">Is Following?</button>
            </form>
        </div>
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>
    </html>
    '''

@app.route('/check_following', methods=['POST'])
def check_following():
    target_user_id = request.form['target_user_id']
    access_token = request.cookies.get('access_token')

    if access_token:
        is_following = check_if_user_follows(access_token, target_user_id)
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Result</title>
            <style>
                body {{
                    background-color: #28a745; /* Yeşil arka plan */
                    color: #fff; /* Beyaz yazı rengi */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .result {{
                    font-size: 36px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 200px;
                }}
            </style>
        </head>
        <body>
            <div class="result">
                Is following: {is_following}
            </div>
        </body>
        </html>
        '''
    else:
        return 'You need to Authorize first.'

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Spotify Follower Check</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #28a745; /* Yeşil arka plan */
                color: #fff; /* Beyaz yazı rengi */
            }
            .container {
                margin-top: 100px; /* Başlığı yukarı taşır */
            }
            .btn-primary {
                background-color: #007bff; /* Mavi buton rengi */
                border-color: #007bff;
            }
            .btn-primary:hover {
                background-color: #0056b3; /* Koyu mavi hover efekti */
                border-color: #004085;
            }
            h1 {
                color: #fff; /* Beyaz başlık rengi */
                margin-bottom: 30px; /* Başlık ve buton arasına boşluk ekler */
            }
        </style>
    </head>
    <body>
        <div class="container text-center">
            <h1>Spotify Follower Check</h1>
            <form action="/login" method="post">
                <button type="submit" class="btn btn-primary btn-block">Authorize</button>
            </form>
        </div>
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>
    </html>
    '''

@app.route('/login', methods=['POST'])
def login():
    auth_url = (
        'https://accounts.spotify.com/authorize'
        '?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&scope={SCOPE}'
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')

    token_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(token_url, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    response_data = response.json()

    # Token'ı kontrol et
    if 'access_token' in response_data:
        access_token = response_data['access_token']
        response = redirect('/user_input')
        response.set_cookie('access_token', access_token)
        return response
    else:
        return f"Hata: {response_data}"

def check_if_user_follows(access_token, target_user_id):
    url = f'https://api.spotify.com/v1/me/following/contains?type=user&ids={target_user_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)

    print(response.status_code)
    print(response.json())

    if response.status_code == 200:
        return response.json()[0]  # İlk eleman true/false dönecek
    else:
        return f"Hata: {response.status_code}, Mesaj: {response.json()}"

if __name__ == '__main__':
    app.run(debug=True, port=8888)
