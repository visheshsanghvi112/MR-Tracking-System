"""
Production-Grade Utilities for MR Bot
- Sentry error tracking
- Structured logging (JSON)
- Circuit breaker for external services
- Request tracing with correlation IDs
- Graceful shutdown handling
"""
import os
import sys
import json
import uuid
import signal
import asyncio
import logging
import functools
from datetime import datetime, timedelta
from typing import Optional, Callable, Any, Dict
from contextlib import contextmanager
from threading import Lock

# Load environment
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# STRUCTURED LOGGING (JSON format for log aggregation)
# ============================================================

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging - works with Datadog, Splunk, etc."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields (correlation_id, user_id, etc.)
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        if hasattr(record, "mr_id"):
            log_data["mr_id"] = record.mr_id
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
            
        return json.dumps(log_data)


def setup_production_logging(json_format: bool = True, level: str = "INFO"):
    """Configure production-grade logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if json_format and os.getenv("ENVIRONMENT", "development") == "production":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        ))
    
    root_logger.addHandler(console_handler)
    
    # Reduce noise from libraries
    for lib in ['httpx', 'telegram', 'urllib3', 'googleapiclient', 'google']:
        logging.getLogger(lib).setLevel(logging.WARNING)
    
    return root_logger


# ============================================================
# SENTRY ERROR TRACKING
# ============================================================

_sentry_initialized = False

def init_sentry():
    """Initialize Sentry for error tracking"""
    global _sentry_initialized
    
    if _sentry_initialized:
        return True
        
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        logging.getLogger(__name__).warning("SENTRY_DSN not set - error tracking disabled")
        return False
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("ENVIRONMENT", "development"),
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # 10% of sampled transactions for profiling
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                LoggingIntegration(level=logging.ERROR, event_level=logging.ERROR),
            ],
            # Don't send PII
            send_default_pii=False,
            # Attach request data
            request_bodies="small",
        )
        
        _sentry_initialized = True
        logging.getLogger(__name__).info("Sentry error tracking initialized")
        return True
        
    except ImportError:
        logging.getLogger(__name__).warning("sentry-sdk not installed - run: pip install sentry-sdk[fastapi]")
        return False
    except Exception as e:
        logging.getLogger(__name__).error(f"Sentry init failed: {e}")
        return False


def capture_exception(error: Exception, context: Optional[Dict] = None):
    """Capture exception to Sentry with optional context"""
    try:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)
    except ImportError:
        pass  # Sentry not installed


# ============================================================
# REQUEST TRACING (Correlation IDs)
# ============================================================

class RequestContext:
    """Thread-local storage for request context"""
    _context: Dict[str, Any] = {}
    _lock = Lock()
    
    @classmethod
    def set(cls, key: str, value: Any):
        with cls._lock:
            cls._context[key] = value
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        with cls._lock:
            return cls._context.get(key, default)
    
    @classmethod
    def clear(cls):
        with cls._lock:
            cls._context.clear()
    
    @classmethod
    def get_correlation_id(cls) -> str:
        cid = cls.get("correlation_id")
        if not cid:
            cid = str(uuid.uuid4())[:8]
            cls.set("correlation_id", cid)
        return cid


def with_correlation_id(func: Callable) -> Callable:
    """Decorator to add correlation ID to function calls"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        RequestContext.set("correlation_id", str(uuid.uuid4())[:8])
        try:
            return await func(*args, **kwargs)
        finally:
            RequestContext.clear()
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        RequestContext.set("correlation_id", str(uuid.uuid4())[:8])
        try:
            return func(*args, **kwargs)
        finally:
            RequestContext.clear()
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


# ============================================================
# CIRCUIT BREAKER (Prevent cascading failures)
# ============================================================

