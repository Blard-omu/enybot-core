"""
Global logger configuration for AI Student Support Service.
Provides consistent logging with colored output and service prefixing.
"""
import logging
import sys
from typing import Optional
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for different log levels."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        # Add service prefix if not already present
        if not hasattr(record, 'service_prefix'):
            record.service_prefix = 'ai-service'
        
        # Format the message with colors
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        
        # Format the service prefix
        record.service_prefix = f"{Fore.BLUE}[{record.service_prefix}]{Style.RESET_ALL}"
        
        return super().format(record)

def setup_logger(
    name: str,
    level: int = logging.INFO,
    service_prefix: str = "ai-service",
    log_to_file: bool = False,
    log_file_path: Optional[str] = None
) -> logging.Logger:
    """
    Setup and configure a logger with consistent formatting and colored output.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level
        service_prefix: Service identifier prefix
        log_to_file: Whether to also log to file
        log_file_path: Path to log file if log_to_file is True
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = ColoredFormatter(
        fmt='%(asctime)s %(service_prefix)s %(levelname)s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file and log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(level)
        
        # File formatter without colors
        file_formatter = logging.Formatter(
            fmt='%(asctime)s [%(service_prefix)s] %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Add service prefix to log records
    logger = logging.LoggerAdapter(logger, {'service_prefix': service_prefix})
    
    return logger

def get_logger(
    name: str,
    service_prefix: str = "ai-service"
) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        service_prefix: Service identifier prefix
    
    Returns:
        Configured logger instance
    """
    return setup_logger(name, service_prefix=service_prefix)

# Global logger instance for the main application
app_logger = get_logger("ai-student-support-svc")
