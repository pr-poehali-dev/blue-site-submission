import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def handler(event: dict, context) -> dict:
    """Принимает заявку на вступление в приватный сервер и отправляет её на почту администратора."""

    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': cors_headers, 'body': ''}

    raw_body = event.get('body') or '{}'
    body = json.loads(raw_body)
    telegram = body.get('telegram', '').strip()
    minecraft_nick = body.get('minecraft_nick', '').strip()

    if not telegram or not minecraft_nick:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Заполните все поля'})
        }

    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    sender_email = 'sendeu823@gmail.com'
    receiver_email = 'sendeu823@gmail.com'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Новая заявка на вступление: {minecraft_nick}'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: #0a1628; color: #e0f0ff; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #0d2040; border: 2px solid #1e90ff; border-radius: 8px; padding: 30px;">
            <h2 style="color: #1e90ff; margin-top: 0;">⛏️ Новая заявка на сервер</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px; color: #7fb3d3; font-weight: bold;">Telegram:</td>
                    <td style="padding: 10px; color: #ffffff; font-size: 16px;">{telegram}</td>
                </tr>
                <tr style="background: #0a1628;">
                    <td style="padding: 10px; color: #7fb3d3; font-weight: bold;">Ник в игре:</td>
                    <td style="padding: 10px; color: #ffffff; font-size: 16px;">{minecraft_nick}</td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({'success': True, 'message': 'Заявка отправлена!'})
    }