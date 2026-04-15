import sys
import math
import time
import random
from datetime import datetime

# 尝试导入PyQt5，如果失败则使用PyQt6
try:
    from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                QTextEdit, QLineEdit, QPushButton, QLabel, QDialog)
    from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, QRect, QPoint, 
                             QEasingCurve, pyqtSignal, QThread)
    from PyQt5.QtGui import (QPainter, QColor, QBrush, QPen, QFont, 
                            QPalette, QRadialGradient, QLinearGradient, QPainterPath)
    print("使用 PyQt5")
except ImportError:
    from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                QTextEdit, QLineEdit, QPushButton, QLabel, QDialog)
    from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QRect, QPoint, 
                             QEasingCurve, pyqtSignal, QThread)
    from PyQt6.QtGui import (QPainter, QColor, QBrush, QPen, QFont, 
                            QPalette, QRadialGradient, QLinearGradient, QPainterPath)
    print("使用 PyQt6")

class BeautifulAIPet(QWidget):
    """高颜值AI桌宠 - 专注极致视觉体验"""
    
    mood_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 基础属性
        self.radius = 45
        self.current_mood = "normal"
        self.animation_time = 0
        
        # 视觉效果
        self.energy_particles = []
        self.energy_waves = []  # 点击时的能量波
        self.orbit_particles = []
        
        # 眼神跟踪
        self.mouse_pos = QPoint(0, 0)
        self.eye_target = QPoint(0, 0)
        self.blink_timer = 0
        self.is_blinking = False
        
        # 悬浮效果
        self.float_offset = QPoint(0, 0)
        self.base_position = QPoint(0, 0)
        
        # 拖拽
        self.drag_position = QPoint()
        self.chat_bubble = None
        
        self.init_ui()
        self.init_effects()
        
    def init_ui(self):
        """初始化界面 - 回滚到安全版本"""
        # 简单可靠的窗口设置
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFixedSize(140, 140)
        self.move(300, 300)
        self.base_position = self.pos()
        self.setMouseTracking(True)
        
    def init_effects(self):
        """初始化视觉效果"""
        # 主渲染定时器 - 60fps确保流畅
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update_all_effects)
        self.render_timer.start(16)  # 60fps
        
        # 初始化粒子系统
        self.init_particles()
        
    def init_particles(self):
        """初始化粒子效果"""
        # 轨道粒子 - 围绕主体旋转
        for i in range(12):
            angle = i * (2 * math.pi / 12)
            particle = {
                'angle': angle,
                'distance': 65 + random.uniform(-5, 5),
                'speed': 0.015 + random.uniform(-0.005, 0.005),
                'size': random.uniform(1.5, 3),
                'alpha': random.uniform(0.4, 0.8),
                'pulse_phase': random.uniform(0, 2 * math.pi),
                'type': 'orbit'
            }
            particle['current_alpha'] = particle['alpha'] 
            self.orbit_particles.append(particle)
            
        # 内部能量粒子 - 球体内部闪烁
        for i in range(8):
            particle = {
                'x': random.uniform(-30, 30),
                'y': random.uniform(-30, 30),
                'size': random.uniform(0.8, 2),
                'alpha': random.uniform(0.3, 0.7),
                'pulse_phase': random.uniform(0, 2 * math.pi),
                'pulse_speed': random.uniform(0.05, 0.15),
                'type': 'energy'
            }
            particle['current_alpha'] = particle['alpha']  # 初始化 current_alpha
            self.energy_particles.append(particle)
    
    def update_all_effects(self):
        """更新所有视觉效果"""
        self.animation_time += 0.016
        
        # 1. 悬浮效果
        self.update_floating()
        
        # 2. 粒子系统
        self.update_particles()
        
        # 3. 眼神跟踪
        self.update_eye_tracking()
        
        # 4. 眨眼系统
        self.update_blinking()
        
        # 5. 能量波效果
        self.update_energy_waves()
        
        # 6. 应用悬浮位置
        self.apply_floating()
        
        self.update()
    
    def update_floating(self):
        """轻柔悬浮效果"""
        # 8字形轨迹，非常轻微
        float_x = 2 * math.sin(self.animation_time * 0.8)
        float_y = 1.5 * math.sin(self.animation_time * 1.2)
        self.float_offset = QPoint(int(float_x), int(float_y))
    
    def update_particles(self):
        """更新粒子效果"""
        # 轨道粒子
        for particle in self.orbit_particles:
            particle['angle'] += particle['speed']
            particle['pulse_phase'] += 0.08
            
            # 脉冲透明度
            pulse = 0.6 + 0.4 * math.sin(particle['pulse_phase'])
            particle['current_alpha'] = particle['alpha'] * pulse
            
        # 内部能量粒子
        for particle in self.energy_particles:
            particle['pulse_phase'] += particle['pulse_speed']
            pulse = 0.5 + 0.5 * math.sin(particle['pulse_phase'])
            particle['current_alpha'] = particle['alpha'] * pulse
    
    def update_eye_tracking(self):
        """眼神跟踪鼠标 - 全屏范围，限制眼球不出框"""
        try:
            # 获取全局鼠标位置
            global_mouse = QApplication.instance().desktop().cursor().pos()
            pet_center = self.geometry().center()
            
            # 计算相对位置
            dx = global_mouse.x() - pet_center.x()
            dy = global_mouse.y() - pet_center.y()
            distance = math.sqrt(dx*dx + dy*dy)
            
            # 眼神跟踪范围 - 适中的移动幅度
            eye_range = 6  # 减小眼球移动范围，确保不出框
            
            if distance > 0:
                # 计算眼球位置，距离越远移动越明显
                factor = min(distance / 500, 1.0)  # 150px开始明显移动
                
                target_x = (dx / distance) * eye_range * factor
                target_y = (dy / distance) * eye_range * factor
                
                # 严格限制在眼眶内
                target_x = max(-eye_range, min(eye_range, target_x))
                target_y = max(-eye_range, min(eye_range, target_y))
                
                self.eye_target = QPoint(int(target_x), int(target_y))
            else:
                self.eye_target = QPoint(0, 0)
                
        except:
            self.eye_target = QPoint(0, 0)
    
    def update_blinking(self):
        """自然眨眼系统"""
        self.blink_timer += 0.016
        
        # 随机眨眼间隔 2-6秒
        if self.blink_timer > random.uniform(2, 6) and not self.is_blinking:
            self.is_blinking = True
            self.blink_timer = 0
            
        # 眨眼持续时间
        if self.is_blinking and self.blink_timer > 0.15:
            self.is_blinking = False
            self.blink_timer = 0
    
    def update_energy_waves(self):
        """更新能量波效果"""
        # 移除过期的能量波
        self.energy_waves = [wave for wave in self.energy_waves 
                           if wave['life'] < wave['max_life']]
        
        # 更新现有能量波
        for wave in self.energy_waves:
            wave['life'] += 0.016
            progress = wave['life'] / wave['max_life']
            wave['radius'] = wave['max_radius'] * progress
            wave['alpha'] = int(255 * (1 - progress) * 0.6)
    
    def apply_floating(self):
        """应用悬浮效果"""
        if self.drag_position.isNull():
            new_pos = self.base_position + self.float_offset
            if self.pos() != new_pos:
                self.move(new_pos)
    
    def paintEvent(self, event):
        """主绘制函数"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # 1. 绘制外围效果
        self.draw_outer_effects(painter, center_x, center_y)
        
        # 2. 绘制轨道粒子
        self.draw_orbit_particles(painter, center_x, center_y)
        
        # 3. 绘制主体核心
        self.draw_main_core(painter, center_x, center_y)
        
        # 4. 绘制内部效果
        self.draw_inner_effects(painter, center_x, center_y)
        
        # 5. 绘制眼睛
        self.draw_eyes(painter, center_x, center_y)
        
        # 6. 绘制能量波
        self.draw_energy_waves(painter, center_x, center_y)
    
    def draw_outer_effects(self, painter, x, y):
        """绘制外围光环效果"""
        # 外层光环 - 3层渐变环
        for i in range(3):
            ring_radius = self.radius + 20 + i * 10
            alpha = int(30 * (1 - i * 0.3))
            
            # 渐变环
            gradient = QRadialGradient(x, y, ring_radius)
            gradient.setColorAt(0.8, QColor(100, 180, 255, 0))
            gradient.setColorAt(0.95, QColor(100, 180, 255, alpha))
            gradient.setColorAt(1.0, QColor(100, 180, 255, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - ring_radius, y - ring_radius,
                              ring_radius * 2, ring_radius * 2)
    
    def draw_orbit_particles(self, painter, x, y):
        """绘制轨道粒子 - 增强效果"""
        for particle in self.orbit_particles:
            px = x + particle['distance'] * math.cos(particle['angle'])
            py = y + particle['distance'] * math.sin(particle['angle'])
            
            alpha = int(255 * particle['current_alpha'])
            size = particle['size']
            
            # 粒子拖尾效果
            trail_length = 15
            for i in range(trail_length):
                trail_alpha = alpha * (1 - i / trail_length) * 0.3
                if trail_alpha > 10:
                    trail_angle = particle['angle'] - i * particle['speed'] * 3
                    trail_x = x + particle['distance'] * math.cos(trail_angle)
                    trail_y = y + particle['distance'] * math.sin(trail_angle)
                    
                    trail_gradient = QRadialGradient(trail_x, trail_y, size * 2)
                    trail_gradient.setColorAt(0, QColor(120, 200, 255, int(trail_alpha)))
                    trail_gradient.setColorAt(1, QColor(120, 200, 255, 0))
                    
                    painter.setBrush(QBrush(trail_gradient))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(int(trail_x - size), int(trail_y - size),
                                      int(size * 2), int(size * 2))
            
            # 主粒子 - 多层光晕
            # 外层光晕
            outer_gradient = QRadialGradient(px, py, size * 5)
            outer_gradient.setColorAt(0, QColor(120, 200, 255, alpha // 3))
            outer_gradient.setColorAt(0.3, QColor(100, 180, 255, alpha // 4))
            outer_gradient.setColorAt(1, QColor(80, 160, 255, 0))
            
            painter.setBrush(QBrush(outer_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(px - size * 5), int(py - size * 5),
                              int(size * 10), int(size * 10))
            
            # 中层光晕
            mid_gradient = QRadialGradient(px, py, size * 3)
            mid_gradient.setColorAt(0, QColor(140, 210, 255, alpha // 2))
            mid_gradient.setColorAt(0.5, QColor(120, 200, 255, alpha // 3))
            mid_gradient.setColorAt(1, QColor(100, 180, 255, 0))
            
            painter.setBrush(QBrush(mid_gradient))
            painter.drawEllipse(int(px - size * 3), int(py - size * 3),
                              int(size * 6), int(size * 6))
            
            # 核心粒子
            core_gradient = QRadialGradient(px, py, size)
            core_gradient.setColorAt(0, QColor(255, 255, 255, alpha))
            core_gradient.setColorAt(0.7, QColor(160, 220, 255, alpha))
            core_gradient.setColorAt(1, QColor(120, 200, 255, alpha // 2))
            
            painter.setBrush(QBrush(core_gradient))
            painter.drawEllipse(int(px - size), int(py - size),
                              int(size * 2), int(size * 2))
    
    def draw_main_core(self, painter, x, y):
        """绘制主体核心 - 增强炫酷效果"""
        # 动态脉冲效果
        pulse = 0.9 + 0.1 * math.sin(self.animation_time * 3)
        current_radius = self.radius * pulse
        
        # 外层发光环
        for i in range(3):
            glow_radius = current_radius + 8 + i * 3
            glow_alpha = int(40 * (1 - i * 0.3) * pulse)
            
            glow_gradient = QRadialGradient(x, y, glow_radius)
            glow_gradient.setColorAt(0.7, QColor(100, 180, 255, 0))
            glow_gradient.setColorAt(0.9, QColor(120, 200, 255, glow_alpha))
            glow_gradient.setColorAt(1.0, QColor(100, 180, 255, 0))
            
            painter.setBrush(QBrush(glow_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x - glow_radius), int(y - glow_radius),
                              int(glow_radius * 2), int(glow_radius * 2))
        
        # 主渐变 - 深蓝到亮蓝，增强层次
        main_gradient = QRadialGradient(x - 12, y - 12, current_radius * 1.2)
        main_gradient.setColorAt(0, QColor(180, 220, 255, 200))     # 中心最亮
        main_gradient.setColorAt(0.2, QColor(140, 190, 255, 230))   # 亮蓝区域
        main_gradient.setColorAt(0.5, QColor(100, 160, 240, 245))   # 过渡区域
        main_gradient.setColorAt(0.8, QColor(60, 120, 200, 250))    # 深蓝区域
        main_gradient.setColorAt(1.0, QColor(30, 80, 150, 255))     # 边缘最深
        
        # 动态边框光晕
        border_intensity = 0.8 + 0.3 * math.sin(self.animation_time * 4)
        border_alpha = int(120 + 80 * border_intensity)
        border_color = QColor(120, 200, 255, border_alpha)
        
        painter.setBrush(QBrush(main_gradient))
        painter.setPen(QPen(border_color, 3))
        painter.drawEllipse(int(x - current_radius), int(y - current_radius),
                          int(current_radius * 2), int(current_radius * 2))
        
        # 多层高光效果
        # 主高光
        highlight1 = QRadialGradient(x - 15, y - 15, 30)
        highlight1.setColorAt(0, QColor(255, 255, 255, 150))
        highlight1.setColorAt(0.5, QColor(255, 255, 255, 80))
        highlight1.setColorAt(1, QColor(255, 255, 255, 0))
        
        painter.setBrush(QBrush(highlight1))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(x - 25, y - 25, 40, 35)
        
        # 次高光
        highlight2 = QRadialGradient(x - 20, y - 20, 20)
        highlight2.setColorAt(0, QColor(200, 230, 255, 100))
        highlight2.setColorAt(1, QColor(200, 230, 255, 0))
        
        painter.setBrush(QBrush(highlight2))
        painter.drawEllipse(x - 30, y - 30, 25, 20)
        
        # 核心亮点 - 跳动效果
        core_pulse = 0.7 + 0.4 * math.sin(self.animation_time * 6)
        core_size = 6 * core_pulse
        core_gradient = QRadialGradient(x - 8, y - 8, core_size)
        core_gradient.setColorAt(0, QColor(255, 255, 255, int(200 * core_pulse)))
        core_gradient.setColorAt(1, QColor(180, 220, 255, int(100 * core_pulse)))
        
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(x - 8 - core_size//2), int(y - 8 - core_size//2),
                          int(core_size), int(core_size))
    
    def draw_inner_effects(self, painter, x, y):
        """绘制内部星点效果"""
        for particle in self.energy_particles:
            px = x + particle['x']
            py = y + particle['y']
            
            # 只绘制在球体内的粒子
            dx = particle['x']
            dy = particle['y']
            if dx*dx + dy*dy <= (self.radius - 5) * (self.radius - 5):
                alpha = int(255 * particle['current_alpha'])
                size = particle['size']
                
                painter.setBrush(QBrush(QColor(200, 220, 255, alpha)))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(int(px - size), int(py - size),
                                  int(size * 2), int(size * 2))
    
    def draw_eyes(self, painter, x, y):
        """绘制灵动的眼睛 - 眼眶也跟着动"""
        # 眼眶跟随眼球轻微移动
        eye_offset_factor = 2  # 眼眶跟随比例
        left_socket_x = x - 15 + self.eye_target.x() * eye_offset_factor
        left_socket_y = y - 8 + self.eye_target.y() * eye_offset_factor
        right_socket_x = x + 15 + self.eye_target.x() * eye_offset_factor  
        right_socket_y = y - 8 + self.eye_target.y() * eye_offset_factor
        
        if self.is_blinking:
            # 眨眼状态 - 绘制眼睑
            painter.setPen(QPen(QColor(200, 220, 255, 180), 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(int(left_socket_x - 5), int(left_socket_y), 
                           int(left_socket_x + 5), int(left_socket_y))
            painter.drawLine(int(right_socket_x - 5), int(right_socket_y),
                           int(right_socket_x + 5), int(right_socket_y))
        else:
            # 正常状态 - 绘制眼睛
            eye_size = 8  # 稍微增大眼睛
            pupil_size = 5
            
            # 眼眶光晕效果
            glow_size = eye_size + 4
            glow_gradient = QRadialGradient(left_socket_x, left_socket_y, glow_size)
            glow_gradient.setColorAt(0, QColor(150, 200, 255, 60))
            glow_gradient.setColorAt(1, QColor(150, 200, 255, 0))
            
            painter.setBrush(QBrush(glow_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(left_socket_x - glow_size), int(left_socket_y - glow_size),
                              glow_size * 2, glow_size * 2)
            painter.drawEllipse(int(right_socket_x - glow_size), int(right_socket_y - glow_size),
                              glow_size * 2, glow_size * 2)
            
            # 眼白 - 带轻微渐变
            eye_gradient = QRadialGradient(left_socket_x, left_socket_y, eye_size)
            eye_gradient.setColorAt(0, QColor(255, 255, 255, 220))
            eye_gradient.setColorAt(1, QColor(240, 245, 255, 200))
            
            painter.setBrush(QBrush(eye_gradient))
            painter.setPen(QPen(QColor(180, 200, 255, 120), 1))
            
            # 左眼
            painter.drawEllipse(int(left_socket_x - eye_size//2), int(left_socket_y - eye_size//2), 
                              eye_size, eye_size)
            # 右眼  
            painter.drawEllipse(int(right_socket_x - eye_size//2), int(right_socket_y - eye_size//2),
                              eye_size, eye_size)
            
            # 瞳孔 - 跟随鼠标，带深度感
            pupil_gradient = QRadialGradient(0, 0, pupil_size)
            pupil_gradient.setColorAt(0, QColor(40, 60, 100, 220))
            pupil_gradient.setColorAt(0.7, QColor(60, 80, 120, 240))
            pupil_gradient.setColorAt(1, QColor(20, 40, 80, 255))
            
            painter.setBrush(QBrush(pupil_gradient))
            painter.setPen(Qt.NoPen)
            
            # 左瞳孔
            left_pupil_x = left_socket_x + self.eye_target.x()
            left_pupil_y = left_socket_y + self.eye_target.y()
            painter.drawEllipse(int(left_pupil_x - pupil_size//2), 
                              int(left_pupil_y - pupil_size//2),
                              pupil_size, pupil_size)
            
            # 右瞳孔
            right_pupil_x = right_socket_x + self.eye_target.x()
            right_pupil_y = right_socket_y + self.eye_target.y()
            painter.drawEllipse(int(right_pupil_x - pupil_size//2),
                              int(right_pupil_y - pupil_size//2), 
                              pupil_size, pupil_size)
            
            # 眼睛高光 - 增强立体感
            highlight_color = QColor(255, 255, 255, 200)
            painter.setBrush(QBrush(highlight_color))
            # 主高光
            painter.drawEllipse(int(left_pupil_x - 1.5), int(left_pupil_y - 1.5), 3, 3)
            painter.drawEllipse(int(right_pupil_x - 1.5), int(right_pupil_y - 1.5), 3, 3)
            # 次高光
            secondary_highlight = QColor(255, 255, 255, 100)
            painter.setBrush(QBrush(secondary_highlight))
            painter.drawEllipse(int(left_pupil_x + 1), int(left_pupil_y + 1), 2, 2)
            painter.drawEllipse(int(right_pupil_x + 1), int(right_pupil_y + 1), 2, 2)
    
    def draw_energy_waves(self, painter, x, y):
        """绘制点击时的能量波"""
        for wave in self.energy_waves:
            if wave['alpha'] > 0:
                painter.setPen(QPen(QColor(120, 200, 255, wave['alpha']), 2))
                painter.setBrush(Qt.NoBrush)
                radius = wave['radius']
                painter.drawEllipse(int(x - radius), int(y - radius),
                                  int(radius * 2), int(radius * 2))
    
    def mousePressEvent(self, event):
        """鼠标点击 - 产生能量波"""
        if event.button() == Qt.LeftButton:
            # 记录拖拽位置
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            
            # 创建能量波效果
            wave = {
                'radius': 0,
                'max_radius': 80,
                'life': 0,
                'max_life': 1.0,  # 1秒
                'alpha': 255
            }
            self.energy_waves.append(wave)
            
            # 切换心情
            moods = ["normal", "happy", "excited"]
            current_index = moods.index(self.current_mood) if self.current_mood in moods else 0
            self.current_mood = moods[(current_index + 1) % len(moods)]
            
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标拖拽"""
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            self.base_position = new_pos
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        if event.button() == Qt.LeftButton:
            self.drag_position = QPoint()
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """双击显示对话气泡"""
        if event.button() == Qt.LeftButton:
            self.show_chat_bubble("你好！我是你的AI伙伴~ ✨")
    
    def contextMenuEvent(self, event):
        """右键菜单"""
        messages = [
            "今天过得怎么样？😊",
            "需要我陪你聊天吗？💭", 
            "我在这里哦~ 🌟",
            "有什么可以帮你的吗？🤖",
            "让我们一起加油吧！💪"
        ]
        message = random.choice(messages)
        self.show_chat_bubble(message)
    
    def show_chat_bubble(self, message):
        """显示聊天气泡"""
        if self.chat_bubble:
            self.chat_bubble.close()
            
        self.chat_bubble = ChatBubble(message, self)
        
        # 定位在AI右上方
        pet_pos = self.pos()
        bubble_x = pet_pos.x() + 100
        bubble_y = pet_pos.y() - 80
        self.chat_bubble.move(bubble_x, bubble_y)
        self.chat_bubble.show()

