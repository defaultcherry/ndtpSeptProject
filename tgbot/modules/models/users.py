from datetime import datetime
from typing import Optional

from modules.db import Base
from modules.enums import TaskVerdict

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

__all__ = ["TgBotUser", "Task", "Contest", "SolvedTask", "SolvedContest", "ContestTask"]


class TgBotUser(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(nullable=False, unique=True, index=True)

    is_owner: Mapped[bool] = mapped_column(default=False)
    can_solve_tasks: Mapped[bool] = mapped_column(default=True)
    can_participate_in_contests: Mapped[bool] = mapped_column(default=True)
    can_create_tasks: Mapped[bool] = mapped_column(default=False)
    can_create_contests: Mapped[bool] = mapped_column(default=False)
    can_manage_permissions: Mapped[bool] = mapped_column(default=False)

    new_contest_notifications_enabled: Mapped[bool] = mapped_column(default=True)
    new_task_notifications_enabled: Mapped[bool] = mapped_column(default=False)
    contest_results_notifications_enabled: Mapped[bool] = mapped_column(default=True)

    created_tasks: Mapped[list["Task"]] = relationship(
        back_populates="author", lazy="selectin"
    )
    created_contests: Mapped[list["Contest"]] = relationship(
        back_populates="author", lazy="selectin"
    )
    solved_tasks: Mapped[list["SolvedTask"]] = relationship(
        back_populates="solver", lazy="selectin"
    )
    solved_contests: Mapped[list["SolvedContest"]] = relationship(
        back_populates="solver", lazy="selectin"
    )


class Task(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    notes: Mapped[Optional[str]]
    visible: Mapped[bool] = mapped_column(
        default=True
    )  # used when contest task created
    author_id: Mapped[int] = mapped_column(ForeignKey("tgbotusers.id"))

    author: Mapped["TgBotUser"] = relationship(
        back_populates="created_tasks", lazy="selectin"
    )
    solved_by: Mapped[list["SolvedTask"]] = relationship(
        back_populates="task", lazy="selectin"
    )
    used_in_contests: Mapped[list['ContestTask']] = relationship(
        back_populates="task", lazy="selectin"
    )


class SolvedTask(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    solver_id: Mapped[int] = mapped_column(ForeignKey("tgbotusers.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    solved_at: Mapped[datetime] = mapped_column(server_default=func.now())
    verdict: Mapped[TaskVerdict] = mapped_column(default=TaskVerdict.PENDING)
    solve_time: Mapped[Optional[float]]
    megabyte_usage: Mapped[Optional[float]]
    failed_test: Mapped[Optional[int]]
    code_format_errors: Mapped[Optional[int]]

    solver: Mapped["TgBotUser"] = relationship(
        back_populates="solved_tasks", lazy="selectin"
    )
    task: Mapped["Task"] = relationship(back_populates="solved_by", lazy="selectin")


class Contest(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("tgbotusers.id"))
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]

    tasks: Mapped["ContestTask"] = relationship(
        back_populates="contest", lazy="selectin"
    )
    author: Mapped["TgBotUser"] = relationship(
        back_populates="created_contests", lazy="selectin"
    )
    solved_by: Mapped[list["SolvedContest"]] = relationship(
        back_populates="contest", lazy="selectin"
    )


class ContestTask(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id"))
    task_reward: Mapped[int]

    task: Mapped["Task"] = relationship(lazy="selectin", back_populates="used_in_contests")
    contest: Mapped["Contest"] = relationship(back_populates="tasks", lazy="selectin")


class SolvedContest(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    solver_id: Mapped[int] = mapped_column(ForeignKey("tgbotusers.id"))
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id"))

    solver: Mapped["TgBotUser"] = relationship(
        back_populates="solved_contests", lazy="selectin"
    )
    contest: Mapped["Contest"] = relationship(
        back_populates="solved_by", lazy="selectin"
    )
