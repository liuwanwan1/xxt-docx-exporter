# -*- coding: utf-8 -*-
"""
学习通作业提取工具 - Android版
Xxt-Docx-Exporter for Android
基于Kivy框架的移动端应用
"""
import os
import sys
import json
import threading
from datetime import datetime
from pathlib import Path

# Add parent directory to path for importing my_xxt module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle

from my_xxt.api import NewXxt
from my_xxt.export_docx import generate_docx_from_json, batch_export_to_docx


# ── Color Theme ──
THEME = {
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'accent': '#FF9800',
    'success': '#4CAF50',
    'danger': '#F44336',
    'warning': '#FFC107',
    'bg': '#F5F5F5',
    'card': '#FFFFFF',
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'divider': '#E0E0E0',
}


class ColoredLabel(Label):
    """Helper for colored labels"""
    pass


class LoadingPopup(Popup):
    """Loading spinner popup"""
    def __init__(self, message="加载中...", **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.separator_height = 0
        self.size_hint = (0.5, 0.3)
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        spinner = Spinner(color=get_color_from_hex(THEME['primary']))
        label = Label(text=message, color=get_color_from_hex(THEME['text_primary']),
                     font_size=dp(14))
        layout.add_widget(spinner)
        layout.add_widget(label)
        self.content = layout


class Toast(Popup):
    """Toast-like notification popup"""
    def __init__(self, message, duration=2, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.separator_height = 0
        self.size_hint = (0.8, 0.1)
        self.auto_dismiss = True

        label = Label(text=message, color=(1,1,1,1), font_size=dp(13))
        self.content = label
        Clock.schedule_once(lambda dt: self.dismiss(), duration)


# ── Screens ──

class WelcomeScreen(Screen):
    """Welcome / Home screen with cover image"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Cover image at top
        cover_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img', 'cover.jpg')
        if not os.path.exists(cover_path):
            cover_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img', 'img_3.png')

        cover = Image(
            source=cover_path,
            size_hint=(1, 0.35),
            keep_ratio=True,
            allow_stretch=True
        )
        main_layout.add_widget(cover)

        # App title
        title = Label(
            text='学习通作业提取工具',
            font_size=dp(22),
            bold=True,
            color=get_color_from_hex(THEME['primary_dark']),
            size_hint=(1, 0.08),
            font_name='DroidSansFallback.ttf'
        )
        main_layout.add_widget(title)

        # Subtitle
        subtitle = Label(
            text='一键提取作业 · 导出Word文档',
            font_size=dp(14),
            color=get_color_from_hex(THEME['text_secondary']),
            size_hint=(1, 0.05),
        )
        main_layout.add_widget(subtitle)

        # Version
        version = Label(
            text='v1.0.0',
            font_size=dp(11),
            color=get_color_from_hex(THEME['text_secondary']),
            size_hint=(1, 0.04),
        )
        main_layout.add_widget(version)

        # Spacer
        main_layout.add_widget(BoxLayout(size_hint=(1, 0.05)))

        # Login buttons
        btn_layout = BoxLayout(orientation='vertical', spacing=dp(12), size_hint=(1, 0.3),
                               padding=[dp(30), 0])

        phone_login_btn = Button(
            text='📱  手机号密码登录',
            font_size=dp(15),
            background_color=get_color_from_hex(THEME['primary']),
            background_normal='',
            color=(1,1,1,1),
            size_hint=(1, 0.3),
        )
        phone_login_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'phone_login'))
        btn_layout.add_widget(phone_login_btn)

        qr_login_btn = Button(
            text='📷  扫码登录',
            font_size=dp(15),
            background_color=get_color_from_hex(THEME['accent']),
            background_normal='',
            color=(1,1,1,1),
            size_hint=(1, 0.3),
        )
        qr_login_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'qr_login'))
        btn_layout.add_widget(qr_login_btn)

        # Export directly button (if already logged in)
        export_btn = Button(
            text='📄  查看导出历史',
            font_size=dp(15),
            background_color=get_color_from_hex(THEME['success']),
            background_normal='',
            color=(1,1,1,1),
            size_hint=(1, 0.3),
        )
        export_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'export'))
        btn_layout.add_widget(export_btn)

        main_layout.add_widget(btn_layout)

        # Disclaimer
        disclaimer = Label(
            text='⚠️ 仅供学习交流使用，请遵守平台规则',
            font_size=dp(10),
            color=get_color_from_hex('#AAAAAA'),
            size_hint=(1, 0.05),
        )
        main_layout.add_widget(disclaimer)

        self.add_widget(main_layout)


class PhoneLoginScreen(Screen):
    """Phone + Password login screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xxt_instance = None
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(12))

        # Header
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.12))
        title = Label(text='手机号登录', font_size=dp(20), bold=True,
                     color=get_color_from_hex(THEME['primary_dark']),
                     font_name='DroidSansFallback.ttf')
        header.add_widget(title)
        header.add_widget(Label(text='请输入学习通账号密码', font_size=dp(13),
                                color=get_color_from_hex(THEME['text_secondary'])))
        main_layout.add_widget(header)

        # Phone input
        main_layout.add_widget(Label(text='手机号', font_size=dp(14),
                                     color=get_color_from_hex(THEME['text_primary']),
                                     size_hint=(1, 0.04)))
        self.phone_input = TextInput(
            hint_text='请输入手机号',
            multiline=False,
            font_size=dp(15),
            size_hint=(1, 0.07),
            input_type='number',
            background_color=get_color_from_hex(THEME['card']),
        )
        main_layout.add_widget(self.phone_input)

        # Password input
        main_layout.add_widget(Label(text='密码', font_size=dp(14),
                                     color=get_color_from_hex(THEME['text_primary']),
                                     size_hint=(1, 0.04)))
        self.password_input = TextInput(
            hint_text='请输入密码',
            multiline=False,
            font_size=dp(15),
            size_hint=(1, 0.07),
            password=True,
            background_color=get_color_from_hex(THEME['card']),
        )
        main_layout.add_widget(self.password_input)

        # Spacer
        main_layout.add_widget(BoxLayout(size_hint=(1, 0.08)))

        # Login button
        login_btn = Button(
            text='登 录',
            font_size=dp(16),
            bold=True,
            background_color=get_color_from_hex(THEME['primary']),
            background_normal='',
            color=(1,1,1,1),
            size_hint=(1, 0.09),
        )
        login_btn.bind(on_release=self.do_login)
        main_layout.add_widget(login_btn)

        # Status label
        self.status_label = Label(
            text='',
            font_size=dp(12),
            color=get_color_from_hex(THEME['danger']),
            size_hint=(1, 0.05),
        )
        main_layout.add_widget(self.status_label)

        # Back button
        back_btn = Button(
            text='← 返回首页',
            font_size=dp(13),
            background_color=(0,0,0,0),
            color=get_color_from_hex(THEME['primary']),
            size_hint=(1, 0.06),
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'welcome'))
        main_layout.add_widget(back_btn)

        self.add_widget(main_layout)

    def do_login(self, instance):
        phone = self.phone_input.text.strip()
        password = self.password_input.text.strip()

        if not phone or not password:
            self.status_label.text = '请输入手机号和密码'
            return

        self.status_label.text = '正在登录...'
        self.status_label.color = get_color_from_hex(THEME['primary'])

        def login_thread():
            try:
                xxt = NewXxt()
                result = xxt.login(phone, password)
                if result.get('status'):
                    info = xxt.getInfo()
                    self.xxt_instance = xxt
                    Clock.schedule_once(lambda dt: self._login_success(info))
                else:
                    msg = result.get('msg2', result.get('msg', '登录失败'))
                    Clock.schedule_once(lambda dt: self._login_failed(msg))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._login_failed(str(e)))

        threading.Thread(target=login_thread, daemon=True).start()

    def _login_success(self, info):
        self.status_label.text = f"✅ 登录成功 - {info.get('name', '')}"
        self.status_label.color = get_color_from_hex(THEME['success'])
        # Store in app
        app = App.get_running_app()
        app.xxt_instance = self.xxt_instance
        app.user_info = info
        # Navigate to courses
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'courses'), 1)

    def _login_failed(self, msg):
        self.status_label.text = f'❌ {msg}'
        self.status_label.color = get_color_from_hex(THEME['danger'])


