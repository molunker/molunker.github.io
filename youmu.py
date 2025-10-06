import pygame
import sys
import os

# 初始化pygame
pygame.init()
pygame.mixer.init()
pygame.font.init()

# 字体设置
font_path = pygame.font.match_font('simsun')
if not font_path:
    font_path = pygame.font.match_font('microsoftyahei')
if not font_path:
    default_font = pygame.font.get_default_font()
    font_path = pygame.font.match_font(default_font)

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
YOUMUgreen = (57, 151, 112)
YOUMUWHITE = (230, 230, 230)

# 获取屏幕分辨率
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
window_width = int(SCREEN_WIDTH * 0.5)
window_height = int(SCREEN_HEIGHT * 0.5)

# 创建窗口
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("youmu加密程序")

# 使用绝对路径加载资源
resource_path = "."

try:
    # 加载背景图片
    background_image = pygame.image.load(os.path.join(resource_path, "background.jpg")).convert()
    bg_original_width, bg_original_height = background_image.get_size()
    bg_aspect_ratio = bg_original_height / bg_original_width  # 高/宽比例

    # 根据背景图片比例计算窗口高度
    window_height = int(window_width * bg_aspect_ratio)

    # 确保窗口高度不会超过屏幕高度
    if window_height > SCREEN_HEIGHT:
        window_height = SCREEN_HEIGHT
        window_width = int(window_height / bg_aspect_ratio)  # 按比例调整宽度

    # 调整窗口大小
    screen = pygame.display.set_mode((window_width, window_height))

    # 缩放背景图片以完全贴合窗口（无变形）
    background_image = pygame.transform.scale(background_image, (window_width, window_height))
except Exception as e:
    print(f"加载背景图片时出错: {e}")
    # 创建一个简单的背景作为备选
    background_image = pygame.Surface((window_width, window_height))
    background_image.fill(GRAY)

try:
    # 加载音乐
    pygame.mixer.music.load(os.path.join(resource_path, "background_music.mp3"))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"加载背景音乐时出错: {e}")

def get_font(size):
    return pygame.font.Font(font_path, size)

prime_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 
              103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 
              211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293]

def letter_to_position(letter):
    # 检查是否为字母
    if not letter.isalpha():
        return None
    if letter.islower():
        idx = ord(letter) - ord('a')
    else:
        idx = ord(letter) - ord('A') + 26
    
    # 检查索引是否在有效范围内
    if 0 <= idx < len(prime_list):
        return prime_list[idx]
    return None

# 全局变量存储密钥
miyao = "youmu"
show_key_window = False  # 控制是否显示密钥修改窗口
key_input = miyao  # 密钥输入框内容
error_message = ""  # 错误信息
last_key_time = 0  # 记录上次按键时间
key_cooldown = 10  # 按键冷却时间(毫秒)，防止输入过快

def calculate_result(input_text):
    global miyao
    if not input_text.strip():
        return "请输入字符"
    
    # 检查输入是否包含无效字符
    for char in input_text:
        if not (char.isalpha() or char == ' '):
            return "输入包含无效字符，仅允许字母和空格"
    
    i = input_text
    if_have_suoxie = 0
    i_list = list(i)
    i_mingcheng , mingcheng_suo = [] , []
    key = str()
    setting_number ,miyao_number = 3 , 1 
    miyao_list = list(miyao)
    
    # 计算密钥数字
    for myao in miyao_list:
        pos = letter_to_position(myao)
        if pos is None:
            return "加密过程出错"
        miyao_number *= pos
    
    for index, value in enumerate(i_list):
        if value == " ":
            if_have_suoxie = 1
            # 提取空格后的缩写
            for night in range(index + 1, len(i_list)):
                key += i_list[night]
            break
        else:
            i_mingcheng.append(value)

    # 处理没有空格的情况
    if if_have_suoxie == 0 and len(i_mingcheng) >= setting_number:
        for c in range(setting_number):     
            key += i_mingcheng[c]
            mingcheng_suo.append(i_mingcheng[c])
    else:
        for c in range(len(i_mingcheng)):
            key += i_mingcheng[c]
            mingcheng_suo.append(i_mingcheng[c])

    # 计算关键数字列表
    key_number_list = []
    for l in mingcheng_suo:
        pos = letter_to_position(l)
        if pos is None:
            return "加密过程出错"
        key_number_list.append(pos)

    key_number_xulie = 1
    for index, value in enumerate(key_number_list):
        if index >= 1 and key_number_list[index] > key_number_list[index - 1]:
            if index + 52 < len(prime_list):
                key_number_xulie *= prime_list[index + 52]

    key_number = 1
    if key: 
        key_list = list(key)
        key_list[0] = key_list[0].upper() 
        key = ''.join(key_list)  
    
    for u in key_number_list:
        key_number *= u
    
    # 处理大数字
    try:
        if abs(miyao_number - key_number) < 1e10:
            if miyao_number - key_number > 0:
                key_number = miyao_number - key_number
            else:
                key_number -= miyao_number
            key += "A" + str(key_number)
        else:
            key_number = int(abs(1e10 - miyao_number - key_number))
            key += "B" + str(key_number)
    except OverflowError:
        return "密钥或加密信息过长"
    
    return f"计算结果: {key}"

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.font = get_font(24)
        self.txt_surface = self.font.render(text, True, BLACK)
        self.active = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = BLUE if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # 只允许输入字母和空格
                    if event.unicode.isalpha() or event.unicode == ' ':
                        self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, BLACK)
        return None
    
    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
    
    def clear(self):
        self.text = ""
        self.txt_surface = self.font.render(self.text, True, BLACK)

