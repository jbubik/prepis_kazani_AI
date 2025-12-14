import openai
import sys

# Assume API key is in the current directory in a file named api.key
try:
    with open("api.key", "r") as f:
        OPENAI_API_KEY = f.read().strip()
except FileNotFoundError:
    print("Error: api.key not found. Please create a file named 'api.key' in the current directory with your OpenAI API key.", file=sys.stderr)
    OPENAI_API_KEY = None

def process_text_with_openai(text, model="gpt-4o-mini"):
    """
    Sends text to OpenAI's API for processing (engaging summary).
    """
    if not OPENAI_API_KEY:
        print("OpenAI API key not available. Returning original text.", file=sys.stderr)
        return text

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    # System instruction for the model
    system_prompt_content = (
        "Jsi šéfredaktor křesťanského časopisu. Tvým úkolem je napsat **poutavou upoutávku (teaser)** na základě přiloženého přepisu kázání.\n\n"
        "Instrukce:\n"
        "1. Nezačínej větou 'Toto kázání je o...'. Místo toho začni provokativní otázkou, silným tvrzením nebo popisem problému, který řečník zmiňuje.\n"
        "2. Identifikuj hlavní biblickou myšlenku nebo ponaučení a stručně ji představ, ale nevyzraď vše – lákej čtenáře, aby si poslechl celé kázání.\n"
        "3. Používej živý, emocemi nabitý jazyk. Vyhni se suchým konstatováním.\n"
        "4. Text musí mít délku cca 200 slov.\n"
        "5. Výstup musí být POUZE výsledný text upoutávky. Žádné 'Zde je shrnutí:' nebo tvé komentáře."
    )

    messages = [
        {"role": "system", "content": system_prompt_content},
        {"role": "user", "content": f"Text kázání:\n\n{text}"}
    ]

    try:
        print(f"Sending text to OpenAI ({model})... This may take a while depending on text length.", file=sys.stderr)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1024, # Corresponding to num_predict for Ollama
            temperature=0.7 # Add a temperature for creativity
        )
        
        return response.choices[0].message.content
        
    except openai.APIError as e:
        print(f"Error communicating with OpenAI API: {e}", file=sys.stderr)
        print("Returning original text.", file=sys.stderr)
        return text
    except Exception as e:
        print(f"An unexpected error occurred with OpenAI API: {e}", file=sys.stderr)
        print("Returning original text.", file=sys.stderr)
        return text
