import math
import itertools
times = 5
def xor_to_base62(num1, num2):
    """
    对两个十进制数进行XOR运算,并将结果转换为62进制
    """
    if isinstance(num1, str):
        num1 = int(num1)
    if isinstance(num2, str):
        num2 = int(num2)
    xor_result = num1 ^ num2
    base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if xor_result == 0:
        return "0"
    result = []
    while xor_result > 0:
        remainder = xor_result % 62
        result.append(base62_chars[remainder])
        xor_result = xor_result // 62
    return ''.join(reversed(result))
def generate_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break    
        if is_prime:
            primes.append(candidate)
        candidate += 1
        if candidate % 2 == 0 and candidate != 2:
            candidate += 1       
    return primes

def num_to_prime(n):
    return primes[n]

def letter_to_num(n):
    if ord(n)<=57:
        return ord(n)-ord('0')
    elif ord(n)<=90:
        return ord(n)-ord('A')
    else:
        return ord(n)-ord('a')


def n_to_decimal(n, num_str):
    """
    将n进制数转换为十进制数
    """
    decimal_num = 0
    length = len(num_str)
    for i in range(length):
        digit = int(num_str[i])
        decimal_num += digit * (n ** (length - 1 - i))
    
    return decimal_num

def fun1():
    """
    函数fun1：生成操作指数序列到整数的映射字典
    映射规则：所有可能的操作指数序列 -> 从1开始的整数列表
    """
    elements = []
    base_elements = [str(i) for i in range(3)] + ['a', 'b', 'A', 'B']
    all_sequences = []
    for combo in itertools.product(base_elements, repeat=times):
        all_sequences.append(combo)
    operation_sequences = []
    for seq in all_sequences:
        def sort_key(char):
            if char.isdigit():
                return (0, char)
            elif char.islower():
                return (1, char)
            elif char.isupper():
                return (2, char)
        
        simplest = sorted(seq, key=sort_key)
        current = simplest.copy()
        operations = []
        
        # 计算将最简序列转换为当前序列所需的操作
        target = list(seq)
        
        for i in range(times):
            if current[i] == target[i]:
                continue
            
            # 找到目标元素位置（考虑重复元素，从i位置开始找第一个匹配项）
            target_pos = -1
            for j in range(i, len(current)):
                if current[j] == target[i]:
                    temp_current = current.copy()
                    temp_target = target.copy()
                    temp_current[i], temp_current[j] = temp_current[j], temp_current[i]
                    
                    # 如果交换后前缀匹配，则这是正确的位置
                    if temp_current[:i+1] == temp_target[:i+1]:
                        target_pos = j
                        break
            
            if target_pos == -1:
                raise ValueError(f"无法找到目标元素 {target[i]} 在位置 {i} 之后")
            
            # 从目标位置向前交换到当前位置
            for j in range(target_pos, i, -1):
                operations.append(j)  # 记录操作
                current[j-1], current[j] = current[j], current[j-1]
        
        # 只添加新的操作序列
        if operations not in operation_sequences:
            operation_sequences.append(operations)
    
    # 排序操作序列以便映射的整数保持一致性
    operation_sequences.sort(key=lambda x: (len(x), x))
    
    # 创建映射字典：操作序列 -> 整数（从1开始）
    mapping = {tuple(ops): i+1 for i, ops in enumerate(operation_sequences)}
    
    return mapping

def fun2(sequence, mapping=None):
    """
    函数fun2:输入一个序列(可包含相同元素),输出其操作指数序列与其映射的整数
    如果未提供mapping,则自动调用fun1生成
    """
    if len(sequence) != times:
        raise ValueError(f"序列长度必须为{times}")
    valid_chars = set(str(i) for i in range(10)) | set(chr(ord('a') + i) for i in range(26)) | set(chr(ord('A') + i) for i in range(26))
    for char in sequence:
        if char not in valid_chars:
            raise ValueError(f"序列包含无效字符: {char}")
    
    # 计算最简序列（移除了元素必须唯一的限制）
    def sort_key(char):
        if char.isdigit():
            return (0, char)
        elif char.islower():
            return (1, char)
        elif char.isupper():
            return (2, char)
    
    simplest = sorted(sequence, key=sort_key)
    current = simplest.copy()
    operations = []
    
    # 计算操作指数序列（改进以处理重复元素）
    for i in range(times):
        if current[i] == sequence[i]:
            continue
        
        # 找到目标元素位置（考虑重复元素）
        target_pos = -1
        for j in range(i, len(current)):
            if current[j] == sequence[i]:
                # 验证这是正确的匹配项
                temp_current = current.copy()
                temp_target = sequence.copy()
                
                # 暂时交换来验证
                temp_current[i], temp_current[j] = temp_current[j], temp_current[i]
                
                if temp_current[:i+1] == temp_target[:i+1]:
                    target_pos = j
                    break
        
        if target_pos == -1:
            raise ValueError(f"无法找到目标元素 {sequence[i]} 在位置 {i} 之后")
        
        # 从目标位置向前交换到当前位置
        for j in range(target_pos, i, -1):
            operations.append(j)
            current[j-1], current[j] = current[j], current[j-1]
    if mapping is None:
        mapping = fun1()
    
    # 获取映射的整数
    try:
        mapped_int = mapping[tuple(operations)]
    except KeyError:
        raise ValueError("ERROR")
    
    return operations, mapped_int

