import json
import smtplib
import os
import psycopg2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def handler(event: dict, context) -> dict:
    """Обрабатывает решение администратора по заявке (принять/отказать) и уведомляет игрока по почте."""

    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': cors_headers, 'body': ''}

    params = event.get('queryStringParameters') or {}
    token = params.get('token', '').strip()
    action = params.get('action', '').strip()

    if not token or action not in ('accept', 'reject'):
        return _html_response(400, '❌ Неверная ссылка', 'Параметры запроса некорректны.')

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    cur.execute(
        "SELECT id, telegram, minecraft_nick, status FROM t_p12699901_blue_site_submission.applications WHERE token = %s",
        (token,)
    )
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return _html_response(404, '❌ Заявка не найдена', 'Возможно, ссылка устарела или уже была использована.')

    app_id, telegram, minecraft_nick, current_status = row

    if current_status != 'pending':
        cur.close()
        conn.close()
        status_label = 'принята ✅' if current_status == 'accepted' else 'отклонена ❌'
        return _html_response(200, f'Уже обработано', f'Заявка игрока {minecraft_nick} была {status_label} ранее.')

    new_status = 'accepted' if action == 'accept' else 'rejected'
    cur.execute(
        "UPDATE t_p12699901_blue_site_submission.applications SET status = %s WHERE id = %s",
        (new_status, app_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    _send_notification(telegram, minecraft_nick, action)

    if action == 'accept':
        return _html_response(200, '✅ Заявка принята', f'Игрок {minecraft_nick} (@{telegram}) уведомлён о принятии.')
    else:
        return _html_response(200, '❌ Заявка отклонена', f'Игрок {minecraft_nick} (@{telegram}) уведомлён об отказе.')


def _send_notification(telegram: str, minecraft_nick: str, action: str):
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    sender_email = 'sendeu823@gmail.com'

    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = sender_email

    if action == 'accept':
        msg['Subject'] = f'✅ Заявка принята: {minecraft_nick}'
        html_body = f"""
        <html>
        <body style="margin:0;padding:0;background:#050e1f;font-family:'Segoe UI',Arial,sans-serif;">
          <div style="max-width:520px;margin:30px auto;background:#0d1f3c;border:2px solid #1a6aff;border-radius:12px;overflow:hidden;">
            <div style="background:linear-gradient(135deg,#0a3080,#0d1f3c);padding:28px 32px;border-bottom:1px solid #1a3a6a;">
              <div style="font-size:28px;font-weight:900;color:#1a8fff;letter-spacing:3px;">⛏️ СПИРИТ</div>
              <div style="color:#4a90d9;font-size:12px;letter-spacing:2px;margin-top:4px;">РЕШЕНИЕ ПО ЗАЯВКЕ</div>
            </div>
            <div style="padding:32px;">
              <div style="font-size:48px;text-align:center;margin-bottom:20px;">✅</div>
              <h2 style="color:#00e676;font-size:22px;font-weight:900;text-align:center;margin:0 0 12px;letter-spacing:2px;">ЗАЯВКА ПРИНЯТА!</h2>
              <p style="color:#c0d8f0;text-align:center;font-size:15px;margin:0 0 24px;line-height:1.6;">
                Поздравляем, <strong style="color:#ffffff;">{minecraft_nick}</strong>!<br>
                Тебя ждут на приватном сервере Спирит.
              </p>
              <div style="background:#071529;border:1px solid #1a3a6a;border-radius:8px;padding:16px;text-align:center;">
                <div style="color:#4a90d9;font-size:11px;letter-spacing:2px;margin-bottom:8px;">СЛЕДУЮЩИЙ ШАГ</div>
                <div style="color:#ffffff;font-size:14px;">Напиши администратору в Telegram для получения IP сервера</div>
              </div>
            </div>
            <div style="padding:14px 32px;background:#071529;border-top:1px solid #1a3a6a;text-align:center;">
              <span style="color:#2a4a6a;font-size:11px;letter-spacing:1px;">СПИРИТ • ПРИВАТНЫЙ СЕРВЕР</span>
            </div>
          </div>
        </body>
        </html>
        """
        # Отправляем уведомление на основную почту (с пометкой для игрока)
        msg['Subject'] = f'✅ ПРИНЯТ | @{telegram} | {minecraft_nick} — отправьте это игроку'
    else:
        msg['Subject'] = f'❌ ОТКЛОНЁН | @{telegram} | {minecraft_nick} — отправьте это игроку'
        html_body = f"""
        <html>
        <body style="margin:0;padding:0;background:#050e1f;font-family:'Segoe UI',Arial,sans-serif;">
          <div style="max-width:520px;margin:30px auto;background:#0d1f3c;border:2px solid #3a1a1a;border-radius:12px;overflow:hidden;">
            <div style="background:linear-gradient(135deg,#1a0a0a,#0d1f3c);padding:28px 32px;border-bottom:1px solid #3a1a1a;">
              <div style="font-size:28px;font-weight:900;color:#1a8fff;letter-spacing:3px;">⛏️ СПИРИТ</div>
              <div style="color:#4a90d9;font-size:12px;letter-spacing:2px;margin-top:4px;">РЕШЕНИЕ ПО ЗАЯВКЕ</div>
            </div>
            <div style="padding:32px;">
              <div style="font-size:48px;text-align:center;margin-bottom:20px;">❌</div>
              <h2 style="color:#ff4444;font-size:22px;font-weight:900;text-align:center;margin:0 0 12px;letter-spacing:2px;">ЗАЯВКА ОТКЛОНЕНА</h2>
              <p style="color:#c0d8f0;text-align:center;font-size:15px;margin:0 0 24px;line-height:1.6;">
                К сожалению, <strong style="color:#ffffff;">{minecraft_nick}</strong>,<br>
                твоя заявка на сервер Спирит не была одобрена.
              </p>
              <div style="background:#1a0a0a;border:1px solid #3a1a1a;border-radius:8px;padding:16px;text-align:center;">
                <div style="color:#883333;font-size:13px;">Ты можешь попробовать подать заявку повторно позже</div>
              </div>
            </div>
            <div style="padding:14px 32px;background:#071529;border-top:1px solid #1a3a6a;text-align:center;">
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


def _html_response(status_code: int, title: str, message: str) -> dict:
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Спирит</title>
  <style>
    body {{ margin:0; background:#050e1f; font-family:'Segoe UI',Arial,sans-serif; display:flex; align-items:center; justify-content:center; min-height:100vh; }}
    .card {{ background:#0d1f3c; border:2px solid #1a6aff; border-radius:12px; padding:48px 40px; text-align:center; max-width:420px; }}
    h1 {{ color:#1a8fff; font-size:24px; font-weight:900; margin:0 0 16px; letter-spacing:2px; }}
    p {{ color:#7ab0d8; font-size:15px; line-height:1.6; margin:0; }}
    .logo {{ font-size:22px; font-weight:900; color:#1a8fff; letter-spacing:3px; margin-bottom:28px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">⛏️ СПИРИТ</div>
    <h1>{title}</h1>
    <p>{message}</p>
  </div>
</body>
</html>"""
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'text/html; charset=utf-8', 'Access-Control-Allow-Origin': '*'},
        'body': html
    }
