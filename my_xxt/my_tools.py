# -*- coding = utf-8 -*-
# @Time :2023/5/16 18:36
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  my_tools.py
import os
import time

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from my_xxt.findAnswer import match_answer
from my_xxt.api import NewXxt
from my_xxt.answer_files import (
    answer_file_exists,
    answer_json_files,
    default_answers_path,
    load_answer_file_infos,
    read_answer_json,
    write_answer_json,
)
from my_xxt.export_docx import generate_docx_from_json, batch_export_to_docx, export_course_assignments_to_docx

from config import __VERSION__


def select_error(console: Console):
    console.log("[green]发生了一些未知的错误！")
    flag = console.input("[green]请选择是否重新选择！(按q退出,按任意键继续)")
    if flag == 'q':
        exit(0)


def select_course(console: Console, courses: list) -> dict:
    while True:
        index = console.input("[yellow]请输入你要打开的课程的序号：")
        for item in courses:
            if item["id"] == index:
                return item
        select_error(console)


def select_work(console: Console, works: list) -> dict:
    if not len(works):
        return {}
    while True:
        index = console.input("[yellow]请输入作业答案的id：")
        for item in works:
            if item["work_id"] == index:
                return item
        select_error(console)


def select_works(console: Console, works: list) -> list:
    works_list = []
    if not len(works):
        return []
    while True:
        index = console.input("[yellow]请输入作业答案的id(如果是爬取多个作业，序号按照（1，2，3）英文逗号)：")
        index = index.replace(" ", "")
        index_list = index.split(",")

        for item in works:
            for choose in index_list:
                if item["work_id"] == choose:
                    works_list.append(item)
        if len(works_list):
            return works_list
        select_error(console)


def selected_course_works(console: Console, xxt: NewXxt) -> tuple[dict, list]:
    courses = xxt.getCourse()
    show_course(courses, console)
    course = select_course(console, courses)
    works = xxt.getWorks(course["course_url"], course["course_name"])
    show_works(works, console)
    return course, works


def answer_json_path(work: dict) -> str:
    return os.path.join(default_answers_path(), f"{work['id']}.json")


def handle_show_courses(console: Console, xxt: NewXxt) -> None:
    show_course(xxt.getCourse(), console)


def handle_show_answer_files(console: Console, xxt: NewXxt) -> None:
    show_all_answer_file(console)


def handle_show_not_work(console: Console, xxt: NewXxt) -> None:
    courses = xxt.getCourse()
    not_work = get_not_work(courses, xxt, console, sleep_time=2)
    show_not_work(not_work, console)


def handle_clear_answers(console: Console, xxt: NewXxt) -> None:
    path = default_answers_path()
    if os.path.isdir(path):
        del_file(path)
    console.log("[green]清空完毕")


def handle_fetch_answer(console: Console, xxt: NewXxt) -> None:
    _, works = selected_course_works(console, xxt)
    work = select_work(console, works)
    if work == {}:
        console.print("[red]该课程下没有作业")
        return
    if work["work_status"] != "已完成":
        console.print("[red]该作业似乎没有完成")
        return

    answer_list = xxt.getAnswer(work["work_url"])
    dateToJsonFile(answer_list, work)
    console.log(f"[green]爬取成功，答案已经保存至{work['id']}.json")


def handle_fetch_course_answers(console: Console, xxt: NewXxt) -> None:
    _, works = selected_course_works(console, xxt)
    works = select_works(console, works)
    if works == []:
        console.log("[red]该课程下没有作业")
        return

    for index, work in enumerate(works, 1):
        with console.status(f"[red]正在查找《{work['work_name']}》...[{index}/{len(works)}]"):
            try:
                if work["work_status"] != "已完成":
                    console.log("[red]该作业似乎没有完成")
                    continue
                dateToJsonFile(xxt.getAnswer(work["work_url"]), work)
            except Exception as e:
                console.log("[red]出现了一点小意外", e)
    console.log("[green]爬取成功")


def prepare_work_submission(console: Console, xxt: NewXxt, work: dict):
    if work["work_status"] == "已完成" and work["isRedo"] == "no":
        console.log("[red]该作业已经完成了")
        return None

    if work["isRedo"] == "yes":
        choose = console.input("[yellow]该作业可以重做，请确认是否要重做：（yes/no）")
        if choose == "no":
            return None
        result = xxt.redoWork(work["work_url"])
        if result["status"] == 1:
            console.log("[green]作业重做成功")
        else:
            console.log(f"[red]作业重做失败,错误原因[red]{result['msg']}[/red]")

    questions = xxt.get_question(work["work_url"])
    if not is_exist_answer_file(f"{work['id']}.json"):
        console.log("[green]没有在答案文件中匹配到对应的答案文件")
        return None
    answer = match_answer(jsonFileToDate(answer_json_path(work))[work["id"]], questions, xxt.randomOptions)
    return answer


