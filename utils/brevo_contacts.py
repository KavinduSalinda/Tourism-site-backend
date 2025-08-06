import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
from django.utils import timezone


def add_contact_to_brevo(email, attributes=None):
    """
    Add a contact to Brevo contact list
    """
    try:
        # Configure API key
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY

        # Create API instance
        api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))

        # --- START: MODIFIED SECTION ---
        list_ids = []
        if hasattr(settings, 'BREVO_CONTACT_LIST_ID'):
            try:
                # FIX: Convert the string from settings into an integer (number)
                list_id = int(settings.BREVO_CONTACT_LIST_ID)
                list_ids.append(list_id)
            except (ValueError, TypeError):
                # This is good practice in case the setting is misconfigured
                print(f"Warning: BREVO_CONTACT_LIST_ID is not a valid number. Contact will be created without being added to a list.")
        
        # Prepare contact data using the corrected list_ids
        contact_data = sib_api_v3_sdk.CreateContact(
             email=email,
             attributes=attributes or {},
             list_ids=list_ids  # Use the new list of integer IDs
        )
        # --- END: MODIFIED SECTION ---

        # Add contact to Brevo
        # The SDK documentation recommends passing the CreateContact object directly
        api_response = api_instance.create_contact(contact_data) 
        print(f"Contact added to Brevo successfully: {email}")
        return True

    except ApiException as e:
        print(f"Exception when calling ContactsApi->create_contact: {e}")
        # The detailed error message you saw is in e.body
        print(f"Error details: {e.body if hasattr(e, 'body') else 'No body'}")
        return False
    except Exception as e:
        print(f"Unexpected error adding contact to Brevo: {e}")
        return False


def update_contact_in_brevo(email, attributes=None):
    """
    Update a contact in Brevo
    """
    try:
        # Configure API key
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY

        # Create API instance
        api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))

        # Prepare contact data
        contact_data = {
            "attributes": attributes or {}
        }

        # Update contact in Brevo
        api_response = api_instance.update_contact(email, contact_data)
        print(f"Contact updated in Brevo successfully: {email}")
        return True

    except ApiException as e:
        print(f"Exception when calling ContactsApi->update_contact: {e}")
        print(f"Error details: {e.body if hasattr(e, 'body') else 'No body'}")
        return False
    except Exception as e:
        print(f"Unexpected error updating contact in Brevo: {e}")
        return False


def get_brevo_contact_lists():
    """
    Get all contact lists from Brevo
    """
    try:
        # Configure API key
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY

        # Create API instance
        api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))

        # Get contact lists
        api_response = api_instance.get_lists()
        return api_response.lists

    except ApiException as e:
        print(f"Exception when calling ContactsApi->get_lists: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error getting Brevo contact lists: {e}")
        return [] 