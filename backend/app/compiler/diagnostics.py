from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any

class DiagnosticSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class StageStatus(str, Enum):
    WAITING = "waiting"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class SourceLocation:
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line or self.line,
            "end_column": self.end_column or self.column,
        }

@dataclass
class Diagnostic:
    stage: str
    message: str
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR
    code: Optional[str] = None
    location: Optional[SourceLocation] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage,
            "message": self.message,
            "severity": self.severity.value,
            "code": self.code,
            "location": self.location.to_dict() if self.location else None,
        }

class CompilerError(Exception):
    def __init__(self, message: str, stage: str = "frontend", code: Optional[str] = None, location: Optional[SourceLocation] = None):
        super().__init__(message)
        self.stage = stage
        self.message = message
        self.code = code
        self.location = location

    def to_diagnostic(self) -> Diagnostic:
        return Diagnostic(
            stage=self.stage,
            message=self.message,
            severity=DiagnosticSeverity.ERROR,
            code=self.code,
            location=self.location,
        )

@dataclass
class StageMetric:
    name: str
    status: StageStatus
    duration_ms: float
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "duration_ms": round(self.duration_ms, 3),
            "details": self.details,
        }
