

def get_target_value(key, dic, tmp_list):
    """
    :param key: 目标key值
    :param dic: JSON数据
    :param tmp_list: 用于存储获取的数据
    :return: list
    """
    if not isinstance(dic, dict) or not isinstance(tmp_list, list):  # 对传入数据进行格式校验
        return 'argv[1] not an dict or argv[-1] not an list '

    if key in dic.keys():
        tmp_list.append(dic[key])  # 传入数据存在则存入tmp_list
    else:
        for value in dic.values():  # 传入数据不符合则对其value值进行遍历
            if isinstance(value, dict):
                get_target_value(key, value, tmp_list)  # 传入数据的value值是字典，则直接调用自身
            elif isinstance(value, (list, tuple)):
                _get_value(key, value, tmp_list)  # 传入数据的value值是列表或者元组，则调用_get_value
    return tmp_list


def _get_value(key, val, tmp_list):
    for val_ in val:
        if isinstance(val_, dict):
            get_target_value(key, val_, tmp_list)  # 传入数据的value值是字典，则调用get_target_value
        elif isinstance(val_, (list, tuple)):
            _get_value(key, val_, tmp_list)   # 传入数据的value值是列表或者元组，则调用自身


# 判断data_res是否被r_res包含
def matchd_result(data_res, r_res):
    """
    :param data_res: xlsx里读取的预期返回值
    :param r_res: 接口返回的数据
    :return: data_res里，除变量外的数据如果与r_res相同，返回True，否则返回False
    """
    issame = True
    iscirculate = False   # 检查循环符号的标记
    try:
        if not data_res and not r_res:  # 处理列表、字典为空的情况
            issame = True
            return issame
        if data_res == r_res:  # 处理列表为字符串、整型的情况
            issame = True
            return issame
        for d in data_res:
            if type(data_res[d]) is list:   # 处理字典里value为list的数据
                if not data_res[d] and r_res[d]:  # 如果预期为空，返回不为空
                    issame = False
                    return issame
                elif not data_res[d] and not r_res[d]:  # 如果预期为空，返回也为空
                    issame = True
                    return issame
                for i in range(0, len(data_res[d]), 1):
                    issame = False
                    for j in range(0, len(r_res[d]), 1):
                        if matchd_result(data_res[d][i], r_res[d][j]):
                            issame = True
                            break
                    # 如果是循环变量，直接跳出整个列表
                    if iscirculate:
                        iscirculate = False
                        issame = True
                    if not issame:
                        print("文档数据：" + str(data_res[d][i]))
                        print("接口数据：" + str(r_res[d][i]))
                        return issame
            elif type(data_res[d]) is not dict:
                if data_res[d] != r_res[d]:
                    issame = False
                    return issame
            else:
                if not matchd_result(data_res[d], r_res[d]):
                    print("***** 对比失败的数据 *****")
                    print("文档数据：" + str(data_res[d]))
                    print("接口数据：" + str(r_res[d]))
                    issame = False
                    return issame

    except Exception as e:
        issame = False
        
    return issame
