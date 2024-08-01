import streamlit as st
import openai

# API Key for OpenAI (replace with your actual key)
api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = api_key

def generate_sentences() -> list:
    prompt = (
        "Generate 25 distinct German sentences with a blank space where a personal pronoun should be. "
        "Follow these guidelines:\n\n"
        "1. Use a mix of Nominativ, Akkusativ, and Dativ cases.\n"  
        "2. Only prononuns that should be used are: ich, du, er, sie, es, wir, ihr, sie, Sie, mich, dich, ihn, sie, es, uns, euch, sie, Sie, mir, dir, ihm, ihr, ihm, uns, euch, ihnen, Ihnen "
        "3. Vary the tenses (present, past, future) and sentence structures.\n"
        "4. Use a range of difficulty levels, from simple to more complex sentences.\n"
        "5. Incorporate different verb types (regular, irregular, separable prefix verbs).\n"
        "6. Ensure that each sentence has an equivalent meaning in both German and Polish.\n"
        "7. Do not display numbers at the begining of sentences\n"
        "8. Verify the grammatical correctness in both languages.\n\n"
        "Provide the output in the following format:\n"
        "German sentence with blank; Polish translation; Correct pronoun\n\n"
        "Examples:\n"
        "__ habe einen Hund.; Ja mam psa.; Ich\n"
        "__ seid sehr freundlich.; Wy jesteście bardzo mili.; Ihr\n"
        "Der Lehrer gibt __ ein Buch.; Ten nauczyciel daje mi książkę.; mir\n"
        "__ Bruder ist Arzt.; Jego brat jest lekarzem.; Sein\n\n"
        "Generate 20 sentences following this format. Do not display the correct pronoun in the sentence, "
        "only provide it at the end for checking purposes. Ensure a good variety of pronouns, cases, and structures."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    response_text = response.choices[0].message['content'].strip()

    sentences = []
    for line in response_text.split('\n'):
        if line.strip():
            try:
                german_sentence, polish_translation, correct_pronoun = line.split('; ')
                polish_translation = polish_translation.strip()
                sentences.append({
                    "sentence_de": german_sentence.strip(),
                    "sentence_pl": polish_translation.strip(),
                    "correct_answer": correct_pronoun.strip()
                })
            except ValueError:
                continue
    return sentences

def check_answer(user_answer: str, correct_answer: str) -> bool:
    """
    Check if the user's answer matches the correct answer.
    """
    user_answer_normalized = user_answer.lower().strip()
    correct_answer_normalized = correct_answer.lower().strip()
    return user_answer_normalized == correct_answer_normalized

def create_pronoun_table_html() -> str:
    """
    Generate HTML for a table of personal pronouns.
    """
    html = """
    <style>
    .pronoun-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #333333;
        color: white;
    }
    .pronoun-table th, .pronoun-table td {
        padding: 10px;
        text-align: center;
    }
    .pronoun-table th {
        background-color: #FF6F61;
        color: white;
    }
    .pronoun-table tr:nth-child(even) {
        background-color: #444444;
    }
    </style>
    <table class="pronoun-table">
        <tr>
            <th>Osoba</th>
            <th>Nominativ (Kto? Co?)</th>
            <th>Akkusativ (Kogo? Co?)</th>
            <th>Dativ (Komu? Czemu?)</th>
        </tr>
        <tr>
            <td>Ja</td>
            <td>ich</td>
            <td>mich</td>
            <td>mir</td>
        </tr>
        <tr>
            <td>Ty</td>
            <td>du</td>
            <td>dich</td>
            <td>dir</td>
        </tr>
        <tr>
            <td>On/Ona/On</td>
            <td>er/sie/es</td>
            <td>ihn/sie/es</td>
            <td>ihm/ihr/ihm</td>
        </tr>
        <tr>
            <td>My</td>
            <td>wir</td>
            <td>uns</td>
            <td>uns</td>
        </tr>
        <tr>
            <td>Wy</td>
            <td>ihr</td>
            <td>euch</td>
            <td>euch</td>
        </tr>
        <tr>
            <td>Oni/One</td>
            <td>sie/Sie</td>
            <td>sie/Sie</td>
            <td>ihnen/Ihnen</td>
        </tr>
    </table>
    """
    return html

def main():
    st.set_page_config(page_title="Ćwiczenie Zaimków Osobowych", page_icon=":books:", layout="wide")
    st.title("Ćwiczenie Zaimków Osobowych")

    # Display the pronoun table
    st.subheader("Tabela Zaimków Osobowych")
    st.markdown(create_pronoun_table_html(), unsafe_allow_html=True)

    # Generate sentences and handle user input
    if 'sentences' not in st.session_state:
        st.session_state.sentences = []

    if st.button("Generuj nowe zadania"):
        with st.spinner("Generowanie zdań..."):
            try:
                st.session_state.sentences = generate_sentences()
                st.success("Nowe zadania zostały wygenerowane!")
            except Exception as e:
                st.error(f"Wystąpił błąd podczas generowania zdań: {str(e)}")

    if st.session_state.sentences:
        for i, sentence in enumerate(st.session_state.sentences):
            st.markdown(f"### Zadanie {i + 1}")
            st.markdown(
                f"<div style='font-size: 18px;'>"
                f"<b>DE:</b> {sentence['sentence_de']}<br>"
                f"<b>PL:</b> {sentence['sentence_pl']}"
                f"</div>",
                unsafe_allow_html=True
            )

            user_answer = st.text_input(
                "Wpisz brakujący zaimek:",
                key=f"answer_{i}"
            )

            if st.button("Sprawdź", key=f"check_{i}"):
                correct_answer = sentence["correct_answer"]
                if check_answer(user_answer, correct_answer):
                    st.success("Poprawna odpowiedź!")
                else:
                    st.error(f"Błędna odpowiedź. Poprawna odpowiedź to: {correct_answer}")

            st.markdown("---")

if __name__ == "__main__":
    main()
