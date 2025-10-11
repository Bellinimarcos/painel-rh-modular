# logic/__init__.py
from .absenteeism_processor import AbsenteeismProcessor
from .burnout_processor import BurnoutProcessor
from .copsoq_processor import COPSOQProcessor
from .workaholism_processor import WorkaholismProcessor
from .turnover_processor import TurnoverProcessor

__all__ = ['AbsenteeismProcessor', 'BurnoutProcessor', 'COPSOQProcessor', 'WorkaholismProcessor']
