import json
import smtplib
import os
import psycopg2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


CARD_NUMBER = '2200 2418 1268 4441'
AMOUNT = '100'
SENDER_EMAIL = 'sendeu823@gmail.com'


def handler(event: dict, context) -> dict:
    """Обрабатывает решение администратора по заявке и отправляет письмо напрямую игроку."""

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': ''}

    params = event.get('queryStringParameters') or {}
    token = params.get('token', '').strip()
    action = params.get('action', '').strip()

    if not token or action not in ('accept', 'reject'):
        return _html_response(400, '❌ Неверная ссылка', 'Параметры запроса некорректны.')

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    cur.execute(
        "SELECT id, telegram, minecraft_nick, email, status FROM t_p12699901_blue_site_submission.applications WHERE token = %s",
        (token,)
    )
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return _html_response(404, '❌ Заявка не найдена', 'Возможно, ссылка устарела.')

    app_id, telegram, minecraft_nick, player_email, current_status = row

    if current_status != 'pending':
        cur.close()
        conn.close()
        label = 'принята ✅' if current_status == 'accepted' else 'отклонена ❌'
        return _html_response(200, 'Уже обработано', f'Заявка игрока {minecraft_nick} была {label} ранее.')

    new_status = 'accepted' if action == 'accept' else 'rejected'
    cur.execute(
        "UPDATE t_p12699901_blue_site_submission.applications SET status = %s WHERE id = %s",
        (new_status, app_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    smtp_password = os.environ.get('SMTP_PASSWORD', '')

    if action == 'accept':
        _send_accept(player_email, minecraft_nick, smtp_password)
        return _html_response(200, '✅ Принято', f'Игрок {minecraft_nick} (@{telegram}) получил письмо с инструкцией об оплате.')
    else:
        _send_reject(player_email, minecraft_nick, smtp_password)
        return _html_response(200, '❌ Отклонено', f'Игрок {minecraft_nick} (@{telegram}) получил письмо об отказе.')


def _send_accept(player_email: str, minecraft_nick: str, smtp_password: str):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '✅ Поздравляем! Ваша заявка на сервер Спирит одобрена'
    msg['From'] = SENDER_EMAIL
    msg['To'] = player_email

    html = f"""
    <html>
    <body style="margin:0;padding:0;background:#050e1f;font-family:'Segoe UI',Arial,sans-serif;">
      <div style="max-width:520px;margin:30px auto;background:#0d1f3c;border:2px solid #1a6aff;border-radius:12px;overflow:hidden;">

        <div style="background:linear-gradient(135deg,#0a3080,#0d1f3c);padding:28px 32px;border-bottom:1px solid #1a3a6a;">
          <div style="font-size:26px;font-weight:900;color:#1a8fff;letter-spacing:3px;">⛏️ СПИРИТ</div>
          <div style="color:#4a90d9;font-size:12px;letter-spacing:2px;margin-top:4px;">ПРИВАТНЫЙ СЕРВЕР</div>
        </div>

        <div style="padding:32px;">
          <div style="font-size:52px;text-align:center;margin-bottom:16px;">🎉</div>
          <h2 style="color:#00e676;font-size:22px;font-weight:900;text-align:center;margin:0 0 12px;letter-spacing:1px;">
            ПОЗДРАВЛЯЕМ, {minecraft_nick.upper()}!
          </h2>
          <p style="color:#c0d8f0;text-align:center;font-size:15px;margin:0 0 28px;line-height:1.7;">
            Твоя заявка на приватный сервер <strong style="color:#ffffff;">Спирит</strong> одобрена!<br>
            Осталось сделать последний шаг.
          </p>

          <div style="background:#071e3d;border:2px solid #1a6aff;border-radius:10px;padding:24px;margin-bottom:24px;">
            <div style="color:#4a90d9;font-size:11px;font-weight:700;letter-spacing:2px;text-align:center;margin-bottom:16px;">
              ДЛЯ ПОЛУЧЕНИЯ ДОСТУПА К СЕРВЕРУ
            </div>

            <div style="background:#0a1628;border-radius:8px;padding:16px;margin-bottom:12px;text-align:center;">
              <div style="color:#7ab0d8;font-size:12px;letter-spacing:1px;margin-bottom:8px;">СУММА ОПЛАТЫ</div>
              <div style="color:#00e676;font-size:36px;font-weight:900;letter-spacing:2px;">{AMOUNT} ₽</div>
            </div>

            <div style="background:#0a1628;border-radius:8px;padding:16px;text-align:center;">
              <div style="color:#7ab0d8;font-size:12px;letter-spacing:1px;margin-bottom:10px;">НОМЕР КАРТЫ ДЛЯ ПЕРЕВОДА</div>
              <div style="color:#ffffff;font-size:24px;font-weight:900;letter-spacing:4px;font-family:'Courier New',monospace;">
                {CARD_NUMBER}
              </div>
            </div>
          </div>

          <div style="background:#071529;border:1px solid #1a3a6a;border-radius:8px;padding:14px;text-align:center;">
            <div style="color:#7ab0d8;font-size:13px;line-height:1.6;">
              После оплаты напиши администратору в Telegram — он выдаст IP сервера
            </div>
          </div>
        </div>

        <div style="padding:14px 32px;background:#071529;border-top:1px solid #1a3a6a;text-align:center;">
          <span style="color:#2a4a6a;font-size:11px;letter-spacing:1px;">СПИРИТ • ПРИВАТНЫЙ СЕРВЕР</span>
        </div>
      </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, 'html'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, smtp_password)
        server.sendmail(SENDER_EMAIL, player_email, msg.as_string())


def _send_reject(player_email: str, minecraft_nick: str, smtp_password: str):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '❌ Результат рассмотрения заявки на сервер Спирит'
    msg['From'] = SENDER_EMAIL
    msg['To'] = player_email

    html = f"""
    <html>
    <body style="margin:0;padding:0;background:#050e1f;font-family:'Segoe UI',Arial,sans-serif;">
      <div style="max-width:520px;margin:30px auto;background:#0d1f3c;border:2px solid #3a1a1a;border-radius:12px;overflow:hidden;">

        <div style="background:linear-gradient(135deg,#1a0808,#0d1f3c);padding:28px 32px;border-bottom:1px solid #3a1a1a;">
          <div style="font-size:26px;font-weight:900;color:#1a8fff;letter-spacing:3px;">⛏️ СПИРИТ</div>
          <div style="color:#4a90d9;font-size:12px;letter-spacing:2px;margin-top:4px;">ПРИВАТНЫЙ СЕРВЕР</div>
        </div>

        <div style="padding:32px;">
          <div style="font-size:52px;text-align:center;margin-bottom:16px;">😔</div>
          <h2 style="color:#ff4444;font-size:20px;font-weight:900;text-align:center;margin:0 0 16px;letter-spacing:1px;">
            К СОЖАЛЕНИЮ, ВАМ ОТКАЗАЛИ В ПРОХОДКЕ
          </h2>
          <p style="color:#c0d8f0;text-align:center;font-size:15px;margin:0 0 24px;line-height:1.7;">
            Привет, <strong style="color:#ffffff;">{minecraft_nick}</strong>.<br>
            После рассмотрения твоей заявки администрация приняла решение не принимать тебя на сервер в данный момент.
          </p>

          <div style="background:#1a0808;border:1px solid #3a1a1a;border-radius:8px;padding:16px;text-align:center;">
            <div style="color:#884444;font-size:13px;line-height:1.6;">
              Ты можешь попробовать снова позже.<br>
              Удачи в других приключениях! 🗡️
            </div>
          </div>
        </div>

        <div style="padding:14px 32px;background:#071529;border-top:1px solid #1a3a6a;text-align:center;">
          <span style="color:#2a4a6a;font-size:11px;letter-spacing:1px;">СПИРИТ • ПРИВАТНЫЙ СЕРВЕР</span>
        </div>
      </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, 'html'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, smtp_password)
        server.sendmail(SENDER_EMAIL, player_email, msg.as_string())


def _html_response(status_code: int, title: str, message: str) -> dict:
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Спирит</title>
  <style>
    body {{ margin:0;background:#050e1f;font-family:'Segoe UI',Arial,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh; }}
    .card {{ background:#0d1f3c;border:2px solid #1a6aff;border-radius:12px;padding:48px 40px;text-align:center;max-width:420px; }}
    h1 {{ color:#1a8fff;font-size:22px;font-weight:900;margin:0 0 14px;letter-spacing:2px; }}
    p {{ color:#7ab0d8;font-size:14px;line-height:1.6;margin:0; }}
    .logo {{ font-size:22px;font-weight:900;color:#1a8fff;letter-spacing:3px;margin-bottom:28px; }}
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
