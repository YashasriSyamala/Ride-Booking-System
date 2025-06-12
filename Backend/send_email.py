from flask_mail import Message, Mail

class SendMail:
    mail = None

    @staticmethod
    def initialize(app):
        if SendMail.mail is None:
            SendMail.mail = Mail(app)

    @staticmethod
    def send_email(recipients: list, ride):
        message = Message(sender="rithvikkantha3771@gmail.com", subject="Your ride has been cancelled", recipients=recipients)
        pick_up_location = ride.pickup_location["location"]
        drop_location = ride.drop_location["location"]
        # TODO: change this
        driver_name = "{Driver naem}"
        message.html = f"""
        <h2>Dear rider,</h2>
        <h3>Your ride FROM: {pick_up_location} TO: {drop_location} has been cancelled.</h3>
        <p>This ride was scheduled to start on: {ride.start_time}.</p>
        <p>The driver {driver_name} has cancelled this ride.
        Your refund will be processed with in 2-3 workings days</p>
        <p>Thank you for your understanding.</p>
        """
        SendMail.mail.send(message)

    @staticmethod
    def send_reset_password_mail(email, reset_link):
        message = Message(sender="rithvikkantha3771@gmail.com", subject="Password reset", recipients=[email])
        message.html = f'''
            <h2>Dear rider,</h2>
            <p> Click here to reset your password: {reset_link}</p>
        '''
        SendMail.mail.send(message)
        pass