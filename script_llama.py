import pandas as pd
import subprocess
import sys


def ask_ollama(query):
    try:
        command = ["ollama", "run", "llama3.1:8b", query]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Ошибка при выполнении запроса:")
        print(f"Код ошибки: {e.returncode}")
        print(f"Stderr: {e.stderr}")
        sys.stderr.flush()
        return None
    except Exception as e:
        print(f"Ошибка при выполнении запроса к Ollama: {e}")
        return None


def save_to_csv(query, response, rating, csv_file="pairs_BMW.csv"):
    try:
        new_row = {
            "query": query,
            "response": response,
            "rating": rating,
        }
        df = pd.DataFrame([new_row])
        df.to_csv(csv_file, mode="a", header=not pd.io.common.file_exists(csv_file), index=False)
        print(f"Данные сохранены в {csv_file}")
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")


if __name__ == "__main__":
    csv_file = "drive2_BMW.csv"
    df = pd.read_csv(csv_file, delimiter=';')
    value = df.iloc[170, -1]
    if value is not None:
        query = f"Представь, что ты работаешь в автосервисе. Ты высокооплачиваемый и очень опытный специалист. " \
                f"Тебе необходимо по описанию определить: пользователь пишет о поломке/неисправности автомобиля или нет." \
                f"Если описывается поломка или неисправность, то надо указать, к какой категории она относится " \
                f"из перечисленных: [система впрыска, топливная система, система зажигания, система смазки, " \
                f"кривошипно-шатунный механизм, система охлаждения, выпускная система, сцепление, коробка передач, " \
                f"газораспределительный механизм, подвеска, рулевое управление, тормозная система, электрооборудование, " \
                f"системы отопления и кондиционирования]. Если ни о какой поломке/неисправности не сказано, то" \
                f" необходимо в ответе указать: неисправность отсутствует. Подумай хорошо, прежде чем дать правильный " \
                f"ответ, так как от этого зависит, выплатят тебе премию или нет. Ответ должен быть на русском языке и " \
                f"должен содержать только одно название категории неисправности из указанных выше или же фразу неисправность " \
                f"отсутствует. Ничего больше в твоем ответе быть не должно, только одно предложение, если напишешь больше, " \
                f"то будешь лишен зарплаты. Если неправильно определишь проблему, то будешь уволен. Текстовое описание: {value}"
        print(f"Запрос к модели: {query}")
        response = ask_ollama(query)
        print(response)
        rating = input("Оцените ответ (хорошо/плохо): ").strip().lower()
        save_to_csv(query, response, rating)
