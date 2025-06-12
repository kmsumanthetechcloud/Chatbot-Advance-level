from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

    @run_on_ui_thread
    def open_browser(url):
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        PythonActivity.mActivity.startActivity(intent)

class ChatbotApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Open Chatbot'))
        btn = Button(text='Launch Chatbot')
        # update btn.bind(on_press=lambda instance: open_browser('http://127.0.0.1:8000/'))
        btn.bind(on_press=lambda instance: open_browser('http://<your-ec2-public-ip>:8000/'))

        layout.add_widget(btn)
        return layout

if __name__ == '__main__':
    ChatbotApp().run()
