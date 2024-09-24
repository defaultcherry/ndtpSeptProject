import contextlib
import os
import subprocess
import time
import psutil
import logging
import asyncio

from asyncio import subprocess
from contextlib import suppress

from sqlalchemy import select

from modules import db, models, enums
from modules.enums import TaskVerdict

TL_MAX = 5
ML_MAX = 256
CODE_CHECK_CMD = "ruff check {} --config \"lint.select = ['E', 'F', 'UP', 'B', 'SIM', 'I']\" --ignore-noqa --isolated --statistics"

async def is_running(proc: subprocess.Process):
    with contextlib.suppress(asyncio.TimeoutError):
        await asyncio.wait_for(proc.wait(), 1e-6)
    return proc.returncode is None

async def test_solution(task_id: int, user_id: int, solution: str):
    with db.Session() as session:
        user = session.scalars(select(models.TgBotUser).filter_by(telegram_id=user_id)).first()
        if user is None:
            return False
        task = models.SolvedTask(
            task_id=task_id,
            solver_id=user.id
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        solution_id = task.id
        formatted_time = task.solved_at.strftime("%d%m%YT%H.%M.%S.%f")
        test_path = f"storage/solution_{task_id}_{user.id}_{formatted_time}.py"
        logging.info("Prepared for compiling")
        with open(test_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(solution)

        logging.info("Wrote user's solution. Compiling...")
        result = await asyncio.create_subprocess_shell(
            "python -c "
            f"\"import py_compile; py_compile.compile('{test_path}', doraise=True)\"",
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        compile_code = await result.wait()
        logging.info("Compiled! Checking result...")
        if compile_code != 0:
            logging.info("Error! Compilation error!")
            task.verdict = TaskVerdict.CE
            session.commit()
            return solution_id

        ruff_check_result = await asyncio.create_subprocess_shell(
            CODE_CHECK_CMD.format(test_path),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        ruff_stdout, _ = await ruff_check_result.communicate()
        if ruff_check_result.returncode == 2:
            task.verdict = TaskVerdict.SERVER_ERROR
            session.commit()
            return solution_id
        if ruff_check_result.returncode == 1:
            errors = ruff_stdout.decode().strip().split("\n")
            total_errors = 0
            for error in errors:
                to_end = error.find("\t")
                to_int = error[:to_end]
                logging.info(to_end)
                logging.info(to_int)
                total_errors += int(to_int)
            task.code_format_errors = total_errors

        input_tests = os.listdir(f"storage/tests/task_{task_id}_in")
        output_tests = os.listdir(f"storage/tests/task_{task_id}_out")
        for i in range(1, len(input_tests) + 1):
            logging.info(f"Test N{i}...")
            # Ввод данных для Python файла
            f = open(f"storage/tests/task_{task_id}_in/{input_tests[i - 1]}", "r", encoding="utf-8")
            input_data = f.read().strip()
            f.close()
            logging.info("Got test input")
            logging.info(f"Test input: {input_data}")

            # Запуск Python файла и передача ему ввода
            logging.info("Starting process...")
            p = await asyncio.create_subprocess_shell(
                f"python -OO {test_path}",
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            logging.info("Process started!")
            # ps_process = psutil.Process(p.pid)
            start_time = time.time()
            logging.info("Counting down...")

            kill_process = False
            # finished_work = False
            max_memory_usage = 0

            # while not finished_work and not kill_process:
            #     now = time.time()
            #     runtime = now - start_time
            #     if not (await is_running(p)):
            #         logging.info("Process stopped!")
            #         finished_work = True
            #
            #     with suppress(Exception):
            #         max_memory_usage = max(max_memory_usage, ps_process.memory_info().vms)
            #
            #     if (runtime > TL_MAX and not finished_work) or max_memory_usage / 1024 / 1024 > ML_MAX:
            #         logging.info("TLE or MLE!")
            #         kill_process = True

            stdout, _ = await p.communicate(input_data.encode())
            result = stdout.decode().strip()

            total_time = time.time() - start_time
            task.solve_time = max(task.solve_time or 0, total_time)
            task.megabyte_usage = max(task.megabyte_usage or 0, max_memory_usage / 1024 / 1024)

            if kill_process or total_time > TL_MAX:
                logging.info(f"Killing task: {os.system(f'taskkill /PID {p.pid} /F')}")
                task.verdict = TaskVerdict.TLE if total_time > TL_MAX else TaskVerdict.MLE
                task.failed_test = i
                session.commit()
                return solution_id

            if p.returncode != 0:
                task.verdict = enums.TaskVerdict.RE
                task.failed_test = i
                session.commit()
                return solution_id

            f = open(f"storage/tests/task_{task_id}_out/{output_tests[i - 1]}", "r", encoding="utf-8")
            expected_output = f.read()
            f.close()
            if result != expected_output:
                task.verdict = enums.TaskVerdict.WA
                task.failed_test = i
                session.commit()
                logging.info(f"WA! {result} got instead of {expected_output}")
                return solution_id

        task.verdict = TaskVerdict.ACCEPTED
        session.commit()
        return solution_id