class QRLoginScreen(Screen):
    """QR Code login screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(12))

        title = Label(text='扫码登录', font_size=dp(20), bold=True,
                     color=get_color_from_hex(THEME['primary_dark']),
                     size_hint=(1, 0.08))
        main_layout.add_widget(title)

        info_label = Label(
            text='请在浏览器中打开以下链接\n使用学习通APP扫码',
            font_size=dp(13),
            color=get_color_from_hex(THEME['text_secondary']),
            size_hint=(1, 0.1),
            halign='center',
        )
        main_layout.add_widget(info_label)

        self.qr_url_label = Label(
            text='点击"获取二维码"按钮',
            font_size=dp(11),
            color=get_color_from_hex(THEME['primary']),
            size_hint=(1, 0.15),
            halign='center',
        )
        main_layout.add_widget(self.qr_url_label)

        get_qr_btn = Button(
            text='📷  获取二维码',
            font_size=dp(15),
            background_color=get_color_from_hex(THEME['accent']),
            background_normal='',
            color=(1,1,1,1),
            size_hint=(1, 0.08),
        )
        get_qr_btn.bind(on_release=self.get_qr_code)
        main_layout.add_widget(get_qr_btn)

        self.status_label = Label(
            text='',
            font_size=dp(14),
            color=get_color_from_hex(THEME['text_secondary']),
            size_hint=(1, 0.08),
            halign='center',
        )
        main_layout.add_widget(self.status_label)

        main_layout.add_widget(BoxLayout(size_hint=(1, 0.2)))

        back_btn = Button(
            text='← 返回首页',
            font_size=dp(13),
            background_color=(0,0,0,0),
            color=get_color_from_hex(THEME['primary']),
            size_hint=(1, 0.06),
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'welcome'))
        main_layout.add_widget(back_btn)

        self.add_widget(main_layout)

    def get_qr_code(self, instance):
        self.status_label.text = '正在获取二维码...'
        def qr_thread():
            try:
                self.xxt = NewXxt()
                self.xxt.qr_get()
                url = self.xxt.qr_geturl()
                self.qr_url_label.text = f'请复制以下链接到浏览器打开：\n\n{url}'
                self.status_label.text = '请用学习通APP扫描二维码...'
                # Start polling
                self.poll_qr_status()
            except Exception as e:
                self.status_label.text = f'获取二维码失败: {e}'

        threading.Thread(target=qr_thread, daemon=True).start()

    def poll_qr_status(self):
        def check():
            try:
                result = self.xxt.login_qr()
                if result.get('status'):
                    info = self.xxt.getInfo()
                    app = App.get_running_app()
                    app.xxt_instance = self.xxt
                    app.user_info = info
                    self.status_label.text = f'✅ 登录成功 - {info.get("name", "")}'
                    Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'courses'), 1)
                elif result.get('type') == '1':
                    self.status_label.text = '二维码验证错误，请重试'
                elif result.get('type') == '2':
                    self.status_label.text = '二维码已失效，请重新获取'
                elif result.get('type') == '4':
                    if '已扫描' not in self.status_label.text:
                        self.status_label.text = '✅ 已扫描，请在手机上确认...'
                    Clock.schedule_once(lambda dt: self.poll_qr_status(), 1.5)
                else:
                    Clock.schedule_once(lambda dt: self.poll_qr_status(), 1.5)
            except Exception as e:
                self.status_label.text = f'轮询失败: {e}'
                Clock.schedule_once(lambda dt: self.poll_qr_status(), 2)

        Clock.schedule_once(lambda dt: check(), 1)


class CourseListScreen(Screen):
    """Course list screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.courses = []
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))

        # Header
        header = BoxLayout(orientation='horizontal', size_hint=(1, 0.06))
        header.add_widget(Label(text='📚 我的课程', font_size=dp(18), bold=True,
                               color=get_color_from_hex(THEME['primary_dark']),
                               size_hint=(0.7, 1)))

        refresh_btn = Button(text='刷新', font_size=dp(12),
                            background_color=get_color_from_hex(THEME['primary']),
                            background_normal='', color=(1,1,1,1),
                            size_hint=(0.3, 1))
        refresh_btn.bind(on_release=lambda x: self.load_courses())
        header.add_widget(refresh_btn)
        main_layout.add_widget(header)

        # Course list (scrollable)
        self.course_list = BoxLayout(orientation='vertical', spacing=dp(5),
                                     size_hint=(1, None))
        self.course_list.bind(minimum_height=self.course_list.setter('height'))

        scroll = ScrollView(size_hint=(1, 0.82))
        scroll.add_widget(self.course_list)
        main_layout.add_widget(scroll)

        # Bottom nav
        nav = BoxLayout(orientation='horizontal', size_hint=(1, 0.06), spacing=dp(5))
        back_btn = Button(text='← 首页', font_size=dp(12),
                         background_color=get_color_from_hex(THEME['text_secondary']),
                         background_normal='', color=(1,1,1,1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'welcome'))
        export_btn = Button(text='导出工具 →', font_size=dp(12),
                           background_color=get_color_from_hex(THEME['success']),
                           background_normal='', color=(1,1,1,1))
        export_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'export'))
        nav.add_widget(back_btn)
        nav.add_widget(export_btn)
        main_layout.add_widget(nav)

        self.add_widget(main_layout)

    def on_enter(self):
        self.load_courses()

    def load_courses(self):
        self.course_list.clear_widgets()
        self.course_list.add_widget(Label(
            text='加载中...', font_size=dp(14),
            color=get_color_from_hex(THEME['text_secondary']),
            size_hint=(1, None), height=dp(40)
        ))

        def load_thread():
            app = App.get_running_app()
            if not app.xxt_instance:
                Clock.schedule_once(lambda dt: self._show_error('请先登录'))
                return
            try:
                courses = app.xxt_instance.getCourse()
                app.courses = courses
                Clock.schedule_once(lambda dt: self._show_courses(courses))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)))

        threading.Thread(target=load_thread, daemon=True).start()

    def _show_courses(self, courses):
        self.course_list.clear_widgets()
        if not courses:
            self.course_list.add_widget(Label(text='暂无课程', font_size=dp(14),
                                              color=get_color_from_hex(THEME['text_secondary']),
                                              size_hint=(1, None), height=dp(40)))
            return

        for course in courses:
            btn = Button(
                text=f"{course['course_name']}\n[size=12dp][color=#999]{course['course_teacher']}[/color][/size]",
                font_size=dp(14),
                size_hint=(1, None),
                height=dp(65),
                background_color=get_color_from_hex(THEME['card']),
                background_normal='',
                color=get_color_from_hex(THEME['text_primary']),
                halign='left',
                valign='middle',
                markup=True,
            )
            btn.course_data = course
            btn.bind(on_release=self.on_course_selected)
            self.course_list.add_widget(btn)

    def on_course_selected(self, instance):
        app = App.get_running_app()
        app.selected_course = instance.course_data
        self.manager.current = 'assignments'

    def _show_error(self, msg):
        self.course_list.clear_widgets()
        self.course_list.add_widget(Label(text=f'错误: {msg}', font_size=dp(13),
                                          color=get_color_from_hex(THEME['danger']),
                                          size_hint=(1, None), height=dp(40)))


