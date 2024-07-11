from flask import Flask, request, jsonify
import requests
import os
import random
import json
import re
import nltk
import difflib
import textwrap
# from nltk.corpus import stopwords
from collections import defaultdict
from datetime import datetime
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

MONGO_URL = 'mongodb+srv://rushaid4:root12345@conversational.9ik2tt0.mongodb.net/'

client = MongoClient(MONGO_URL)

conversational_db = client['conversational']
test_db = client['test']

# Accessing collections
items_collection = test_db['items']
invoices_collection = conversational_db['invoices']

# items = items_collection.find()
# for item in items:
#     print(item)

# items_to_add = [
#     { 'itemName': 'sugar', 'price': 40.99 },
#     { 'itemName': 'salt', 'price': 40.99 },
#     { 'itemName': 'chilli', 'price': 200.49 },
#     { 'itemName': 'chocolate', 'price': 20.49 },
#     { 'itemName': 'tea Powder', 'price': 30.99 },
#     { 'itemName': 'atta', 'price': 46.99 },
#     { 'itemName': 'maida', 'price': 44.99 },
#     { 'itemName': 'coconut Oil', 'price': 120.99 },
#     { 'itemName': 'palm oil', 'price': 100.99 },
#     { 'itemName': 'match box', 'price': 9.99 },
#     { 'itemName': 'rice', 'price': 45.99 },
#     { 'itemName': 'kadala', 'price': 90.99 },
#     { 'itemName': 'parippu', 'price': 110.99 },
# ]

# result = items_collection.insert_many(items_to_add)
# for id in result.inserted_ids:
#     print(f"Inserted document ID: {id}")




# Environment variables
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
GRAPH_API_TOKEN = 'EAAQ4gGOpnq0BO6bzreZB9sV3SnZAfMNZAHwaefeO20rrDp0HMmSFZBjQq9tmLDw0XXKEkQ1w0pZBsAP9SyneJAlvEAYb2RiqBwzwZCsDxEYMLNwaYVLVUneTHKEY1LjWhwZAvhHxnuOINJIvdmIbDBEDrcNdWa9m4Cs95Q75KeI5TXC8tdd6DbCv4OWE3UZCwjdYID7hmYk3mTkxa9hSpl0ZD'
last_reference_number = 99

json_file = os.path.join(os.path.dirname(__file__), 'dataset.json')

# Load dataset.json
with open(json_file, 'r', encoding='utf-8') as file:
    dataset = json.load(file)
    items = dataset["items"]
    intent_keywords = dataset["intent_keywords"]
    numbers = dataset["numbers"]
    
    
    

stopwords_list = [':',';','to', 'the', 'and', 'a', 'of', 'in', 'for', 'on', 'with', 'as', 'by', 'at', 'an', 'be', 'this', 'that', 'which','K','k','KG','kg','kilo','kilos','killo','kilogram','kilograms','gram','grams','g','gm','ml','milli','milliliters','liter','litre','packets','packet','packt','pkt','add','remove','.',',','confirm','update','change','view']



@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        # Handle verification request
        print("inside get request")
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            return challenge, 200
        else:
            return 'Verification failed', 403
    
    elif request.method == 'POST':
      
        print("Inside post request")
        # Handle incoming messages
        data = request.json
        print("Incoming webhook message:", data)
        
        changes = data.get('entry', [])[0].get('changes', [])[0].get('value', {})
        
        if 'messages' in changes:
            # Process incoming message
            message = changes['messages'][0]
            print("message is ", message)

        # Check if message type is text
            if message['type'] == 'text':
                business_phone_number_id = data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
                from_number = message['from']
                message_body = message['text']['body']
                message_id = message['id']
            
                # Analyze user input
                response_message = handle_user_message(message_body, from_number)
                print("response message is ",response_message)
            
            # Send reply message
                reply_url = "https://graph.facebook.com/v18.0/" + business_phone_number_id + "/messages"
                reply_headers = {
                'Authorization': f'Bearer {GRAPH_API_TOKEN}',
                'Content-Type': 'application/json'
            }
                reply_data = {
                'messaging_product': 'whatsapp',
                'to': from_number,
                'text': {'body': response_message},
                'context': {'message_id': message_id}
            }
                response = requests.post(reply_url, headers=reply_headers, json=reply_data)
                print("Reply sent, status:", response.status_code)

                # Mark message as read
                read_url = "https://graph.facebook.com/v18.0/" + business_phone_number_id + "/messages"
                read_data = {
                'messaging_product': 'whatsapp',
                'status': 'read',
                'message_id': message_id
            }
                read_response = requests.post(read_url, headers=reply_headers, json=read_data)
                print("Message marked as read, status:", read_response.status_code)
                
            elif 'statuses' in changes:
                # Process status update
                status = changes['statuses'][0]
                print("status is ", status)

        

    return 'OK', 200