def handle_commit_work(console: Console, xxt: NewXxt) -> None:
    course, works = selected_course_works(console, xxt)
    work = select_work(console, works)
    if work == {}:
        console.log("[red]该课程下没有作业")
        return

    answer = prepare_work_submission(console, xxt, work)
    if answer is None:
        return
    show_answer(answer_list=answer, console=console)

    choose = console.input("[yellow]是否继续进行提交：（yes/no）")
    if choose != "yes":
        return
    console.log(xxt.commit_work(answer, work))
    show_works(xxt.getWorks(course["course_url"], course["course_name"]), console)


def handle_batch_commit_work(console: Console, xxt: NewXxt) -> None:
    _, works = selected_course_works(console, xxt)
    selected_work = select_work(console, works)
    users = jsonFileToDate(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "user.json"))
    show_users(users, console)

    users_select = select_users(users, console)
    success_count = 0
    fail_count = 0
    for index, user in enumerate(users_select, 1):
        user_xxt = NewXxt()
        login_status = user_xxt.login(user["phone"], user["password"])
        if login_status["status"] != True:
            console.log(f"({index})  [green]{user['name']}---该用户的作业操作失败:[red]账号或者密码错误[/red][/green]")
            fail_count += 1
            continue

        courses = user_xxt.getCourse()
        user_course = find_course(courses, selected_work["courseId"])
        if user_course == {}:
            console.log(f"({index})  [green]{user['name']}---该用户的作业操作失败[red]该账号不存在该课程或者作业")
            fail_count += 1
            continue

        user_works = user_xxt.getWorks(user_course["course_url"], user_course["course_name"])
        user_work = find_work(user_works, selected_work["work_id"])
        if user_work == {}:
            console.log(f"({index})  [green]{user['name']}---该用户的作业操作失败[red]该账号不存在该课程或者作业")
            fail_count += 1
            continue
        if user_work["work_status"] == "已完成":
            console.log(f"({index})  [green]{user['name']}---该用户的作业操作失败[red]该账号已完成该作业")
            fail_count += 1
            continue
        if not is_exist_answer_file(f"{user_work['id']}.json"):
            console.log(f"({index})  [green]{user['name']}---该用户的作业操作失败[red]没有在答案文件中匹配到对应的答案文件")
            fail_count += 1
            continue

        questions = user_xxt.get_question(user_work["work_url"])
        answer = match_answer(jsonFileToDate(answer_json_path(user_work))[user_work["id"]], questions, user_xxt.randomOptions)
        ret = user_xxt.commit_work(answer, user_work)
        if ret["msg"] == "success!":
            user_works = user_xxt.getWorks(user_course["course_url"], user_course["course_name"])
            user_work = find_work(user_works, user_work["work_id"])
            console.log(f"({index})  [green]{user['name']}---该用户的作业操作成功[blue]最终分数为{user_work['score']}")
            success_count += 1
        else:
            console.log(f"({index})  [green]{user['name']}---该用户的作业操作失败 {ret},你可以再次尝试一次。")
            fail_count += 1
    console.log(f"[yellow]一共成功{success_count},失败数为{fail_count}[/yellow]")


def handle_export_single_docx(console: Console, xxt: NewXxt) -> None:
    answers_path = default_answers_path()
    show_all_answer_file(console)

    answer_files = answer_json_files(answers_path)
    if not answer_files:
        console.log("[red]暂无答案文件，请先爬取作业答案")
        return

    file_id = console.input("[yellow]请输入要导出的答案文件ID（输入文件名前缀，如27835863）：")
    matched_files = [file for file in answer_files if file_id in file]
    if not matched_files:
        console.log(f"[red]未找到匹配的答案文件: {file_id}")
        return

    for file_name in matched_files:
        json_path = os.path.join(answers_path, file_name)
        with console.status(f"[green]正在导出 {file_name} 为Word文档..."):
            try:
                output_path = generate_docx_from_json(json_path)
                console.log(f"[green]✅ 导出成功: {output_path}")
            except Exception as e:
                console.log(f"[red]❌ 导出失败 {file_name}: {e}")


def handle_export_batch_docx(console: Console, xxt: NewXxt) -> None:
    answers_path = default_answers_path()
    answer_files = answer_json_files(answers_path)
    if not answer_files:
        console.log("[red]暂无答案文件，请先爬取作业答案")
        return

    console.log(f"[yellow]找到 {len(answer_files)} 个答案文件")
    export_mode = console.input("[yellow]请选择导出模式：（1=每个作业单独导出，2=合并为一个文档）")
    merge = export_mode == "2"

    with console.status("[green]正在批量导出为Word文档..."):
        try:
            output_files = batch_export_to_docx(answers_path, merge=merge)
            console.log(f"[green]✅ 批量导出完成，共生成 {len(output_files)} 个文件：")
            for file in output_files:
                console.log(f"[green]   - {file}")
        except Exception as e:
            console.log(f"[red]❌ 批量导出失败: {e}")