class AssignmentListScreen(Screen):
    """Assignment list and export screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.works = []
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))

        # Header
        self.course_label = Label(text='作业列表', font_size=dp(17), bold=True,
                                 color=get_color_from_hex(THEME['primary_dark']),
                                 size_hint=(1, 0.05))
        main_layout.add_widget(self.course_label)

        # Assignment list
        self.work_list = BoxLayout(orientation='vertical', spacing=dp(5),
                                  size_hint=(1, None))
        self.work_list.bind(minimum_height=self.work_list.setter('height'))

        scroll = ScrollView(size_hint=(1, 0.82))
        scroll.add_widget(self.work_list)
        main_layout.add_widget(scroll)

        # Bottom buttons
        nav = BoxLayout(orientation='horizontal', size_hint=(1, 0.06), spacing=dp(5))
        back_btn = Button(text='← 课程', font_size=dp(12),
                         background_color=get_color_from_hex(THEME['text_secondary']),
                         background_normal='', color=(1,1,1,1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'courses'))

        fetch_btn = Button(text='爬取答案', font_size=dp(12),
                          background_color=get_color_from_hex(THEME['accent']),
                          background_normal='', color=(1,1,1,1))
        fetch_btn.bind(on_release=self.fetch_selected)

        export_btn = Button(text='📄 导出 Word', font_size=dp(12),
                           background_color=get_color_from_hex(THEME['success']),
                           background_normal='', color=(1,1,1,1))
        export_btn.bind(on_release=self.export_selected)

        nav.add_widget(back_btn)
        nav.add_widget(fetch_btn)
        nav.add_widget(export_btn)
        main_layout.add_widget(nav)

        self.add_widget(main_layout)

    def on_enter(self):
        app = App.get_running_app()
        course = app.selected_course
        if course:
            self.course_label.text = f"📋 {course['course_name']}"
            self.load_assignments()

    def load_assignments(self):
        self.work_list.clear_widgets()
        self.work_list.add_widget(Label(text='加载中...', font_size=dp(13),
                                       color=get_color_from_hex(THEME['text_secondary']),
                                       size_hint=(1, None), height=dp(35)))

        def load_thread():
            app = App.get_running_app()
            course = app.selected_course
            try:
                works = app.xxt_instance.getWorks(course['course_url'], course['course_name'])
                app.current_works = works
                Clock.schedule_once(lambda dt: self._show_works(works))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)))

        threading.Thread(target=load_thread, daemon=True).start()

    def _show_works(self, works):
        self.work_list.clear_widgets()
        if not works:
            self.work_list.add_widget(Label(text='该课程暂无作业', font_size=dp(13),
                                           color=get_color_from_hex(THEME['text_secondary']),
                                           size_hint=(1, None), height=dp(40)))
            return

        for work in works:
            status_color = '#4CAF50' if work['work_status'] == '已完成' else '#FF9800'
            btn = Button(
                text=f"{work['work_name']}\n[size=12dp][color={status_color}]{work['work_status']} | 得分: {work['score']}[/color][/size]",
                font_size=dp(13),
                size_hint=(1, None),
                height=dp(65),
                background_color=get_color_from_hex(THEME['card']),
                background_normal='',
                color=get_color_from_hex(THEME['text_primary']),
                halign='left',
                valign='middle',
                markup=True,
            )
            btn.work_data = work
            if work['work_status'] == '已完成':
                btn.bind(on_release=self.on_work_selected)
            self.work_list.add_widget(btn)

    def on_work_selected(self, instance):
        """Fetch answer for selected completed work"""
        work = instance.work_data
        app = App.get_running_app()

        def fetch():
            try:
                answers = app.xxt_instance.getAnswer(work['work_url'])
                # Save to file
                import json
                answer_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'answers')
                os.makedirs(answer_dir, exist_ok=True)
                data = {work['id']: answers, 'info': work}
                filepath = os.path.join(answer_dir, f"{work['id']}.json")
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)

                Clock.schedule_once(lambda dt: self._show_toast(f'✅ 答案已保存: {work["id"]}.json'))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_toast(f'❌ 失败: {e}'))

        self._show_toast('正在爬取答案...')
        threading.Thread(target=fetch, daemon=True).start()

    def fetch_selected(self, instance):
        """Fetch all completed assignments"""
        app = App.get_running_app()
        works = app.current_works
        completed = [w for w in works if w['work_status'] == '已完成']

        if not completed:
            self._show_toast('没有已完成的作业可爬取')
            return

        self._show_toast(f'正在爬取 {len(completed)} 个作业...')

        def fetch_all():
            import json
            answer_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'answers')
            os.makedirs(answer_dir, exist_ok=True)
            success = 0
            for work in completed:
                try:
                    answers = app.xxt_instance.getAnswer(work['work_url'])
                    data = {work['id']: answers, 'info': work}
                    filepath = os.path.join(answer_dir, f"{work['id']}.json")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False)
                    success += 1
                except:
                    pass
            Clock.schedule_once(lambda dt: self._show_toast(f'✅ 成功爬取 {success}/{len(completed)} 个作业'))

        threading.Thread(target=fetch_all, daemon=True).start()

    def export_selected(self, instance):
        """Navigate to export screen"""
        self.manager.current = 'export'

    def _show_error(self, msg):
        self.work_list.clear_widgets()
        self.work_list.add_widget(Label(text=f'错误: {msg}', font_size=dp(13),
                                       color=get_color_from_hex(THEME['danger']),
                                       size_hint=(1, None), height=dp(40)))

    def _show_toast(self, msg):
        try:
            Toast(message=msg).open()
        except:
            pass


class ExportScreen(Screen):
    """Export assignments to Word"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))

        # Header
        title = Label(text='📄 导出 Word 文档', font_size=dp(20), bold=True,
                     color=get_color_from_hex(THEME['primary_dark']),
                     size_hint=(1, 0.08))
        main_layout.add_widget(title)
        main_layout.add_widget(Label(text='将已爬取的作业答案导出为格式化Word文档',
                                     font_size=dp(13),
                                     color=get_color_from_hex(THEME['text_secondary']),
                                     size_hint=(1, 0.05)))

        # Available JSON files
        self.file_list = BoxLayout(orientation='vertical', spacing=dp(4),
                                  size_hint=(1, None))
        self.file_list.bind(minimum_height=self.file_list.setter('height'))

        scroll = ScrollView(size_hint=(1, 0.45))
        scroll.add_widget(self.file_list)
        main_layout.add_widget(scroll)

        # Export buttons
        btn_layout = BoxLayout(orientation='vertical', spacing=dp(10),
                               size_hint=(1, 0.3), padding=[dp(10), 0])

        export_single = Button(
            text='📝 导出全部答案（独立文件）',
            font_size=dp(14),
            background_color=get_color_from_hex(THEME['primary']),
            background_normal='', color=(1,1,1,1),
            size_hint=(1, 0.25),
        )
        export_single.bind(on_release=self.export_separate)
        btn_layout.add_widget(export_single)

        export_merge = Button(
            text='📚 合并导出（一个Word文件）',
            font_size=dp(14),
            background_color=get_color_from_hex(THEME['success']),
            background_normal='', color=(1,1,1,1),
            size_hint=(1, 0.25),
        )
        export_merge.bind(on_release=self.export_merged)
        btn_layout.add_widget(export_merge)

        self.status_label = Label(
            text='',
            font_size=dp(13),
            color=get_color_from_hex(THEME['text_secondary']),
            size_hint=(1, 0.2),
            halign='center',
        )
        btn_layout.add_widget(self.status_label)

        main_layout.add_widget(btn_layout)

        # Navigation
        nav = BoxLayout(orientation='horizontal', size_hint=(1, 0.06), spacing=dp(5))
        back_btn = Button(text='← 作业', font_size=dp(12),
                         background_color=get_color_from_hex(THEME['text_secondary']),
                         background_normal='', color=(1,1,1,1))
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'assignments'))
        home_btn = Button(text='🏠 首页', font_size=dp(12),
                         background_color=get_color_from_hex(THEME['primary']),
                         background_normal='', color=(1,1,1,1))
        home_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'welcome'))
        nav.add_widget(back_btn)
        nav.add_widget(home_btn)
        main_layout.add_widget(nav)

        self.add_widget(main_layout)

    def on_enter(self):
        self.load_files()

    def load_files(self):
        self.file_list.clear_widgets()
        answer_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'answers')
        os.makedirs(answer_dir, exist_ok=True)

        json_files = [f for f in os.listdir(answer_dir) if f.endswith('.json')]
        if not json_files:
            self.file_list.add_widget(Label(
                text='暂无答案文件\n请先在"作业"页面爬取答案',
                font_size=dp(13), halign='center',
                color=get_color_from_hex(THEME['text_secondary']),
                size_hint=(1, None), height=dp(60)))
            return

        for f in sorted(json_files):
            # Try to read info
            try:
                with open(os.path.join(answer_dir, f), 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                info = data.get('info', {})
                label_text = f"📋 {info.get('work_name', f)} | {info.get('course_name', '')}"
            except:
                label_text = f"📄 {f}"

            lbl = Label(
                text=label_text,
                font_size=dp(13),
                color=get_color_from_hex(THEME['text_primary']),
                size_hint=(1, None),
                height=dp(35),
                halign='left',
                valign='middle',
            )
            self.file_list.add_widget(lbl)

    def export_separate(self, instance):
        self.status_label.text = '正在导出...'
        def do_export():
            try:
                answer_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'answers')
                files = batch_export_to_docx(answer_dir, merge=False)
                Clock.schedule_once(lambda dt: self._export_done(files))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._export_failed(str(e)))

        threading.Thread(target=do_export, daemon=True).start()

    def export_merged(self, instance):
        self.status_label.text = '正在合并导出...'
        def do_export():
            try:
                answer_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'answers')
                files = batch_export_to_docx(answer_dir, merge=True)
                Clock.schedule_once(lambda dt: self._export_done(files))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._export_failed(str(e)))

        threading.Thread(target=do_export, daemon=True).start()

    def _export_done(self, files):
        self.status_label.text = f'✅ 导出成功！\n共 {len(files)} 个文件\n保存于 answers/ 目录'
        self.load_files()

    def _export_failed(self, msg):
        self.status_label.text = f'❌ 导出失败: {msg}'


# ── Main App ──

class XxtDocxApp(App):
    """学习通作业提取工具 - Android App"""
    title = '学习通作业提取'
    icon = 'img/cover.jpg'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xxt_instance = None
        self.user_info = None
        self.courses = []
        self.selected_course = None
        self.current_works = []

    def build(self):
        # Set window background
        Window.clearcolor = get_color_from_hex(THEME['bg'])

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(PhoneLoginScreen(name='phone_login'))
        sm.add_widget(QRLoginScreen(name='qr_login'))
        sm.add_widget(CourseListScreen(name='courses'))
        sm.add_widget(AssignmentListScreen(name='assignments'))
        sm.add_widget(ExportScreen(name='export'))
        return sm


if __name__ == '__main__':
    XxtDocxApp().run()
