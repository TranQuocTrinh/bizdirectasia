import deathbycaptcha

# Put your DBC account username and password here.
username = "henryvn2004@gmail.com"
password = "Saigon123"
captcha_file = 'captcha.png'  # image

client = deathbycaptcha.SocketClient(username, password)
#to use http client client = deathbycaptcha.HttpClient(username, password)
def get_captcha(captcha_file):
    try:
        balance = client.get_balance()

        # Put your CAPTCHA file name or file-like object, and optional
        # solving timeout (in seconds) here:
        captcha = client.decode(captcha_file, type=2)
        if captcha:
            # The CAPTCHA was solved; captcha["captcha"] item holds its
            # numeric ID, and captcha["text"] item its list of "coordinates".
            print("CAPTCHA %s solved: %s" % (captcha["captcha"], captcha["text"]))

            if '':  # check if the CAPTCHA was incorrectly solved
                client.report(captcha["captcha"])
            return str(captcha["text"])
    except deathbycaptcha.AccessDeniedException:
        # Access to DBC API denied, check your credentials and/or balance
        print ("error: Access to DBC API denied, check your credentials and/or balance")
        return ""
