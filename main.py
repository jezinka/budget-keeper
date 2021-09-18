from const import LABEL_ID, ME_ID, ID
from read_emails import search_messages, read_message
from services import get_gmail_service, get_gspread_service
from writing_spread import write_messages

if __name__ == "__main__":
    gmail_service = get_gmail_service()
    spread_service = get_gspread_service()

    results = search_messages(gmail_service, LABEL_ID)

    print(f'found {len(results)} mails for processing\n')
    if len(results) > 0:
        for msg in results:
            print(f'message {msg[ID]} processing start')
            try:
                message = read_message(gmail_service, msg)
                print(f'message {msg[ID]} read')
                write_messages(spread_service, message)
                print(f'message {msg[ID]} saved in sheet')
                gmail_service.users().messages().modify(userId=ME_ID, id=msg[ID],
                                                        body={'removeLabelIds': [LABEL_ID]}).execute()
                print(f'message {msg[ID]} label removed')

            except:
                print("Unexpected error:", msg['id'])
            print(f'message {msg[ID]} processing end\n')