class ChatBubble(QWidget):
    """聊天气泡"""
    
    def __init__(self, message, parent_pet):
        super().__init__()
        self.message = message
        self.parent_pet = parent_pet
        self.typing_index = 0
        self.displayed_text = ""
        
        self.init_ui()
        self.start_typing()
    
    def init_ui(self):
        """初始化气泡界面"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 计算气泡大小
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.message)
        text_height = font_metrics.height()
        
        bubble_width = min(max(text_width + 40, 120), 300)
        bubble_height = text_height + 30
        
        self.setFixedSize(bubble_width, bubble_height)
        
        # 自动消失定时器
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.fade_out)
        self.fade_timer.setSingleShot(True)
        self.fade_timer.start(3000)  # 3秒后开始淡出
        
        # 打字效果定时器
        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.type_next_char)
        
    def start_typing(self):
        """开始打字效果"""
        self.typing_timer.start(50)  # 50ms一个字符
        
    def type_next_char(self):
        """打字效果 - 下一个字符"""
        if self.typing_index < len(self.message):
            self.displayed_text += self.message[self.typing_index]
            self.typing_index += 1
            self.update()
        else:
            self.typing_timer.stop()
    
    def paintEvent(self, event):
        """绘制气泡"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 气泡背景
        bubble_rect = QRect(10, 10, self.width() - 20, self.height() - 20)
        
        # 渐变背景
        gradient = QLinearGradient(0, 0, 0, bubble_rect.height())
        gradient.setColorAt(0, QColor(248, 249, 250, 240))
        gradient.setColorAt(1, QColor(240, 242, 245, 240))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(200, 210, 220, 200), 2))
        painter.drawRoundedRect(bubble_rect, 15, 15)
        
        # 小尾巴
        tail_points = [
            QPoint(25, bubble_rect.bottom()),
            QPoint(15, bubble_rect.bottom() + 10), 
            QPoint(35, bubble_rect.bottom())
        ]
        painter.drawPolygon(tail_points)
        
        # 文字
        painter.setPen(QColor(80, 90, 100))
        painter.setFont(QFont("Arial", 11))
        text_rect = bubble_rect.adjusted(15, 8, -15, -8)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.displayed_text)
    
    def fade_out(self):
        """淡出并关闭"""
        self.close()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 创建高颜值AI桌宠
    ai_pet = BeautifulAIPet()
    ai_pet.show()
    
    print("🎨 炫酷AI桌宠启动成功！")
    print("✨ 增强特性:")
    print("  - 深蓝渐变科技球体 + 动态脉冲")
    print("  - 眼神跟随鼠标 (全屏范围)")
    print("  - 眼眶跟随眼球微动")
    print("  - 自然眨眼系统") 
    print("  - 轻柔悬浮效果")
    print("  - 增强粒子系统 + 拖尾效果")
    print("  - 多层光晕 + 核心亮点跳动")
    print("  - 点击能量波扩散")
    print("🖱️ 交互:")
    print("  - 拖拽: 移动位置")
    print("  - 单击: 能量波 + 切换心情")
    print("  - 双击: 问候对话")
    print("  - 右键: 随机聊天")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()