def fun3(mapped_int, simplest_sequence, mapping=None):
    """
    函数fun3:：输入操作指数序列对应的整数和最简序列,输出反解密之后的序列
    即fun2的反函数
    """
    def sort_key(char):
        if char.isdigit():
            return (0, char)
        elif char.islower():
            return (1, char)
        elif char.isupper():
            return (2, char)
    
    if sorted(simplest_sequence, key=sort_key) != simplest_sequence:
        raise ValueError("ERROR")
    # 获取映射
    if mapping is None:
        mapping = fun1()
    
    # 查找与整数对应的操作指数序列
    reverse_mapping = {v: k for k, v in mapping.items()}
    try:
        operations = list(reverse_mapping[mapped_int])
    except KeyError:
        raise ValueError(f"没有找到与整数 {mapped_int} 对应的操作指数序列")
    
    # 应用操作指数序列到最简序列，得到原始序列
    current = simplest_sequence.copy()
    for op in operations:
        if not (1 <= op < len(current)):
            raise ValueError(f"无效的操作指数: {op}")
        # 执行交换操作（第op位与第op+1位交换）
        current[op-1], current[op] = current[op], current[op-1]
    return current

text,salt="as2d5sd6XZ","youmu"
times=5
primes=generate_primes(500)
mapping = fun1() 
list_text=list(text)
list_text_list,list_xulie_list,list_text_final=[],[],[]
list_text_num,list_text_num_list=1,[]
list_temp,num_temp,letter_temp=[],1,"0"
output="youmu"

'''part1:切割字符串(list_text_list)'''
for index_1 in range(len(list_text)//times+1):
    for index_11 in range(0,times):
        if index_1*times+index_11>=len(list_text):
            break
        list_temp.append(list_text[index_1*times+index_11])
    list_text_list.append(list_temp)
    list_temp=[]
    if list_text_list[-1]==[]:
        list_text_list.pop(-1)
print("切割后的字符串列表:", list_text_list)


'''part2:计算各个字符串对应的大质数(list_text_num_list)'''
for index_2,value in enumerate(list_text_list):
    for index_21 in value:
        list_text_num*=num_to_prime(letter_to_num(index_21))
    list_text_num_list.append(list_text_num)
    list_text_num=1
print("字符串对应的大质数列表:", list_text_num_list)


'''part3:计算重排列各个字符串的序列排列指数及其对应的大质数'''
for index_3, value in enumerate(list_text_list):
    _, mapped_int = fun2(value, mapping)
    list_xulie_list.append(num_to_prime(mapped_int + 62))
print("排列指数对应的大质数列表:", list_xulie_list)

'''part4:重组各个字符串'''
for index_4 in range(len(list_text_list)):
    list_text_final.append(list_xulie_list[index_4]*list_text_num_list[index_4])
print("重组结果:", list_text_final)

'''part5:加盐'''
list_salt=list(salt)
if len(list_salt) < times:
    num_temp = len(list_salt)
    for index_50 in range(num_temp,times):
        list_salt.append(list_salt[index_50%num_temp])
else:
    list_salt = list_salt[:times]
num_temp=1
for index_5 in list_salt:
    num_temp*=num_to_prime(letter_to_num(index_5))
_, mapped_int = fun2(list_salt, mapping)
num_temp*=(num_to_prime(mapped_int + 62))
salt_num,num_temp=num_temp,1
for index_51,vaule_51 in enumerate(list_text_final):
    list_text_final[index_51]=xor_to_base62(salt_num,vaule_51)
    if len(list_text_final[index_51])<10:
        output+="0"+str(len(list_text_final[index_51]))+str(list_text_final[index_51])
    else:
        output+=str(len(list_text_final[index_51]))+str(list_text_final[index_51])
print("结果:", output)
