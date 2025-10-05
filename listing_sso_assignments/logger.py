from aws_lambda_powertools import Logger, Tracer

# Module-level variables to hold singleton instances of Logger and Tracer
_logger = None
_tracer = None


def get_logger():
    """
    Get or create a singleton instance of the AWS Lambda Powertools Logger.

    This function initializes and returns a singleton instance of the Logger
    class from the AWS Lambda Powertools library. The Logger provides structured
    logging capabilities and is configured based on environment variables
    such as `POWERTOOLS_SERVICE_NAME`.

    Returns:
        Logger: A singleton instance of the Logger class.

    Example:
        >>> logger = get_logger()
        >>> logger.info("This is a log message.")
    """
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger


def get_tracer():
    """
    Get or create a singleton instance of the AWS Lambda Powertools Tracer.

    This function initializes and returns a singleton instance of the Tracer
    class from the AWS Lambda Powertools library. The Tracer is used for
    distributed tracing in AWS Lambda functions, enabling you to trace requests
    and record performance metrics.

    Returns:
        Tracer: A singleton instance of the Tracer class.

    Example:
        >>> tracer = get_tracer()
        >>> @tracer.capture_method
        ... def my_method():
        ...     # your code here
        ...     pass
    """
    global _tracer
    if _tracer is None:
        _tracer = Tracer()
    return _tracer
