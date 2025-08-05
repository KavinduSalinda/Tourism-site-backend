# Description: This file contains the function to send email using Sendinblue API.
from __future__ import print_function
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
from django.conf import settings

# Template IDs
# NEW_BOOKING_REQUEST = 2


# Function to send email using Sendinblue API
def send_email(template_id, recipients, params):
    try:
        print(f"Email body: {params}")

        # Check if the SEND_EMAIL setting is enabled
        if settings.SEND_EMAIL:
            print("Sending email...")

            # Configure API key
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
            print(f"API key: {settings.SENDINBLUE_API_KEY}")

            # Create API instance
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            print("API instance created...")

            # Define recipient
            to = [{"email": email, "name": name} for email, name in recipients]
            print(f"Recipients: {to}")

            # Headers (corrected format)
            headers = {"accept": "application/json", "content-type": "application/json"}

            # Prepare email object
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                headers=headers,
                params=params,
                template_id=template_id
            )

            # Send email
            api_response = api_instance.send_transac_email(send_smtp_email)
            pprint(api_response)
            print("Email sent successfully!")
            return True

        else:
            print("Email sending is disabled in settings.")
            return False

    except ApiException as e:
        print(f"Exception when calling SMTPApi->send_transac_email: {e}")
        print(f"Error details: {e.body if hasattr(e, 'body') else 'No body'}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False



# Example usage
# send_email(
#     template_id=5,
#     recipients=[("
#         email": " [email protected]",
#         "name": "John Doe"
#     )],
#     params={
#         "username": "John Doe",
#         "project_name": "Project X",
#         "link": "https://example.com/project/123"
#     }
# )
#
