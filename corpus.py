import os
#正则表达式（Regular Expression):匹配字符串中字符组合的模式
import re
#统计词频：导入Counter计数器类
from collections import Counter

# 1.TXT清洗（去标点、小写、分句）
def clean_text(raw):
    # 1. 去掉网址
    raw = re.sub(r'https?://\S+|www\.\S+', '', raw)
    
    # 2. 去掉HTML标签
    raw = re.sub(r'<[^>]+>', '', raw)
    
    # 3. 去掉HTML实体（&amp; &nbsp; 等）
    raw = re.sub(r'&[a-zA-Z]+;', '', raw)
    
    # 4. 去掉方括号引用（[1] [2] [Source] 等）
    raw = re.sub(r'\[.*?\]', '', raw)
    
    # 5. 去掉圆括号里的非英文内容（可选，看情况用）
    #raw = re.sub(r'\([^)]*\)', '', raw)
    
    # 6. 只保留英文字母、空格、句号、问号、感叹号
    raw = re.sub(r'[^a-zA-Z\s\.\?!]', ' ', raw)
    
    # 7. 把连续空格合并成一个
    raw = re.sub(r'\s+', ' ', raw)
    
    # 8. 去掉多余的空格和首尾空白
    raw = raw.strip()

    # 9.处理PDF连字符断行
    raw = re.sub(r'-\n', '', raw)

    # 10.换行变空格
    raw = re.sub(r'\n', ' ', raw)
    return raw

def load_corpus(folder_path):
    texts = []
    for file in os.listdir(folder_path):
        if file.endswith('.txt'):
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
                raw = f.read()
                raw = clean_text(raw)
                texts.append(raw.strip())
    return ' '.join(texts)

# ========== 放在 load_corpus 函数后面 ==========

# 2. 查一个词的出现次数（词频）
def get_freq(word, corpus):
    word_list = re.findall(r'\b\w+\b', corpus.lower())
    count = word_list.count(word.lower())
    if count == 0:
        print(f'未找到 "{word}"，请检查拼写')
    else:
        print(f'"{word}" 出现次数: {count}')
    return count
# 3. 查一个词的上下文（左右各5个词）
def concordance(word, corpus, window=5):
    """
    查一个词的上下文（左右各 window 个词）。
    
    参数：
        word   : 要查的词
        corpus : 语料库（一个大字符串）
        window : 左右各看几个词，默认 5
    
    改进点：
        1. 支持标点后没有空格
        2. 支持多标点 ?! ...
        3. 支持引号包裹的句子
        4. 支持换行符作为句子分隔
        5. 高亮显示用 >>> <<<
    """
    word = word.lower()
    
    # === 第1步：切分句子 ===
    # 匹配规则：
    #   [^\.\?!\n]+  : 一个或多个"非句末标点、非换行"的字符（句子主体）
    #   [\.\?!]*     : 后面跟 0 个或多个句末标点
    #   ["\']?       : 可选的收尾引号
    pattern = r'[^\.\?!\n]+[\.\?!]*["\']?'
    sentences = re.findall(pattern, corpus)
    
    # === 第2步：初始化计数器 ===
    found = 0
    
    # === 第3步：遍历每个句子 ===
    for sent in sentences:
        sent = sent.strip()               # 去首尾空白
        if not sent:                      # 空句子跳过
            continue
        if word not in sent.lower():      # 不含目标词，跳过
            continue
        
        # === 第4步：句内分词 ===
        words = sent.split()
        
        # === 第5步：遍历每个词 ===
        for i, w in enumerate(words):
            # 去标点后比较
            clean_w = w.lower().strip('.,;:!?"\'()[]{}')
            if clean_w != word:
                continue
            
            # === 第6步：找到目标词，记录上下文 ===
            found += 1
            
            # 左边 window 个词
            left_start = max(0, i - window)
            left = ' '.join(words[left_start:i])
            
            # 右边 window 个词 +1规避“左闭右开”
            right_end = i + window + 1
            right = ' '.join(words[i+1:right_end])
            
            # === 第7步：输出 ===
            # 注意左右取词时都可以排除了i，也就是排除了所查word本身
            # 用 >>> <<< 高亮目标词，比 [ ] 更醒目
            print(f'[{found}] {left} >>> {w} <<< {right}')
            print('-' * 60)
    
    # === 第8步：没找到时提示 ===
    if found == 0:
        print(f'未找到 "{word}"')
    
    return found

# 4# ========== 停用词表（需要时取消注释使用） ==========
#     STOP_WORDS = {
#       'the', 'a', 'an', 'and', 'or', 'but', 'if', 'of', 'at', 'by',
#       'for', 'with', 'about', 'to', 'from', 'in', 'on', 'is', 'are',
#       'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
#       'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
#       'might', 'must', 'can', 'this', 'that', 'these', 'those', 'it',
#       'its', 'as', 'so', 'than', 'then', 'there', 'here', 'when',
#       'where', 'which', 'who', 'whom', 'what', 'why', 'how', 'not',
#       'no', 'nor', 'too', 'very', 'just', 'also', 'only', 'own',
#       'same', 'such', 'more', 'most', 'some', 'any', 'all', 'both',
#       'each', 'few', 'other', 'into', 'over', 'after', 'before',
#       'between', 'under', 'above', 'up', 'down', 'out', 'off', 'again'
#   }


