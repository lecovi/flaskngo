"""
    domi-back.email
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Description
    
    :copyright: (c) 2016 by Leandro E. Colombo Viña <<@LeCoVi>>.
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
# Third-party imports
from flask import current_app, render_template
from flask_mail import Message
# BITSON imports
from app.extensions import celery, mail


@celery.task
def send_async_email(message):
    """
    Send a mail using Flask-Mail extension via Celery.

    :param message: A dictionary with Flask-Mail Message attributes.
    """
    msg = Message(**message)
    mail.send(message=msg)


def celery_email(subject='', recipients=None, body=None, html=None,
                 sender=None, cc=None, bcc=None, attachments=None,
                 reply_to=None, date=None, charset=None, extra_headers=None,
                 mail_options=None, rcpt_options=None,
                 template=None, countdown=60, **kwargs):
    """
    Construct Mail object and send a mail using Flask-Mail extension via Celery.

    :param subject:
    :param recipients:
    :param body:
    :param html:
    :param sender:
    :param cc:
    :param bcc:
    :param attachments:
    :param reply_to:
    :param date:
    :param charset:
    :param extra_headers:
    :param mail_options:
    :param rcpt_options:
    :param template:
    :param countdown:
    :param kwargs:
    :return:
    """
    app = current_app._get_current_object()

    subject = " ".join([app.config.get('MAIL_SUBJECT_PREFIX').upper(), subject])
    msg = dict(subject=subject, recipients=recipients, body=body, html=html,
               sender=sender or app.config.get('MAIL_DEFAULT_SENDER'), cc=cc,
               bcc=bcc, attachments=attachments, reply_to=reply_to, date=date,
               charset=charset, extra_headers=extra_headers,
               mail_options=mail_options, rcpt_options=rcpt_options)
    if template:
        msg['body'] = render_template("".join([template, ".txt"]), **kwargs)
        msg['html'] = render_template("".join([template, ".html"]), **kwargs)
    send_async_email.apply_async(args=[msg, ],
                                 countdown=countdown)

