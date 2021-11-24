import requests

def subscription_success_mail(email):
    url = "https://api.zuri.chat/external/send-mail?custom_mail=1"
    payload = {
        "email": email,
        "subject": "Subscription Successful",
        "content_type": "text/html",
        "mail_body": '<div style="background-color: chocolate; width: 100%; height: 30%;"><h1 style="color: white; text-align: center; padding: 1em">Noticeboard Plugin</h2></div><div style="margin: 0% 5% 10% 5%;"><p>Hey!</p><br><p>You have successfully subscribed to receiving email notifications when there is a new notice on the Noticeboard Plugin.</p><p>We will keep you updated about notices.</p><br><p>Cheers,</p><p>Noticeboard Plugin</p><p><a href="https://zuri.chat/">zuri chat</a></p></div>',
    }
    response_email = requests.post(url=url, json=payload)