def collocates(word, corpus, direction='right', top_n=10, use_stopwords=False):
    """
    查一个词的搭配（左边、右边或双向）。
    
    参数：
        word          : 要查的词
        corpus        : 语料库（大字符串）
        direction     : 搭配方向
                        'right' = 右边搭配（默认）
                        'left'  = 左边搭配
                        'both'  = 左右都查
        top_n         : 显示前 N 个，默认 10
        use_stopwords : 是否过滤停用词，默认 False
                        需要过滤时改为 True
    
    返回：
        一个 Counter 对象（包含所有搭配及次数）
    """
    word = word.lower()
    all_matches = []   # 用来装所有方向的搭配词
    
    # ========== 1. 查右边搭配 ==========
    if direction in ('right', 'both'):
        pattern_right = re.compile(rf'\b{word}\b\s+(\w+)', re.IGNORECASE)
        matches_right = pattern_right.findall(corpus)
        all_matches.extend(matches_right)
    
    # ========== 2. 查左边搭配 ==========
    if direction in ('left', 'both'):
        # 注意：左边搭配的正则和右边相反
        # (\w+)\s+\b{word} 表示"一个词 + 空格 + 目标词"
        pattern_left = re.compile(rf'(\w+)\s+\b{word}\b', re.IGNORECASE)
        matches_left = pattern_left.findall(corpus)
        all_matches.extend(matches_left)
    all_matches = [w.lower()for w in all_matches]
    
    # ========== 3. 过滤停用词（可选） ==========
    # if use_stopwords:
    #     # 把停用词表里的词从搭配结果中剔除
    #     # 需要先取消上面 STOP_WORDS 的注释
    #     all_matches = [w for w in all_matches if w.lower() not in STOP_WORDS]
    
    # ========== 4. 统计词频 ==========
    freq = Counter(all_matches)
    
    # ========== 5. 输出 ==========
    direction_cn = {
        'right': '右边',
        'left' :  '左边',
        'both' :  '左右两边'
    }
    if len(freq) == 0:
        print(f'未找到"{word}"的任何搭配，请检查拼写')
        return freq
    
    print(f'"{word}" {direction_cn[direction]}最常见的搭配:')
    for w, count in freq.most_common(top_n):
        print(f'  {w}: {count}')
    
    return freq

# ========== 主程序调用 ==========
if __name__ == '__main__':
    try:
        corpus = load_corpus('corpus_raw')
    except FileNotFoundError:
        print('错误：找不到 corpus_raw 文件夹')
        print('请先创建文件夹并放入 txt 文件')
        exit()
    
    if not corpus.strip():
        print('错误：语料库为空，请检查 txt 文件内容')
        exit()
    
    print(f'语料库已加载，共 {len(corpus)} 字符')
    print('=' * 40)
    
    while True:
        print('\n请选择功能：')
        print('  1 = 查词频（出现多少次）')
        print('  2 = 查上下文（前后各5词）')
        print('  3 = 查搭配（右边最常见的词）')
        print('  q = 退出')
        
        choice = input('输入选项: ').strip().lower()
        
        if choice == 'q':
            print('Bye!')
            break
        
        if choice not in ('1', '2', '3'):
            print('无效选项，请重新输入')
            continue
        
        word = input('输入要查的词: ').strip()
        
        if not word:
            print('未输入任何词，请重新输入')
            continue
        
        try:
            # ========== 功能1：查词频 ==========
            if choice == '1':
                count = get_freq(word, corpus)
                if count > 0:
                    print(f'（返回值：{count}）')
            
            # ========== 功能2：查上下文 ==========
            elif choice == '2':
                print('\n【上下文查询选项】')
                print('  1 = 默认（左右各5词）')
                print('  2 = 自定义窗口')
                sub = input('输入选项（默认1）: ').strip() or '1'
                
                window = 5   # 默认值
                if sub == '2':
                    w_input = input('左右各看几个词？(默认5) ').strip()
                    if w_input.isdigit():        # 判断是不是数字
                        window = int(w_input)
                    else:
                        print('输入无效，使用默认值 5')
                
                found = concordance(word, corpus, window)
                if found > 0:
                    print(f'（共找到 {found} 处）')
            
            # ========== 功能3：查搭配 ==========
            elif choice == '3':
                print('\n【搭配查询选项】')
                print('  1 = 默认（右边，前10个）')
                print('  2 = 自定义方向')
                print('  3 = 自定义方向 + 数量')
                sub = input('输入选项（默认1）: ').strip() or '1'
                
                direction = 'right'
                top_n = 10
                use_stopwords = False
                
                if sub in ('2', '3'):
                    d_input = input('方向 (right/left/both，默认right): ').strip().lower()
                    if d_input in ('right', 'left', 'both'):
                        direction = d_input
                    else:
                        print('输入无效，使用默认 right')
                
                if sub == '3':
                    n_input = input('显示前几个？(默认10) ').strip()
                    if n_input.isdigit():
                        top_n = int(n_input)
                    else:
                        print('输入无效，使用默认 10')
                
                # 可选：是否过滤停用词（需要先取消 STOP_WORDS 注释）
                sw_input = input('过滤停用词？(y/n，默认n): ').strip().lower()
                use_stopwords = (sw_input == 'y')
                
                freq = collocates(word, corpus, direction, top_n, use_stopwords)
                if len(freq) > 0:
                    print(f'（共 {len(freq)} 种搭配）')
        
        except Exception as e:
            print(f'查询出错: {e}')