def handle_export_course_docx(console: Console, xxt: NewXxt) -> None:
    answers_path = default_answers_path()
    if not answer_json_files(answers_path):
        console.log("[red]暂无答案文件，请先爬取作业答案")
        return

    show_all_answer_file(console)
    course_name = console.input("[yellow]请输入课程名称（或关键词）：")
    with console.status(f"[green]正在查找课程'{course_name}'的作业并导出..."):
        try:
            output_path = export_course_assignments_to_docx(course_name, answers_path)
            console.log(f"[green]✅ 导出成功: {output_path}")
        except ValueError as e:
            console.log(f"[red]❌ 导出失败: {e}")
        except Exception as e:
            console.log(f"[red]❌ 导出失败: {e}")


MENU_HANDLERS = {
    "1": handle_show_courses,
    "2": handle_show_answer_files,
    "3": handle_show_not_work,
    "4": handle_clear_answers,
    "5": handle_fetch_answer,
    "6": handle_fetch_course_answers,
    "7": handle_commit_work,
    "8": handle_batch_commit_work,
    "10": handle_export_single_docx,
    "11": handle_export_batch_docx,
    "12": handle_export_course_docx,
}


def select_menu(console: Console, xxt: NewXxt) -> None:
    while True:
        show_menu(console)
        index = console.input("[yellow]请输入你想选择的功能：")
        if index == "9":
            return
        handler = MENU_HANDLERS.get(index)
        if handler is None:
            select_error(console)
            continue
        handler(console, xxt)


def find_course(courses: list, course_id: str) -> dict:
    for course in courses:
        # url 里面有course_id
        if course_id in course["course_url"]:
            return course
    return {}


def find_work(works: list, work_id: str) -> dict:
    for work in works:
        if work["work_id"] == work_id:
            return work
    return {}


def show_start(console: Console) -> None:

    console.print(Panel(
        title="[white]欢迎使用该做题脚本",
        renderable=
        Group(
            Text("    ███╗   ██╗███████╗██╗    ██╗        ██╗  ██╗██╗  ██╗████████╗\n \
   ████╗  ██║██╔════╝██║    ██║        ╚██╗██╔╝╚██╗██╔╝╚══██╔══╝\n \
 ██╔██╗ ██║█████╗  ██║ █╗ ██║         ╚███╔╝  ╚███╔╝    ██║\n\
  ██║╚██╗██║██╔══╝  ██║███╗██║         ██╔██╗  ██╔██╗    ██║\n\
  ██║ ╚████║███████╗╚███╔███╔╝███████╗██╔╝ ██╗██╔╝ ██╗   ██║\n\
  ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝  ", justify="center",style="bold white"),
            Text("注意：该脚本仅供学习参考,详细信息请参考https://github.com/aglorice/new_xxt", justify="center", style="bold red"),
            Text(f"当前版本为 {__VERSION__}", justify="center", style="bold red"),
        ),
        style="bold green",
        width=120,
    ))


def show_users(users: dict, console: Console) -> None:
    tb = Table("序号", "账号", "密码", "姓名", border_style="blue", width=116)
    i = 0

    for user in users["users"]:
        tb.add_row(
            f"[green]{i + 1}[/green]",
            user["phone"],
            user["password"],
            user["name"],
        )
        i = i + 1

    console.print(
        Panel(
            title="[blue]用户表[/blue]",
            renderable=tb,
            style="bold green",
        )
    )


def show_course(courses: list, console: Console) -> None:
    tb = Table("序号", "课程名", "老师名", border_style="blue", width=116)
    for course in courses:
        tb.add_row(
            f"[green]{course['id']}[/green]",
            course["course_name"],
            course["course_teacher"],
            style="bold yellow"
        )
    console.print(
        Panel(
            title="[blue]课程信息[/blue]",
            renderable=tb,
            style="bold green",
        )
    )


def select_users(users: dict, console: Console) -> list:
    user_list = []
    users_id = console.input("请选择你要完成此作业的账号 如(1,2,3) 英文逗号 全选请输入 all :")
    if users_id == "all":
        return users["users"]
    users_id = users_id.replace(" ", "")
    users_id_list = users_id.split(",")
    try:
        for user in users_id_list:
            user_list.append(users["users"][int(user) - 1])
        return user_list
    except Exception as e:
        select_error(console)


