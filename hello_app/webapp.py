# Entry point for the application.
# did this twice in views and here, thought it was not necessary => check
# maybe i mixed up the different views as i distributed the code in different files
from flask import Flask, render_template, redirect, url_for, request, session
from . import app    # For application discovery by the 'flask' command. 
from . import views  # For import side-effects of setting up routes. 
import requests, os, uuid, json
# if keyvault is used, uncomment the following lines####
from dotenv import load_dotenv
load_dotenv()
# until here############################################
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
# from azure.core.credentials import AzureKeyCredential


# Time-saver: output a URL to the VS Code terminal so you can easily Ctrl+click to open a browser
# print('http://127.0.0.1:5000/hello/VSCode')
###################################################
# starting here, we define the translation service#
###################################################
@app.route("/input-translate", methods=['GET'])
def index():
    return render_template('input-translate.html')


@app.route('/input-translate', methods=['POST'])
def index_post():
    # Read the values from the form Watch out: module is requests but statement is request.form#
    original_text = request.form['text']
    target_language = request.form['language']

    ########################################################
    #Load the values from .env
    # key = os.environ['KEY']
    # endpoint = os.environ['ENDPOINT']
    # location = os.environ['LOCATION']
    ########################################################

    # Load the values from keyvault, GJ: all in lower case as this is how they are stored in keyvault 
    # keyVaultName = os.environ["playgroundkeysgj"] no idea why this does not work
    keyVaultName = "playgroundkeysgj"

    # Set these variables to the names you created for your secrets
    keySecretName = "TranslationpythonKey1"
    endpointSecretName = "TranslationpythonEndpoint"
    locationSecretName = "TranslationpythonRegion"  
    
    # URI for accessing key vault, watch out, i did not set an evironment variable for the keyvault name!!!!!
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    

    # Instantiate the client and retrieve secrets
    credential = DefaultAzureCredential()
    kv_client = SecretClient(vault_url=KVUri, credential=credential)

    print(f"Retrieving your secrets from {keyVaultName}.")

    key = kv_client.get_secret(keySecretName).value
    endpoint = kv_client.get_secret(endpointSecretName).value
    location = kv_client.get_secret(locationSecretName).value

    # Indicate that we want to translate and the API version (3.0) and the target language
    path = '/translate?api-version=3.0'
    # Add the target language parameter
    target_language_parameter = '&to=' + target_language
    # Create the full URL
    constructed_url = endpoint + path + target_language_parameter

    # Set up the header information, which includes our subscription key
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # Create the body of the request with the text to be translated
    body = [{ 'text': original_text }]

    # Make the call using post
    translator_request = requests.post(constructed_url, headers=headers, json=body)
    # Retrieve the JSON response
    translator_response = translator_request.json()
    # Retrieve the translation
    translated_text = translator_response[0]['translations'][0]['text']

    # Call render template, passing the translated text,
    # original text, and target language to the template
    return render_template(
        "output-translate.html",
         translated_text=translated_text,
         original_text=original_text,
       target_language=target_language
    )
 