class Button:
    def __init__(self, x, y, w, h, text, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.hover_color = WHITE
        self.clicked_color = (150, 150, 150)
        self.text = text
        self.font = get_font(24)
        self.txt_surface = self.font.render(text, True, BLACK)
        self.action = action
        self.is_hovered = False
        self.is_clicked = False
        self.last_click_time = 0
        self.click_cooldown = 300  # 按钮点击冷却时间
    
    def handle_event(self, event):
        current_time = pygame.time.get_ticks()
        
        # 重置点击状态（冷却时间后）
        if current_time - self.last_click_time > self.click_cooldown:
            self.is_clicked = False
        
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
            if self.rect.collidepoint(event.pos) and current_time - self.last_click_time > self.click_cooldown:
                self.is_clicked = True
                self.last_click_time = current_time
                if self.action:
                    self.action()
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # 左键释放
            self.is_clicked = False
    
    def draw(self, screen):
        # 根据状态选择颜色
        if self.is_clicked:
            color = self.clicked_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color
            
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # 边框
        screen.blit(self.txt_surface, (self.rect.x + (self.rect.w - self.txt_surface.get_width()) // 2,
                                      self.rect.y + (self.rect.h - self.txt_surface.get_height()) // 2))

def handle_key_window_events():
    """单独处理密钥窗口事件，避免刷新过快导致的问题"""
    global key_input, error_message, show_key_window, miyao, last_key_time
    
    current_time = pygame.time.get_ticks()
    events = pygame.event.get()
    
    # 创建按钮（仅用于事件处理）
    win_width, win_height = 400, 220
    win_x = (window_width - win_width) // 2
    win_y = (window_height - win_height) // 2
    
    save_btn = Button(win_x + 50, win_y + 180, 120, 35, "保存")
    cancel_btn = Button(win_x + 230, win_y + 180, 120, 35, "取消")
    
    # 处理按钮事件
    for event in events:
        save_btn.handle_event(event)
        cancel_btn.handle_event(event)
        
        # 点击关闭窗口
        if event.type == pygame.QUIT:
            return False
        
        # 点击保存按钮
        if save_btn.is_clicked:
            if not key_input.strip():
                error_message = "密钥不能为空！"
            elif not key_input.isalpha():
                error_message = "密钥只能包含字母！"
            else:
                miyao = key_input
                show_key_window = False
                error_message = ""
        
        # 点击取消按钮
        if cancel_btn.is_clicked:
            show_key_window = False
            error_message = ""
            key_input = miyao  # 恢复为当前密钥
        
        # 键盘输入处理（带冷却时间）
        if event.type == pygame.KEYDOWN:
            if current_time - last_key_time > key_cooldown:
                last_key_time = current_time
                
                if event.key == pygame.K_ESCAPE:  # 按ESC键关闭窗口
                    show_key_window = False
                    error_message = ""
                    key_input = miyao
                elif event.key == pygame.K_RETURN:  # 按Enter键保存
                    if not key_input.strip():
                        error_message = "密钥不能为空！"
                    elif not key_input.isalpha():
                        error_message = "密钥只能包含字母！"
                    else:
                        miyao = key_input
                        show_key_window = False
                        error_message = ""
                elif event.key == pygame.K_BACKSPACE:  # 退格键
                    key_input = key_input[:-1]
                    error_message = ""
                elif event.unicode.isalpha():  # 只允许字母输入
                    key_input += event.unicode
                    error_message = ""
    
    return True

def draw_key_window():
    """绘制密钥修改窗口"""
    global key_input, error_message
    
    # 创建半透明遮罩
    overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # 黑色半透明
    screen.blit(overlay, (0, 0))
    
    # 窗口尺寸和位置
    win_width, win_height = 400, 220
    win_x = (window_width - win_width) // 2
    win_y = (window_height - win_height) // 2
    
    # 绘制窗口背景
    pygame.draw.rect(screen, WHITE, (win_x, win_y, win_width, win_height))
    pygame.draw.rect(screen, BLACK, (win_x, win_y, win_width, win_height), 2)  # 边框
    
    # 窗口标题
    title_font = get_font(28)
    title_surface = title_font.render("更改密钥", True, BLACK)
    screen.blit(title_surface, (win_x + (win_width - title_surface.get_width()) // 2, win_y + 15))
    
    # 提示文本
    hint_font = get_font(20)
    hint_surface = hint_font.render("请输入新密钥（仅字母）:", True, BLACK)
    screen.blit(hint_surface, (win_x + 30, win_y + 60))
    
    # 输入框
    input_rect = pygame.Rect(win_x + 30, win_y + 100, win_width - 60, 40)
    pygame.draw.rect(screen, WHITE, input_rect)
    pygame.draw.rect(screen, BLUE, input_rect, 2)
    
    # 输入文本
    input_font = get_font(24)
    input_surface = input_font.render(key_input, True, BLACK)
    screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))
    
    # 错误信息
    if error_message:
        error_font = get_font(18)
        error_surface = error_font.render(error_message, True, RED)
        screen.blit(error_surface, (win_x + 30, win_y + 150))
    
    # 创建并绘制按钮
    save_btn = Button(win_x + 50, win_y + 180, 120, 35, "保存")
    cancel_btn = Button(win_x + 230, win_y + 180, 120, 35, "取消")
    
    # 绘制按钮
    save_btn.draw(screen)
    cancel_btn.draw(screen)

def main():
    clock = pygame.time.Clock()

    # 调整界面元素位置，使其在窗口内居中
    input_box_width = window_width * 0.85
    input_box_height = 50
    input_box_x = (window_width - input_box_width) // 2
    input_box_y = window_height * 0.3
    input_box = InputBox(input_box_x, input_box_y, input_box_width, input_box_height)

    result_text = ""
    copy_hint = ""
    
    def calculate_action():
        nonlocal result_text, copy_hint
        result = calculate_result(input_box.text)
        result_text = result
        copy_hint = ""
        
        if result == "请输入字符" or result.startswith("输入包含无效字符"):
            pass
        elif not result.startswith("加密过程出错") and not result.startswith("加密过程中出现数字溢出"):
            result_value = result.split(": ")[1]
            # 复制到剪贴板
            pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, result_value.encode('utf-8'))
            copy_hint = "结果已复制到剪贴板"
        
        input_box.clear()
    
    def open_key_window():
        """打开密钥修改窗口"""
        global show_key_window, key_input
        show_key_window = True
        key_input = miyao  # 初始化为当前密钥
    
    # 计算按钮
    button_width = window_width * 0.3
    button_height = 50
    button_x = (window_width - button_width) // 2
    button_y = window_height * 0.5
    calculate_button = Button(button_x, button_y, button_width, button_height, "计算", calculate_action)
    
    # 更改密钥按钮（左上角）
    key_button = Button(15, 25, 120, 40, "更改密钥", open_key_window)
    
    running = True
    while running:
        # 处理事件
        if show_key_window:
            # 密钥窗口事件单独处理
            if not handle_key_window_events():
                running = False
        else:
            # 主界面事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                input_result = input_box.handle_event(event)
                if input_result is not None:
                    calculate_action()
                
                calculate_button.handle_event(event)
                key_button.handle_event(event)
        
        # 绘制主界面
        screen.blit(background_image, (0, 0))
        
        title_font = get_font(36)
        title_surface = title_font.render("youmu加密程序", True, YOUMUWHITE)
        title_x = (window_width - title_surface.get_width()) // 2
        screen.blit(title_surface, (title_x, window_height * 0.05))
        
        input_font = get_font(20)
        input_surface = input_font.render("请输入字母(可包含空格):", True, YOUMUgreen)
        input_x = (window_width - input_surface.get_width()) // 2
        screen.blit(input_surface, (input_x, window_height * 0.15))
        
        input_box.draw(screen)
        calculate_button.draw(screen)
        key_button.draw(screen)  # 绘制更改密钥按钮
        
        if result_text:
            result_font = get_font(24)
            # 设置结果文本颜色
            if result_text in ["请输入字符", "输入包含无效字符，仅允许字母和空格", "加密过程出错", "加密过程中出现数字溢出"]:
                color = RED
            else:
                color = YOUMUWHITE
            result_surface = result_font.render(result_text, True, color)
            result_x = (window_width - result_surface.get_width()) // 2
            screen.blit(result_surface, (result_x, window_height * 0.6))
        
        if copy_hint:
            hint_font = get_font(20)
            hint_surface = hint_font.render(copy_hint, True, YOUMUgreen)
            hint_x = (window_width - hint_surface.get_width()) // 2
            screen.blit(hint_surface, (hint_x, window_height * 0.7))
        
        # 如果需要显示密钥修改窗口，则绘制它
        if show_key_window:
            draw_key_window()
        
        pygame.display.flip()
        clock.tick(60)  # 适当提高帧率，使界面更流畅
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    