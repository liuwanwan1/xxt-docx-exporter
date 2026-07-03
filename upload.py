import re
import subprocess

from config import __VERSION__

"""
    修改README.md文件中的版本号
"""


def update_version():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
        content = re.sub(r"v\d+\.\d+\.\d+", f"{__VERSION__}", content)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("1.修改README.md文件中的版本号成功！")


"""
    提交新修改的README.md文件并推送到github
"""


def git_push_readme():
    run_git("add", "README.md")
    run_git("commit", "-m", "update version")
    run_git("push", "origin", "red")
    print("2.提交新修改的README.md文件并推送到github成功！")


"""
    自动生成创建新git tag标签，并上穿到github
"""


def git_tag():
    run_git("tag", "-a", __VERSION__, "-m", __VERSION__)
    run_git("push", "origin", __VERSION__)
    print("3.自动生成创建新git tag标签，并上穿到github成功！")


def run_git(*args):
    subprocess.run(["git", *args], check=True)


def confirm_release():
    answer = input(f"确认提交 README 并推送 tag {__VERSION__}? 输入 yes 继续：")
    return answer == "yes"


if __name__ == '__main__':
    update_version()
    if confirm_release():
        git_push_readme()
        git_tag()
    else:
        print("已取消推送和打标签。")
