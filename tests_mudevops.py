import os
import json
import random
import utility
from colorama import init, Fore, Style

init()

subjects = {
        1: {"name": "CI/CD", "path": "subjects/cicd"},
        2: {"name": "Ges. Proyecto", "path": "subjects/project"},
        3: {"name": "Contenedores", "path": "subjects/containers"}
    }

def load_question(file_path):
    """

    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error. No se encontró el archivo {file_path}")

def extract_title(file):
    """

    """
    content = load_question(file)
    return f"{extract_topic_number(file)}. {content['name']}"if content and "name" in content else "Sin título"

def extract_topic_number(topic_name):
    """
    Extrae el número del nombre del tema para ordenarlo numéricamente.
    Si no hay un número, devuelve 0 por defecto.
    """
    try:
        return int("".join(filter(str.isdigit, topic_name)))
    except ValueError:
        return 0
    
def valid_input():
    """
    Validar la entrada de la respuesta del usuario
    """
    while True:
        input_choise = input(Fore.YELLOW + "Ingresa una opción (A, B, C, D): " + Style.RESET_ALL).strip().upper()
        if input_choise in ["A", "B","C","D"]:
            return input_choise
        else:
            print(f"\nTu respuesta {input_choise} no es valida vuelva a intentarlo.")



def main_menu():
    """
    
    """
    while True:
        print(Fore.GREEN + "\n === Menu Principal ===" + Style.RESET_ALL)
        print(Style.DIM + "Seleccionar la materia a repasar\n"+ Style.RESET_ALL)

        for idx, materia in subjects.items():
            print(f"{idx}. {materia["name"]}")
        print("0. Salir")

        option = input(str(Fore.YELLOW +"\nSeleciona una materia: " + Style.RESET_ALL))

        if option.isdigit():
            option = int(option)
            if option in subjects:
                selected_subject = subjects[option]
                utility.clear_console()
                print(f"\nLa Materia selecionadas es: {selected_subject["name"]}")
                return selected_subject["path"]
            elif option == 0:
                utility.clear_console()
                print("¡Hasta luego!")
                break
            else:
                print(f"Opción invalidad")
        else:
            utility.clear_console()
            print(f"{Fore.RED}Solo se pueden igresar números{Style.RESET_ALL}")

def topic_menu(subject_path):
    """
    
    """
    if not subject_path:
        return None

    topics = []

    try:
        files = sorted([f for f in os.listdir(subject_path) if f.endswith(".json")], key=extract_topic_number)
        if not files:
            print("no se ha encontrado la carpeta seleccionada")
            return []
        
        topics = [extract_title(os.path.join(subject_path, f)) for f in files]
    except FileExistsError:
        print(f"La carpeta '{subject_path} no se encuntra")
    except Exception as e:
        print(f"Ocurrio un error inesperado: {e}")
    
    print(Fore.GREEN + "\n === Menu Temas ==="+ Style.RESET_ALL)
    print(Style.DIM + "Seleccionar el o los temas a repasar\n"+ Style.RESET_ALL)

    print("T. Repasar todos los temas")
    if topics:
        for idx, topic in enumerate(topics, start=1):
            print(f"{topic}")
        print("0. Volver al menú principal")
    else:
        print("No hay temas disponibles para esta materia.")
        return []

    while True:    
        topic_choice = input(str(Fore.YELLOW + "\nSelecciona un tema (o 0 para volver al menú principal): " + Style.RESET_ALL))
        
        if topic_choice.isdigit():
            topic_choice = int(topic_choice)
            if topic_choice == 0:
                print(f"Volviendo al menú principal")
                return None                
            elif 1 <= topic_choice <= len(topics):
                topic = topics[topic_choice - 1]
                file_path = os.path.join(subject_path, f"{files[topic_choice - 1]}")
                topic = load_question(file_path)
                if not topic:
                    print(f"Error al cargar el tema {topic_choice}")
                    return None
                utility.clear_console()
                print(f"El tema seleccionado es: TEMA{topic_choice} - {topic["name"]}")
                return topic["preguntas"]
            else:
                print(f"Opción Invalida")
        # REPASAR TODOS LOS TEMAS SI ES "t"
        elif topic_choice in ["t", "T"]:
            print("Cargando preguntas de todos los temas...")
            all_questions = []
            for file in files:
                file_path = os.path.join(subject_path, file)
                topic_data = load_question(file_path)
                if topic_data and "preguntas" in topic_data:
                    # Agregar las preguntas con el nombre del tema
                    for question in topic_data["preguntas"]:
                        question["tema"] = "{}- {}".format(str(topic_data.get("tema", "")), str(topic_data.get("name", "")))
                        all_questions.append(question)
            print("Preguntas de todos los temas cargadas.")
            return all_questions
        else:
            print(f"Solo se pueden ingresar números.")

def ask_questions(all_questions):

    if not all_questions:
        print("❌ No hay preguntas disponibles.")

    random.shuffle(all_questions)
    score = 0
    total = len(all_questions)
    fail_question = []
    for idx , question  in enumerate(all_questions, start=1):
        print(f"Pregunta {idx} de {total}: ")
        # Mostrar tema si se están repasando todos
        if all_questions and "tema" in question:
            print(Style.DIM + f"(Tema: {question['tema']})" + Style.RESET_ALL)
        
        
        print(Fore.GREEN + question["enunciado"] + Style.RESET_ALL)
        for option in question["options"]:
            print(f"{option['op']}. {option['desc']}")
        # Pregunta estándar de una respuesta
        if "ele" not in question["correct"][0]:
            # Obtener respuesta del usuario
            user_answer = valid_input()

            # Verificar respuesta
            correct_answers = [c["op"] for c in question["correct"]]
            if user_answer in correct_answers:
                print("✅ ¡Correcto!")
                score += 1
            else:
                print(f"❌ Incorrecto. La respuesta correcta era: {', '.join(correct_answers)}")
                fail_question.append(question)

            # Mostrar justificación si existe
            if "just" in question:
                print(f"Justificación: {question['just']}\n")
            else:
                print("\n")
        # Pregunta de relación de conceptos
        else:
            user_answers = {}
            correct_relations = {c["ele"]: c["op"] for c in question["correct"]}
            parcial_score = 0

            for element in correct_relations:
                print(f"Relaciona '{element}' con una opción (A, B, C, D): ")
                user_answer = valid_input()
                if user_answer in correct_relations.values():
                    user_answers[element] = user_answer
                    if user_answers[element] == correct_relations[element]:
                        parcial_score += 1 / len(correct_relations)
                        print(f"parcial_score: {parcial_score}")
                else:
                    print("❌ Respuesta inválida. Intenta de nuevo.")
                    user_answers[element] = None

            score = score + parcial_score
            # Validar respuestas
            if user_answers == correct_relations:
                print("✅ ¡Correcto! Relacionaste todos los elementos correctamente.")
            else:
                print("❌ Incorrecto. Las relaciones correctas eran:")
                print(f"Haz acertado {int(parcial_score / (1 / len(correct_relations))) } de {len(correct_relations)}" if parcial_score > 0 else "No has acertado ninguna relación.")
                for element, correct_option in correct_relations.items():
                    correct = next((o for o in question["options"] if o["op"] == correct_option), None)
                    print(f"    {element:<15} <->   {correct["op"]} - {correct['desc']}")
                fail_question.append(question)

            # Mostrar justificación si existe
            if "just" in question:
                print(f"Justificación: {question['just']}\n")
            else:
                print("\n")

    # Mostrar puntaje final
    print(f"Tu puntuación final: {score}/{total} ({(score / total) * 100:.2f}%)\n")
    if (score != total):
        print(f"❌ Preguntas falladas: {len(fail_question)}")
        print("¿Deseas volver a responder falladas?")
        show_fail = input("Ingresa 's' o para volver a responder las preguntas falladas o 'n' para volver al menú principal: ")
        if show_fail.lower() == "s":
            ask_questions(fail_question)
        else:
            return       




if __name__ == "__main__":

    while True:
        subject_path = main_menu()
        if subject_path:
            topic_questions = topic_menu(subject_path)
            if topic_questions:
                print("\nIniciando cuestionario...")
                ask_questions(topic_questions)
            else:
                continue
        else:
            break