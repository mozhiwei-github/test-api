import os
from interface_common.mongodb_operate import MongoDBOperate


def read_forbid_words():
    """读取禁忌词文件"""
    db_word_list = []
    forbid_words_folder = r"D:\Work\接口自动化\毒霸\forbid_words"
    file_list = os.listdir(forbid_words_folder)
    for file in file_list:
        file_path = os.path.join(forbid_words_folder, file)
        with open(file_path, 'r', encoding="utf-8") as f:
            word_list = f.read().splitlines()
            for word in word_list:
                # 含有空格的禁忌词取第一个空格前的字符串为禁忌词
                if " " in word:
                    word = word.split(" ")[0]

                # 去除空字符串禁忌词
                if len(word) == 0:
                    continue

                db_word_list.append({
                    "Table_Name": "ForbidWords",
                    "forbid_word": word,
                    "category": file.split(".")[0]
                })

    return db_word_list


def write_forbid_words_to_mongodb():
    # 读取禁忌词文件
    forbid_words = read_forbid_words()
    # 将禁忌词列表写入数据库
    MongoDBOperate.add_data({
        "data": forbid_words
    })


# if __name__ == '__main__':
    # write_forbid_words_to_mongodb()