# Simulated database
database = []

# Simulated invoice storage
invoices = {}

def handle_user_message(user_message, user_id):
    response = analyze_input(user_message)
    user_intent = response.get('user_intent')
    items_quantities = response.get('items_quantities')
    error = response.get('error')

    if error:
        return error
      
    if user_intent == 'hello':
        res = "Welcome to ************* ,\n\n Please provide items and quantities to generate invoices\n\n Type 'admin' to move to Admin Panel "
        return res

    if user_id not in invoices:
        invoices[user_id] = {
            "reference_number": generate_reference_number(),
            "items": defaultdict(lambda: {"quantity": 0, "price": 0.0}),
            "total": 0.0
        }

    if user_intent in {'unknown', 'add'} and items_quantities:
        # Add items to invoice
        for item, quantities in items_quantities.items():
            for quantity in quantities:
                invoices[user_id]['items'][item]['quantity'] += quantity
                # Assuming price is fetched from a database or predefined list
                price = fetch_item_price(item)
                print("price is ",price)
                if price is None:
                    price = 0.0;
                invoices[user_id]['items'][item]['price'] = price
                invoices[user_id]['total'] += price * quantity
        return generate_invoice_message(user_id)

    
    elif user_intent == 'confirm':
        confirmation_message = generate_invoice_message(user_id)
        invoice_id = save_invoice_to_database(user_id)
        return f"Invoice confirmed and saved with ID: {invoice_id}\n" + confirmation_message
    
    elif user_intent == 'view':
        return generate_invoice_message(user_id)

    
    elif user_intent == 'clear':
        clear_invoice(user_id)
        return "Invoice has been cleared."

    
    elif user_intent == 'remove':
        for item, quantities in items_quantities.items():
            for quantity in quantities:
                if item in invoices[user_id]['items']:
                    invoices[user_id]['items'][item]['quantity'] -= quantity
                    if invoices[user_id]['items'][item]['quantity'] <= 0:
                        del invoices[user_id]['items'][item]
                    price = fetch_item_price(item)
                    print("price is ",price)
                    if price is None:
                        price = 0.0;
                    invoices[user_id]['total'] -= price * quantity
                    if invoices[user_id]['total'] < 0:
                        invoices[user_id]['total'] = 0
        return "item removed from invoice"

    elif user_intent == 'update':
        for item, quantities in items_quantities.items():
            if item in invoices[user_id]['items']:
                old_quantity = invoices[user_id]['items'][item]['quantity']
                new_quantity = quantities[0]
                price = fetch_item_price(item)
                invoices[user_id]['total'] += (new_quantity - old_quantity) * price
                invoices[user_id]['items'][item]['quantity'] = new_quantity
        return "Invoice updated"
      
    elif user_intent in {'unknown'} and not items_quantities:
        return "I'm sorry, I didn't understand that."
        

    else:
        return "I'm sorry, I didn't understand that."

def generate_reference_number():
    # Start from 100 and increment for each new reference number
    if not hasattr(generate_reference_number, "counter"):
        generate_reference_number.counter = 100  # it doesn't exist yet, so initialize it
    reference_number = generate_reference_number.counter
    generate_reference_number.counter += 1
    return str(reference_number).zfill(8)  # Zero-padding to keep the format consistent

  
# def fetch_item_price(item_name):
#     try:
#         item = items_collection.find_one({'itemName': item_name})
#         if item:
#             return item['price']
#         else:
#             print(f"No item found with itemName: {item_name}")
#             return None
#     except Exception as e:
#         print(f'Error retrieving item details for {item_name}: {e}')
#         return None
      

def fetch_item_price(item_name):
    try:
        item_name = item_name.strip()  # Remove any leading or trailing whitespace
        item = items_collection.find_one({'name': {'$regex': f'^{item_name}$', '$options': 'i'}})
        if item:
            return item['price']
        else:
            print(f"No item found with name: {item_name}")
            return None
    except Exception as e:
        print(f'Error retrieving item details for {item_name}: {e}')
        return None

