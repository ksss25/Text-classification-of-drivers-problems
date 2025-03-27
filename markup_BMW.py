import pandas as pd
import subprocess
import sys
import time
from progress.bar import IncrementalBar


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


if __name__ == "__main__":
    csv_file = "drive2_BMW.csv"
    df1 = pd.read_csv(csv_file, delimiter=';', on_bad_lines='skip')
    df1['Категория неисправности'] = None
    df = df1.copy()
    bar = IncrementalBar('Обработано описаний:', max=len(df))
    for index, row in df.iterrows():
        text = row['Описание']
        if pd.isna(text):
            df.at[index, 'Категория неисправности'] = "None"
            continue
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
                f"то будешь лишен зарплаты. Если неправильно определишь проблему, то будешь уволен. Текстовое описание: {text}"
        response = ask_ollama(query)
        df.at[index, 'Категория неисправности'] = response
        df.to_csv('drive2_BMW_final.csv', index=False, encoding='utf-8-sig', sep=';')
        bar.next()
        time.sleep(3)
    bar.finish()
    print('Разметка датасета завершена!')
