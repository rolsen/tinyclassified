"""Underlying service to manage the sending of emails.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@author: Sam Pottinger (samnsparky, Gleap LLC 2014)
"""
import markdown
import sendgrid

import tiny_classified


def get_service_client(username, password, secure):
    """Get the client for the current email service.

    @param username: The username to use to authenticate with the email service.
    @type username: str
    @param password: The password of the corresponding user.
    @type password: str
    @param secure: Flag indicating if SSL should be forced.
    @type secure: bool
    @return: The email service client.
    """
    return sendgrid.SendGridClient(username, password, secure=secure)


def send(recipients, subject, plain_body, html_body=None):
    """Sends email message through the system-specified email service.

    @param recipients: The email addresses to send to.
    @type recipients: Iterable over str
    @param subject: The email subject line.
    @type subject: str
    @param plain_body: The plain text email body.
    @type plain_body: str
    @keyword html_body: The HTML email body.
    @type html_body: str
    """
    app_config = tiny_classified.get_config()

    if html_body == None:
        html_body = markdown.markdown(plain_body)

    if app_config['FAKE_EMAIL']:
        print '-------'
        print html_body
        print '-------'
        return

    client = get_service_client(
        app_config['EMAIL_USERNAME'],
        app_config['EMAIL_PASSWORD'],
        app_config['EMAIL_USE_SECURE']
    )

    message = sendgrid.Mail()
    message.set_from(app_config['EMAIL_FROM_ADDR'])
    message.set_subject(subject)
    message.set_html(html_body)
    message.set_text(plain_body)

    for recipient in recipients:
        message.add_to(recipient)

    client.web.send(message)