def generate_invoice_message(user_id):
    invoice = invoices[user_id]
    organization_name = "Your Organization Name"
    reference_number = invoice['reference_number']
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    grand_total = invoice['total']

    # Formatting the message
    message = f"*{organization_name.center(50)}*\n\n"
    message += f"*Reference Number:* {reference_number}\n"
    message += f"*Date & Time:* {date_time}\n\n"
    message += "*INVOICE*\n\n"

    # Column headers
    message += f"{'*Item Name*'.ljust(20)} {'*Qty*'.rjust(5)} {'*Price*'.rjust(10)} {'*Total*'.rjust(10)}\n"
    message += "-" * 50 + "\n"

    # Items
    for item, details in invoice['items'].items():
        wrapped_item = textwrap.fill(item, width=20)
        lines = wrapped_item.split('\n')
        first_line = lines[0]
        remaining_lines = lines[1:]

        qty = f"{details['quantity']:.2f}"
        price = f"{details['price']:.2f}"
        total = f"{details['quantity'] * details['price']:.2f}"

        # First line with item details
        message += f"{first_line.ljust(20)} {qty.rjust(5)} {price.rjust(10)} {total.rjust(10)}\n"
        
        # Remaining lines for long item names
        for line in remaining_lines:
            message += f"{line.ljust(20)}\n"

    # Grand Total
    message += "-" * 50 + "\n"
    message += f"{'*Grand Total:*'.ljust(35)} {grand_total:.2f}\n"

    return message


  
def clear_invoice(user_id):
    invoices[user_id]['items'].clear()
    invoices[user_id]['total'] = 0.0

