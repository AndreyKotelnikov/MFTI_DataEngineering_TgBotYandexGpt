import importlib.metadata

with open('requirements_full.txt', 'w', encoding='utf-8') as f:
    for dist in importlib.metadata.distributions():
        # Получаем имя и версию пакета
        name = dist.metadata.get('Name', 'Unknown')
        version = dist.version
        f.write(f'{name}=={version}\n')

        # Получаем описание (Summary) из метаданных пакета
        summary = dist.metadata.get('Summary')
        if summary:
            f.write(f'# {summary}\n')
        else:
            f.write("# Описание не найдено\n")
        f.write('\n')
print("requirements_full.txt has been generated.")