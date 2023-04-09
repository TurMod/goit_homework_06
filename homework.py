from pathlib import Path
import sys
import re
import shutil
import os

parse_list = {'documents': [], 'video': [], 'audio': [], 'images': [], 'archives': [], None: []}
extentions = {'identified': [], 'unidentified': []}


def parse_files(path: Path) -> None:
    global parse_list
    global extentions
    DIRECTORIES = ('documents', 'video', 'audio', 'images', 'archives')
    for file in path.iterdir():
        if file.is_file():
            name, file_extension, status = identify_file(file)
            parse_list[name].append(file.name)
            extentions[status].append(file_extension)
        elif file.is_dir():
            if file.name.lower() in DIRECTORIES:
                continue
            elif not os.listdir(file):
                os.rmdir(file)
                continue
            else:
                parse_files(normilize(file))


def identify_file(file: Path) -> str:
    POSSIBLE_EXTENTIONS = {
        'documents': ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
        'video': ('.avi', '.mp4', '.mov', '.mkv'),
        'audio': ('.mp3', '.ogg', '.wav', '.amr'),
        'images': ('.jpeg', '.png', '.jpg', '.svg'),
        'archives': ('.zip', '.gz', '.tar')
    }
    file_extension = file.suffix.lower()
    for name, extensions in POSSIBLE_EXTENTIONS.items():
        for extension in extensions:
            if file_extension == extension:
                move_to_directory(normilize(file), name)
                return name, file_extension, 'identified'
    return None, file_extension, 'unidentified'

def normilize(file: Path) -> Path:
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = (
        "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", 
        "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g"
    )
    map = {}
    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        map[ord(c)] = l
        map[ord(c.upper())] = l.upper()
    edited_file_name = file.name.replace(file.suffix, '')
    edited_file_name = edited_file_name.translate(map)
    edited_file_name = re.sub(r'[^a-zA-Z0-9_]', '_', edited_file_name)
    return file.rename(str(file).replace(file.name, f'{edited_file_name}{file.suffix}'))
    

def move_to_directory(file: Path, directory_name: str) -> None:
    directory_path = Path(str(file).replace(file.name, directory_name))
    archive_path = directory_path / file.name.replace(file.suffix, '')
    try:
        os.mkdir(directory_path)
        if file.suffix in ('.zip', '.gz', '.tar'):
            os.mkdir(archive_path)
    except FileExistsError:
        None
    finally:
        if file.suffix in ('.zip', '.gz', '.tar'):
            shutil.unpack_archive(file, archive_path)
        else:    
            shutil.move(file, directory_path)



try:
    path = sys.argv[1]
    path = Path(path)
    if path.is_file():
        raise IndexError
    elif path.is_dir():
        parse_files(path)
        print('| {:^30} | {:^30} | {:^30} | {:^30} | {:^30} |'.format('documents', 'video', 'audio', 'images', 'archives'))
        max_len = len(max(
            parse_list['documents'],
            parse_list['video'],
            parse_list['audio'],
            parse_list['images'],
            parse_list['archives'],
            key=len
        ))

        for list_ in parse_list.values():
            while len(list_) < max_len:
                list_.append('')
        
        for a, b, c, d, e in zip(parse_list['documents'],
                                 parse_list['video'],
                                 parse_list['audio'],
                                 parse_list['images'],
                                 parse_list['archives']):
            print('| {:^30} | {:^30} | {:^30} | {:^30} | {:^30} |'.format(a, b, c, d, e))

        print(f'\n| identified extentions: {set(extentions["identified"])}')
        print(f'| unidentified extentions: {set(extentions["unidentified"])}')
        print('\nОперация произошла успешно!\n')
    else: 
        raise IndexError
except IndexError:
    print('Вы не указали путь к папке!')