def show_menu(console: Console) -> None:
    console.print(Panel(
        title="[green]菜单",
        renderable=
        Group(
            Text("1.查看课程", justify="center", style="bold yellow"),
            Text("2.查看当前所有答案文件", justify="center", style="bold yellow"),
            Text("3.查询所有未完成的作业", justify="center", style="bold yellow"),
            Text("4.清除所有答案文件", justify="center", style="bold yellow"),
            Text("5.爬取指定作业的答案", justify="center", style="bold yellow"),
            Text("6.批量爬取指定课程的答案", justify="center", style="bold yellow"),
            Text("7.完成作业（请先确认是否已经爬取了你想要完成作业的答案）", justify="center", style="bold yellow"),
            Text("8.批量完成作业完成作业（请先确认是否已经爬取了你想要完成作业的答案，请填好user.json里的账号数据）",
                 justify="center", style="bold yellow"),
            Text("9.退出登录", justify="center", style="bold yellow"),
            Text("10.导出指定作业答案为Word文档(docx)", justify="center", style="bold cyan"),
            Text("11.批量导出所有答案为Word文档(docx)", justify="center", style="bold cyan"),
            Text("12.导出指定课程的所有作业为一个Word文档", justify="center", style="bold cyan"),
        ),
        style="bold green",
        width=120,
    ))


def show_works(works: list, console: Console) -> None:
    tb = Table("id", "作业名称", "作业状态", "分数", "是否可以重做", border_style="blue", width=116)
    for work in works:
        tb.add_row(
            f"[green]{work['work_id']}[/green]",
            work['work_name'],
            work["work_status"],
            work["score"],
            work["isRedo"],
            style="bold yellow"
        )
    console.print(
        Panel(
            title="[blue]作业信息",
            renderable=tb,
            style="bold green",
        )
    )


def show_answer(console: Console, answer_list: list) -> None:
    tb = Table("id", "题目名称", "答案", border_style="blue", width=116)
    for answer in answer_list:
        tb.add_row(
            f"[green]{answer['id']}[/green]",
            answer['title'],
            str(answer["answer"]),
            style="bold yellow"
        )
    console.print(
        Panel(
            title="[blue]检查答案",
            renderable=tb,
            style="bold green",
        )
    )


def dateToJsonFile(answer: list, info: dict) -> None:
    """
    将答案写入文件保存为json格式
    :param answer:
    :param info:
    :return:
    """
    write_answer_json(answer, info)


def jsonFileToDate(file: str) -> dict:
    return read_answer_json(file)


def show_all_answer_file(console: Console) -> None:
    answer_file_info = load_answer_file_infos()

    tb = Table("id", "作业名", "文件名称", "课程名称", border_style="blue", width=116)
    for work_info in answer_file_info:
        tb.add_row(
            f"[green]{work_info['id']}[/green]",
            work_info["work_name"],
            work_info["file_name"],
            work_info["course_name"],
            style="bold yellow"
        )
    console.print(
        Panel(
            title="[blue]作业文件列表[/blue]",
            renderable=tb,
            style="bold green",
        )
    )


def is_exist_answer_file(work_file_name: str, answers_path: str | None = None) -> bool:
    return answer_file_exists(work_file_name, answers_path)


def del_file(path_data: str):
    for i in os.listdir(path_data):  # os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
        file_data = path_data + "\\" + i  # 当前文件夹的下面的所有东西的绝对路径
        if os.path.isfile(file_data) == True:  # os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
            os.remove(file_data)
        else:
            del_file(file_data)


def get_not_work(courses: list, xxt: NewXxt, console: Console, sleep_time: float = 1) -> list:
    not_work = []
    for course in courses:
        with console.status(f"[red]正在查找《{course['course_name']}》...[{course['id']}/{len(courses)}][/red]"):
            time.sleep(sleep_time)
            try:
                works = xxt.getWorks(course["course_url"], course["course_name"])
                for work in works:
                    if work["work_status"] == "未交":
                        not_work.append({
                            "id": work["id"],
                            "work_name": work["work_name"],
                            "work_status": work["work_status"],
                            "course_name": work["course_name"]
                        })
            except Exception as e:
                console.log(f"[red]在查找课程[green]《{course['course_name']}》[/green]出现了一点小意外[/red]")
    return not_work


def show_not_work(not_work: list, console: Console) -> None:
    tb = Table("id", "作业名", "课程名称", "作业状态", border_style="blue", width=116)
    for work in not_work:
        tb.add_row(
            f"[green]{work['id']}[/green]",
            work["work_name"],
            work["course_name"],
            f"[green]{work['work_status']}",
            style="bold yellow"
        )

    console.print(
        Panel(
            title="[blue]作业文件列表[/blue]",
            renderable=tb,
            style="bold green",
        )
    )
