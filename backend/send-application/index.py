import json
import smtplib
import os
import secrets
import psycopg2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def handler(event: dict, context) -> dict:
    """Принимает заявку на вступление в приватный сервер, сохраняет в БД и отправляет письмо с кнопками Принять/Отказать."""

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

    token = secrets.token_urlsafe(32)

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO t_p12699901_blue_site_submission.applications (telegram, minecraft_nick, token) VALUES (%s, %s, %s) RETURNING id",
        (telegram, minecraft_nick, token)
    )
    conn.commit()
    cur.close()
    conn.close()

    accept_url = f'https://functions.poehali.dev/8fa2983f-f706-4830-980f-6a2eecb87e48?token={token}&action=accept'
    reject_url = f'https://functions.poehali.dev/8fa2983f-f706-4830-980f-6a2eecb87e48?token={token}&action=reject'

    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    sender_email = 'sendeu823@gmail.com'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'⛏️ Новая заявка на Спирит: {minecraft_nick}'
    msg['From'] = sender_email
    msg['To'] = sender_email

    html_body = f"""
    <html>
    <body style="margin:0;padding:0;background:#050e1f;font-family:'Segoe UI',Arial,sans-serif;">
      <div style="max-width:520px;margin:30px auto;background:#0d1f3c;border:2px solid #1a6aff;border-radius:12px;overflow:hidden;">

        <div style="background:linear-gradient(135deg,#0a3080,#0d1f3c);padding:28px 32px;border-bottom:1px solid #1a3a6a;">
          <div style="font-size:28px;font-weight:900;color:#1a8fff;letter-spacing:3px;">⛏️ СПИРИТ</div>
          <div style="color:#4a90d9;font-size:12px;letter-spacing:2px;margin-top:4px;">ПРИВАТНЫЙ СЕРВЕР — НОВАЯ ЗАЯВКА</div>
        </div>

        <div style="padding:28px 32px;">
          <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
            <tr>
              <td style="padding:12px 16px;color:#4a90d9;font-weight:700;font-size:13px;letter-spacing:1px;background:#071529;border-radius:6px 0 0 6px;width:40%;">TELEGRAM</td>
              <td style="padding:12px 16px;color:#ffffff;font-size:15px;font-weight:600;background:#0a1e36;border-radius:0 6px 6px 0;">@{telegram}</td>
            </tr>
            <tr><td colspan="2" style="height:6px;"></td></tr>
            <tr>
              <td style="padding:12px 16px;color:#4a90d9;font-weight:700;font-size:13px;letter-spacing:1px;background:#071529;border-radius:6px 0 0 6px;">НИК В ИГРЕ</td>
              <td style="padding:12px 16px;color:#ffffff;font-size:15px;font-weight:600;background:#0a1e36;border-radius:0 6px 6px 0;">{minecraft_nick}</td>
            </tr>
          </table>

          <div style="display:flex;gap:12px;margin-top:8px;">
            <a href="{accept_url}" style="display:inline-block;flex:1;padding:14px 0;background:#1a6aff;color:#ffffff;font-weight:900;font-size:14px;letter-spacing:2px;text-decoration:none;border-radius:8px;text-align:center;box-shadow:0 0 20px rgba(26,106,255,0.4);">
              ✅ &nbsp;ПРИНЯТЬ
            </a>
            <a href="{reject_url}" style="display:inline-block;flex:1;padding:14px 0;background:#1a1a2e;color:#ff4444;font-weight:900;font-size:14px;letter-spacing:2px;text-decoration:none;border-radius:8px;text-align:center;border:2px solid #3a1a1a;">
              ❌ &nbsp;ОТКАЗАТЬ
            </a>
          </div>
        </div>

        <div style="padding:16px 32px;background:#071529;border-top:1px solid #1a3a6a;text-align:center;">
          <span style="color:#2a4a6a;font-size:11px;letter-spacing:1px;">СПИРИТ • ПРИВАТНЫЙ СЕРВЕР</span>
        </div>
      </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, smtp_password)
        server.sendmail(sender_email, sender_email, msg.as_string())

    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({'success': True})
    }