def save_invoice_to_database(user_id):
    invoice = invoices[user_id]
    invoice_entry = {
        "reference_number": invoice["reference_number"],
        "items": [],
        "total": invoice["total"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    for item, details in invoice['items'].items():
        invoice_entry["items"].append({
            "item_name": item,
            "quantity": details['quantity'],
            "price": details['price'],
            "total": details['quantity'] * details['price']
        })

    try:
        invoice_id = save_invoice_to_db(invoice_entry)
        if invoice_id:
            clear_invoice(user_id)
            return invoice_id
        else:
            raise Exception("Failed to save invoice to database")
    except Exception as e:
        print(f"Error saving invoice to database: {e}")
        raise

def save_invoice_to_db(invoice_entry):
    try:
        result = invoices_collection.insert_one(invoice_entry)
        return result.inserted_id
    except Exception as e:
        print(f"Error saving invoice to database: {e}")
        return None

def verify_connection():
    try:
        client.admin.command('ping')
        print("Connected to MongoDB")
    except Exception as e:
        print("Failed to connect to MongoDB", str(e))    

    
def analyze_input(user_input):
    response = {}
    print("inside analyze user input")
    user_intent = classify_intent(user_input, intent_keywords)
    print("intent is :", user_intent)

    pattern = re.compile(
        r'\b(?:\d+(\.\d+)?\s*(kg|g|ml|l|lbs|oz)\b\s*\w+(?:\s+\w+)*|(\w+(?:\s+\w+)*:\s*\d+(\.\d+)?\s*(kg|g|ml|l|lbs|oz))|\b\w+(?:\s+\w+)*\s*\d+(\.\d+)?\s*(kg|g|ml|l|lbs|oz))\b',
        re.IGNORECASE
    )

    items_and_quantities = None
    error_occurred = False

    if user_intent not in {"hello", "confirm", "view", "clear"}:
        print("in user analyze")

        try:
            if pattern.findall(user_input):
                items_and_quantities = analyze_user_input(user_input, items)
                print("Items and quantities:", items_and_quantities)
            else:
                print("No recognizable item and quantity pattern found.")
                error_occurred = True
                return {
                    "user_intent": user_intent,
                    "error": "No recognizable item and quantity pattern found."
                }

        except Exception as e:
            print("An error occurred during analysis", str(e))
            error_occurred = True
            return {
                "user_intent": user_intent,
                "error": "An error occurred during analysis."
            }

    response = {
        "user_intent": user_intent,
    }

    if items_and_quantities is not None:
        response["items_quantities"] = items_and_quantities

    if error_occurred and items_and_quantities is None:
        response["error"] = "An error occurred during analysis, and no items were recognized."
        return response
    
    elif error_occurred:
        response["partial_result"] = "An error occurred during analysis. Partial results are provided."

    return response


def preprocess_input(user_input):
    user_input = user_input.lower().strip().replace(',', '').replace(':', '').replace(';', '').replace('.', '')
    tokens = user_input.split()
    return tokens

def classify_intent(user_message, intent_keywords):
    print("all_intented keywords functionn")
    tokens = preprocess_input(user_message)
    all_intent_keywords = [keyword for keywords in intent_keywords.values() for keyword in keywords]
    
    print(all_intent_keywords)
    
    for token in tokens:
        print("inside close match loop")
        closest_match = difflib.get_close_matches(token, all_intent_keywords, n=1, cutoff=0.8)
        if closest_match:
            print("close_match is ", closest_match)
            for intent, keywords in intent_keywords.items():
                if closest_match[0] in keywords:
                    print("intent is", intent)
                    return intent
    return "unknown"

def analyze_user_input(user_input, dataset):
    user_input = user_input.lower().strip().replace(',', '')
    tokens = nltk.word_tokenize(user_input)
    print("tokens:", tokens)

    items_and_quantities = defaultdict(list)
    unrecognized_items = defaultdict(list)
    processed_tokens = []

    all_items = [variation for variations in items.values() for variation in variations]
    all_qty = [variation for variations in numbers.values() for variation in variations]

    def is_quantity(token):
        return any(char.isdigit() for char in token)

    def get_closest_match(token, possibilities):
        print("Inside close match function")
        matches = difflib.get_close_matches(token, possibilities, n=1, cutoff=0.7)
        print("Matches are", matches)
        if matches:
            match = matches[0]
            if match in all_qty:
                print("inside all qty")
                for key, variations in numbers.items():
                    if match in variations:
                        print("key is ", key)
                        return key
            else:
                print("else of all qty")
                for key, variations in items.items():
                    if match in variations:
                        print("key is ", key)
                        return key
        return None 

    def extract_quantity(token):
        try:
            return float(re.sub(r'[^\d.]', '', token))
        except ValueError:
            return None

    i = 0
    while i < len(tokens):
        try:
            token = tokens[i]
            print("token:", token)

            if token in stopwords_list:
                i += 1
                continue

            if token in processed_tokens and not is_quantity(token):
                i += 1
                continue

            processed_tokens.append(token)




        
            if is_quantity(token):
            
                print("Inside is_quantity :")
                close_match = get_closest_match(token, all_qty)
                print("close match is ",close_match)
                quantity = extract_quantity(close_match)
                print("Quantity is ,: ",quantity)
                next_token=None
            
                if i + 1 < len(tokens):
                    print("insideeee")
                    print(tokens[i+1])

                    if tokens[i + 1] not in stopwords_list and not is_quantity(tokens[i+1]):
                        print("inside i + 1")
                        next_token = tokens[i + 1]
                        print("next token is ",next_token)
                        i += 2;
                        if i < len(tokens) and tokens[i] not in stopwords_list and not is_quantity(tokens[i]):
                            print("for double name")
                            if not is_quantity(tokens[i + 1]) or not (i + 2 < len(tokens) and is_quantity(tokens[i + 2])):
                                next_token += " " + tokens[i]
                                i += 1
                            # if i < len(tokens) and tokens[i] not in stopwords and not is_quantity(tokens[i]):
                            #     next_token += " " + tokens[i]
                            #     i += 1

                    elif tokens[i+2] not in stopwords_list and not is_quantity(tokens[i+2]):
                        print("inside i + 2")
                        next_token = tokens[i + 2]
                        print("next token is ",next_token)
                        i += 3;
                        if i < len(tokens) and tokens[i] not in stopwords_list and not is_quantity(tokens[i]):
                            print("i is ",tokens[i])
                            next_token += " " + tokens[i]
                            i += 1
                            # if i < len(tokens) and tokens[i] not in stopwords and not is_quantity(tokens[i]):
                            #     next_token += " " + tokens[i]
                            #     i += 1
                else:
                    break
                    

               
                
                print("in quantity next token is :",next_token)
                item_name = get_closest_match(next_token, all_items)
                print("In quanty , item name is ",item_name)
                
                if item_name and quantity:
                    items_and_quantities[item_name].append(quantity)
                    print("in quanty , dict is ",items_and_quantities)
                    continue
                    
                else:
                    unrecognized_items[next_token].append(quantity)
                    print("In quanty unrecog is ",unrecognized_items)
                    continue

            else:
                print("In NOT quanty ")
                item_name = get_closest_match(token, all_items)
                print("In NOT quanty , item name is ",item_name)
                if not item_name:
                    item_name = token
                    print("In NOT quanty , if not item name is ",item_name)
                    if i + 1 < len(tokens) and not is_quantity(tokens[i + 1]) and tokens[i + 1] not in stopwords_list:
                        item_name += " " + tokens[i + 1]
                        print("In NOT quanty , if not item name and second is ",item_name)
                        i += 1
                        if i + 1 < len(tokens) and not is_quantity(tokens[i + 1]) and tokens[i + 1] not in stopwords_list:
                            item_name += " " + tokens[i + 1]
                            print("In NOT quanty , if not item name and second is ",item_name)
                            i += 1
                else:
                    if i + 1 < len(tokens) and not is_quantity(tokens[i + 1]) and tokens[i + 1] not in stopwords_list:
                        item_name += " " + tokens[i + 1]
                        item_name = get_closest_match(item_name, all_items)
                        print("In NOT quanty , if item name in else is ",item_name)
                        i += 1
                        if i + 1 < len(tokens) and not is_quantity(tokens[i + 1]) and tokens[i + 1] not in stopwords_list:
                            item_name += " " + tokens[i + 1]
                            item_name = get_closest_match(item_name, all_items)
                            print("In NOT quanty , if not item name in else is ",item_name)
                            i += 1



            
                if item_name in items:
                    print("if item_name in all_items")
                    if i + 1 < len(tokens) and is_quantity(tokens[i + 1]) and tokens[i + 1] not in stopwords_list:
                        ww = tokens[i + 1]
                        print("ww is",ww)
                        close = get_closest_match(ww,all_qty)
                        print("close match is ",close)
                        quantity = extract_quantity(close)
                        print("NOT quanty , Quantity is ,: ",quantity)
                        # items_and_quantities[item_name].append(quantity)
                        items_and_quantities.setdefault(item_name, []).append(quantity)
                        print("in not quanty , dict is ",items_and_quantities)
                        i += 2
                        continue
                    elif i + 2 < len(tokens) and is_quantity(tokens[i + 2]) and tokens[i + 2] not in stopwords_list:
                     # unrecognized_items[token] = quantity
                        print("if else item_name in all_items")
                        quantity = get_closest_match(tokens[i+2],all_qty)
                        items_and_quantities.setdefault(item_name, []).append(quantity)
                        print("1 In NOT quanty recog is ",items_and_quantities)
                        i += 3
                        continue
                else:
                    print("inside item name not in all items")
                    if i + 1 < len(tokens) and is_quantity(tokens[i + 1]) and tokens[i + 1] not in stopwords_list:
                        print("inside item name no tin all items token is i+1")
                        close_quanty = get_closest_match(tokens[i + 1],all_qty)
                        print("In NOT quanty 2nd  quantity is ",close_quanty)
                        quantity=extract_quantity(close_quanty)
                        unrecognized_items.setdefault(item_name, []).append(quantity)
                        print("In NOT quanty 2nd  unrecog is ",unrecognized_items)
                        i += 2
                        continue
                
                    elif i + 2 < len(tokens) and is_quantity(tokens[i + 2]) and tokens[i + 2] not in stopwords_list:
                        print("inside item name no tin all items token is i+1")
                        close_quanty = get_closest_match(tokens[i + 2],all_qty)
                        print("In NOT quanty 2nd  quantity is ",close_quanty)
                        quantity=extract_quantity(close_quanty)
                        unrecognized_items.setdefault(item_name, []).append(quantity)
                        print("In NOT quanty 2nd  unrecog is ",unrecognized_items)
                        i += 3
                        continue


                    else:
                        unrecognized_items.setdefault(item_name, []).append(tokens[i+1])
                        i += 1
                        continue

        except Exception as e:
            print(f"Error processing token '{token}': {e}")
            break
            
        
    print("Items and Quantities:",dict( items_and_quantities))
    print("Unrecognized Items:", dict(unrecognized_items))

    suffix = " (availability pending!)"

         # Create a new dictionary with modified keys (adding suffix)
    modified_unrecognized_items = {key + suffix: value for key, value in unrecognized_items.items()}

        # Print the modified dictionary
    print("Unrecognized Items:", dict(modified_unrecognized_items))

       # Combine the dictionaries
    combined_result = {**items_and_quantities, **modified_unrecognized_items}

    return dict(combined_result);
if __name__ == '__main__':
    verify_connection()
    app.run(debug=True, port=3000)