class CircuitBreaker:
    """
    Circuit breaker pattern for external service calls.
    
    States:
    - CLOSED: Normal operation, calls go through
    - OPEN: Service is down, fail fast without calling
    - HALF_OPEN: Testing if service recovered
    
    Usage:
        breaker = CircuitBreaker("gemini", failure_threshold=5, recovery_timeout=60)
        
        @breaker
        async def call_gemini(prompt):
            return await gemini.generate(prompt)
    """
    
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
    
    # Registry of all circuit breakers
    _breakers: Dict[str, "CircuitBreaker"] = {}
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout)
        self.half_open_max_calls = half_open_max_calls
        
        self.state = self.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self._lock = Lock()
        
        # Register breaker
        CircuitBreaker._breakers[name] = self
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator usage"""
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self.call_async(func, *args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return self.call_sync(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    def _should_allow_request(self) -> bool:
        """Check if request should be allowed"""
        with self._lock:
            if self.state == self.CLOSED:
                return True
            
            if self.state == self.OPEN:
                # Check if recovery timeout has passed
                if self.last_failure_time and \
                   datetime.now() - self.last_failure_time > self.recovery_timeout:
                    self.state = self.HALF_OPEN
                    self.half_open_calls = 0
                    return True
                return False
            
            if self.state == self.HALF_OPEN:
                if self.half_open_calls < self.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False
        
        return False
    
    def _record_success(self):
        """Record successful call"""
        with self._lock:
            self.success_count += 1
            if self.state == self.HALF_OPEN:
                if self.success_count >= self.half_open_max_calls:
                    self.state = self.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    logging.getLogger(__name__).info(
                        f"Circuit breaker '{self.name}' CLOSED (service recovered)"
                    )
    
    def _record_failure(self):
        """Record failed call"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == self.HALF_OPEN:
                self.state = self.OPEN
                logging.getLogger(__name__).warning(
                    f"Circuit breaker '{self.name}' OPEN (recovery failed)"
                )
            elif self.failure_count >= self.failure_threshold:
                self.state = self.OPEN
                logging.getLogger(__name__).warning(
                    f"Circuit breaker '{self.name}' OPEN (threshold reached: {self.failure_count})"
                )
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        if not self._should_allow_request():
            raise CircuitBreakerOpenError(
                f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
            )
        
        try:
            result = await func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise
    
    def call_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Execute sync function with circuit breaker protection"""
        if not self._should_allow_request():
            raise CircuitBreakerOpenError(
                f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
            )
        
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }
    
    @classmethod
    def get_all_status(cls) -> Dict[str, Dict]:
        """Get status of all circuit breakers"""
        return {name: breaker.get_status() for name, breaker in cls._breakers.items()}


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# ============================================================
# GRACEFUL SHUTDOWN
# ============================================================

class GracefulShutdown:
    """Handle graceful shutdown for clean connection closing"""
    
    _instance = None
    _callbacks: list = []
    _is_shutting_down: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, callback: Callable):
        """Register a cleanup callback"""
        cls._callbacks.append(callback)
    
    @classmethod
    def is_shutting_down(cls) -> bool:
        return cls._is_shutting_down
    
    @classmethod
    async def shutdown(cls, signal_name: str = "UNKNOWN"):
        """Execute graceful shutdown"""
        if cls._is_shutting_down:
            return
        
        cls._is_shutting_down = True
        logger = logging.getLogger(__name__)
        logger.info(f"Received {signal_name}, starting graceful shutdown...")
        
        for callback in cls._callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Shutdown callback error: {e}")
        
        logger.info("Graceful shutdown complete")


def setup_graceful_shutdown(loop: asyncio.AbstractEventLoop = None):
    """Setup signal handlers for graceful shutdown"""
    loop = loop or asyncio.get_event_loop()
    
    def handle_signal(sig):
        asyncio.create_task(GracefulShutdown.shutdown(sig.name))
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            signal.signal(sig, lambda s, f, sig=sig: handle_signal(sig))


# ============================================================
# HEALTH CHECK HELPERS
# ============================================================

async def check_gemini_health() -> Dict[str, Any]:
    """Check Gemini API health"""
    try:
        from gemini_handler import gemini
        status = gemini.get_status()
        return {
            "status": "healthy" if status.get("initialized") else "degraded",
            "api_keys_available": status.get("api_keys_available", 0),
            "models_available": status.get("models_available", []),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_sheets_health() -> Dict[str, Any]:
    """Check Google Sheets health"""
    try:
        from smart_sheets import SmartMRSheetsManager
        manager = SmartMRSheetsManager()
        # Just check if we can access sheet names
        if hasattr(manager, 'sheet') and manager.sheet:
            return {"status": "healthy"}
        return {"status": "degraded", "message": "Sheets not fully initialized"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def get_full_health_status() -> Dict[str, Any]:
    """Get comprehensive health status"""
    import platform
    
    gemini_health = await check_gemini_health()
    sheets_health = await check_sheets_health()
    circuit_breakers = CircuitBreaker.get_all_status()
    
    # Determine overall status
    statuses = [gemini_health.get("status"), sheets_health.get("status")]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        overall = "unhealthy"
    else:
        overall = "degraded"
    
    return {
        "status": overall,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": os.getenv("APP_VERSION", "2.1.0"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "components": {
            "gemini": gemini_health,
            "google_sheets": sheets_health,
        },
        "circuit_breakers": circuit_breakers,
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.system(),
        }
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    # Logging
    "setup_production_logging",
    "JSONFormatter",
    
    # Sentry
    "init_sentry",
    "capture_exception",
    
    # Request tracing
    "RequestContext",
    "with_correlation_id",
    
    # Circuit breaker
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    
    # Graceful shutdown
    "GracefulShutdown",
    "setup_graceful_shutdown",
    
    # Health checks
    "check_gemini_health",
    "check_sheets_health",
    "get_full_health_status",
]
